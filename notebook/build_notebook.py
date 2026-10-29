"""Builds Flight_Trajectory_Analysis.ipynb (self-contained: embeds project scripts via %%writefile)."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cells = []


def md(s): cells.append({"cell_type": "markdown", "metadata": {}, "source": s.strip()})


def code(s): cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.strip()})


def embed(rel):
    with open(os.path.join(ROOT, rel)) as fh:
        code(f"%%writefile {os.path.basename(rel)}\n" + fh.read())


md("""
# ✈️ Flight Trajectory Analysis — Spatio-Temporal Big Data Analytics
**BDSMA Micro Project · SDG 9: Industry, Innovation & Infrastructure**

**Problem:** Indian airspace handles 4,000+ daily flights. Congested terminal areas, airway detours and
holding patterns waste fuel, add CO₂ and delay passengers. We use big-data tools on ADS-B
*state vectors* (OpenSky Network schema) to find **where & when** airspace is congested, **which routes are
inefficient**, and **which airports are structural hubs** — insights for air-navigation infrastructure planning.

| Stage | Syllabus concept | Tool |
|---|---|---|
| 1 | HDFS storage & file ops | Hadoop 3.3.6 (pseudo-distributed) |
| 2 | MapReduce: spatio-temporal grid aggregation, trajectory reconstruction | Hadoop Streaming (Python) |
| 3 | Distributed processing, window functions | Apache Spark (PySpark) |
| 4 | NoSQL document store + geospatial index | MongoDB (`2dsphere`) |
| 5 | Community detection / structural analytics | Louvain, PageRank, Betweenness |
| 6 | Visualisation | Folium + web dashboard |

> Runtime → *Run all*. Takes ~6–8 min (mostly Hadoop download).
""")

md("## 0. Setup — Java + Hadoop (single-node HDFS)")
code("""
!apt-get -qq install -y openjdk-11-jdk-headless > /dev/null
!wget -q https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
!tar -xzf hadoop-3.3.6.tar.gz && mv hadoop-3.3.6 /usr/local/hadoop
!pip -q install pyspark pymongo folium networkx
""")
code("""
import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
os.environ["HADOOP_HOME"] = "/usr/local/hadoop"
os.environ["PATH"] += ":/usr/local/hadoop/bin:/usr/local/hadoop/sbin"
for r in ["HDFS_NAMENODE_USER", "HDFS_DATANODE_USER", "HDFS_SECONDARYNAMENODE_USER"]:
    os.environ[r] = "root"

core = '''<configuration>
 <property><name>fs.defaultFS</name><value>hdfs://localhost:9000</value></property>
</configuration>'''
hdfs = '''<configuration>
 <property><name>dfs.replication</name><value>1</value></property>
 <property><name>dfs.permissions.enabled</name><value>false</value></property>
 <property><name>dfs.namenode.name.dir</name><value>/tmp/hdfs/nn</value></property>
 <property><name>dfs.datanode.data.dir</name><value>/tmp/hdfs/dn</value></property>
</configuration>'''
open("/usr/local/hadoop/etc/hadoop/core-site.xml", "w").write(core)
open("/usr/local/hadoop/etc/hadoop/hdfs-site.xml", "w").write(hdfs)
!echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> /usr/local/hadoop/etc/hadoop/hadoop-env.sh
""")
code("""
!hdfs namenode -format -force -nonInteractive 2>&1 | tail -1
!hdfs --daemon start namenode && hdfs --daemon start datanode
!sleep 8 && jps && hdfs dfsadmin -report | head -12
""")

md("""
## 1. Dataset
**Primary:** [OpenSky Network historical state vectors](https://opensky-network.org/datasets/states) — real ADS-B
data, one CSV per hour, ~1 GB/day of global traffic. We download one hour and keep the Indian FIR bounding box
(lat 6–37°N, lon 68–98°E).

**Labelled sample:** OpenSky vectors carry no origin/destination, so for route-efficiency & network analysis we also
generate a reproducible 24-hour dataset in the *same schema* for 20 major Indian airports (gravity traffic model,
IST peak hours, airway dog-legs, holding stacks at DEL/BOM).
""")
embed("data/generate_dataset.py")
code("""
!python generate_dataset.py
import pandas as pd, subprocess
COLS = ["time","icao24","lat","lon","velocity","heading","vertrate","callsign","onground",
        "baroaltitude","geoaltitude","origin","destination"]
try:  # REAL OpenSky hour (2022-06-27 06:00 UTC = Indian morning peak)
    url = "https://s3.opensky-network.org/data-samples/states/2022-06-27/06/states_2022-06-27-06.csv.tar"
    subprocess.run(f"wget -q -O os.tar {url} && tar -xf os.tar", shell=True, check=True)
    raw = pd.read_csv("states_2022-06-27-06.csv.gz")
    india = raw[raw.lat.between(6, 37) & raw.lon.between(68, 98)].dropna(subset=["lat", "lon"])
    india = india.assign(origin="", destination="")[COLS]
    india.to_csv("opensky_india.csv", index=False)
    print("Real OpenSky India rows:", len(india), "| aircraft:", india.icao24.nunique())
except Exception as e:
    print("OpenSky download unavailable (", e, ") -> using labelled sample only")
    pd.read_csv("flights_states.csv").to_csv("opensky_india.csv", index=False)
pd.read_csv("flights_states.csv").head()
""")

md("## 2. HDFS operations (Experiment 1)")
code("""
!hdfs dfs -mkdir -p /flights/raw /flights/archive
!hdfs dfs -put -f flights_states.csv /flights/raw/          # copy local -> HDFS
!hdfs dfs -put -f opensky_india.csv /flights/raw/
!hdfs dfs -ls -h /flights/raw                                # list
!hdfs dfs -cat /flights/raw/flights_states.csv | head -5     # display
!hdfs dfs -du -h /flights                                    # disk usage
!hdfs dfs -cp /flights/raw/opensky_india.csv /flights/archive/   # copy inside HDFS
!hdfs dfs -mv /flights/archive/opensky_india.csv /flights/archive/opensky_backup.csv  # move/rename
!hdfs dfs -get -f /flights/archive/opensky_backup.csv ./from_hdfs.csv   # HDFS -> local
!hdfs dfs -rm /flights/archive/opensky_backup.csv            # delete
!hdfs fsck /flights/raw/flights_states.csv -files -blocks | grep -E "blocks|Status"
""")

md("""
## 3. MapReduce with Hadoop Streaming (Experiment 3)
**Job 1 — Spatio-temporal density grid.** Map: each ADS-B point → key `(lat_cell, lon_cell, hour, altitude_band)`.
Reduce: sum. This is a *spatio-temporal histogram* — the basis for hotspot detection.

**Job 2 — Trajectory reconstruction.** Map: group by `icao24|callsign`. Reduce: sort points by time, compute flown
distance vs great-circle distance → **route inefficiency %**.
""")
for f in ["hadoop/mapper_grid.py", "hadoop/reducer_sum.py", "hadoop/mapper_route.py", "hadoop/reducer_route.py"]:
    embed(f)
code("""
STREAM = "/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar"
!hdfs dfs -rm -r -f /flights/out_grid /flights/out_route
!hadoop jar {STREAM} -files mapper_grid.py,reducer_sum.py -mapper "python3 mapper_grid.py" \\
   -reducer "python3 reducer_sum.py" -input /flights/raw/flights_states.csv -output /flights/out_grid 2>&1 | tail -3
!hadoop jar {STREAM} -files mapper_route.py,reducer_route.py -mapper "python3 mapper_route.py" \\
   -reducer "python3 reducer_route.py" -input /flights/raw/flights_states.csv -output /flights/out_route 2>&1 | tail -3
""")
code("""
print("Top spatio-temporal cells (lat_cell, lon_cell, hour_UTC, band -> count)")
!hdfs dfs -cat /flights/out_grid/part-* | sort -t$'\\t' -k2 -nr | head -10
print("\\nLeast efficient flights (flight -> origin,dest,flown_km,gc_km,ineff%,dur,max_alt)")
!hdfs dfs -cat /flights/out_route/part-* | sort -t, -k5 -nr | head -10
""")

md("## 4. Distributed processing with Spark (reads directly from HDFS)")
code("""
from pyspark.sql import SparkSession, functions as F, Window
spark = SparkSession.builder.appName("FlightTrajectory").getOrCreate()
sdf = spark.read.csv("hdfs://localhost:9000/flights/raw/flights_states.csv", header=True, inferSchema=True)
sdf = sdf.withColumn("hour_ist", ((F.col("time") % 86400) / 3600 + 5.5).cast("int") % 24)
print("partitions:", sdf.rdd.getNumPartitions(), "rows:", sdf.count())
sdf.createOrReplaceTempView("sv")
spark.sql('''SELECT hour_ist, COUNT(DISTINCT icao24) AS active_aircraft, COUNT(*) AS points
             FROM sv GROUP BY hour_ist ORDER BY hour_ist''').show(24)
""")
code("""
# Window functions: per-flight point-to-point turn rate & climb phase segmentation
w = Window.partitionBy("icao24").orderBy("time")
seg = (sdf.withColumn("dh", (F.col("heading") - F.lag("heading").over(w) + 540) % 360 - 180)
          .withColumn("phase", F.when(F.col("baroaltitude") < 30, "Ground")
                                .when(F.col("vertrate") > 1, "Climb")
                                .when(F.col("vertrate") < -1, "Descent").otherwise("Cruise")))
seg.groupBy("phase").count().show()
# holding detection: >= 540 deg net turn below 3000 m
holds = (seg.filter("baroaltitude < 3000").groupBy("icao24", "destination")
            .agg(F.abs(F.sum("dh")).alias("net_turn")).filter("net_turn >= 540"))
holds.groupBy("destination").count().orderBy(F.desc("count")).show()
""")
code("""
# Hotspots: 0.5 deg grid, airborne only
spark.sql('''SELECT FLOOR(lat/0.5)*0.5+0.25 AS clat, FLOOR(lon/0.5)*0.5+0.25 AS clon, COUNT(*) AS n
             FROM sv WHERE baroaltitude > 30 GROUP BY 1,2 ORDER BY n DESC LIMIT 10''').show()
""")

md("## 5. NoSQL — MongoDB document store with geospatial index (Experiment 2)")
code("""
!wget -q https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2204-7.0.14.tgz
!tar -xzf mongodb-linux-x86_64-ubuntu2204-7.0.14.tgz && mkdir -p /data/db
!mongodb-linux-x86_64-ubuntu2204-7.0.14/bin/mongod --dbpath /data/db --fork --logpath /tmp/mongod.log
""")
code("""
from pymongo import MongoClient, GEOSPHERE
db = MongoClient("mongodb://localhost:27017").airspace
db.trajectories.drop()
df = pd.read_csv("flights_states.csv")
docs = []
for icao, g in df.sort_values("time").groupby("icao24"):
    docs.append({"_id": icao, "callsign": g.callsign.iloc[0], "origin": g.origin.iloc[0],
                 "destination": g.destination.iloc[0], "start": int(g.time.min()), "end": int(g.time.max()),
                 "max_alt": float(g.baroaltitude.max()),
                 "path": {"type": "LineString", "coordinates": g[["lon", "lat"]].values.tolist()}})
db.trajectories.insert_many(docs)
db.trajectories.create_index([("path", GEOSPHERE)])
db.trajectories.create_index([("origin", 1), ("destination", 1)])
print(db.trajectories.count_documents({}), "trajectory documents")
""")
code("""
# Spatial query: which flights passed within 50 km of Nagpur (central-India airway crossroads)?
q = {"path": {"$near": {"$geometry": {"type": "Point", "coordinates": [79.0472, 21.0922]}, "$maxDistance": 50000}}}
print("Flights within 50 km of NAG:", len(list(db.trajectories.find(q, {"_id": 1}))))
# Spatio-temporal: flights intersecting Mumbai TMA polygon during evening peak (17-21 IST)
tma = {"type": "Polygon", "coordinates": [[[72.4,18.7],[73.4,18.7],[73.4,19.5],[72.4,19.5],[72.4,18.7]]]}
base = 1719446400
print("Mumbai TMA, 17-21 IST:", db.trajectories.count_documents(
    {"path": {"$geoIntersects": {"$geometry": tma}}, "start": {"$lt": base + 15.5*3600}, "end": {"$gt": base + 11.5*3600}}))
# Aggregation pipeline: busiest routes
for r in db.trajectories.aggregate([{"$group": {"_id": {"o": "$origin", "d": "$destination"}, "n": {"$sum": 1}}},
                                    {"$sort": {"n": -1}}, {"$limit": 5}]): print(r)
""")

md("## 6. Structural analytics — airport network, Louvain communities (Experiments 6 & 7)")
code("""
import networkx as nx
G = nx.Graph()
for (o, d), n in df.groupby(["origin", "destination"]).icao24.nunique().items():
    G.add_edge(o, d, weight=G.get_edge_data(o, d, {"weight": 0})["weight"] + n)
comms = nx.community.louvain_communities(G, weight="weight", seed=7)
print("Modularity:", round(nx.community.modularity(G, comms, weight="weight"), 3))
for i, c in enumerate(comms): print(f"Community {i}: {sorted(c)}")
pr, bt = nx.pagerank(G, weight="weight"), nx.betweenness_centrality(G)
print(pd.DataFrame({"pagerank": pr, "betweenness": bt}).sort_values("pagerank", ascending=False).head(8))
""")

md("## 7. Visualisation")
code("""
import folium
from folium.plugins import HeatMap
m = folium.Map(location=[22, 80], zoom_start=5, tiles="CartoDB dark_matter")
HeatMap(df[df.baroaltitude > 30][["lat", "lon"]].sample(15000).values.tolist(), radius=6, blur=8).add_to(m)
for icao, g in list(df.groupby("icao24"))[:80]:
    folium.PolyLine(g[["lat", "lon"]].values.tolist(), weight=1, color="#4cc9f0", opacity=.5).add_to(m)
m
""")

md("""
## 8. Insights → SDG 9
* **Congestion hotspots** cluster around DEL & BOM terminal areas during IST 06–10 and 17–21 peaks → case for
  additional runway capacity / parallel approach procedures.
* **Holding patterns** at DEL/BOM waste fuel; spatio-temporal detection lets ANSPs quantify delay cost.
* **Route inefficiency** (flown vs great-circle) quantifies the benefit of *Free Route Airspace* / GAGAN-enabled
  direct routings → lower fuel burn and CO₂ (SDG 9 + SDG 13).
* **Louvain communities** reveal regional sub-networks (North/West/South/East) and **PageRank/Betweenness**
  identify hubs where infrastructure investment has the largest network effect.

Run `analytics/pipeline.py` to regenerate `web/data/dashboard.json` for the interactive dashboard.
""")
code("""
!hdfs --daemon stop datanode && hdfs --daemon stop namenode
""")

nb = {"cells": cells, "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"},
                                   "colab": {"provenance": []}}, "nbformat": 4, "nbformat_minor": 0}
out = os.path.join(ROOT, "notebook", "Flight_Trajectory_Analysis.ipynb")
json.dump(nb, open(out, "w"), indent=1)
print("wrote", out)
