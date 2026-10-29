"""Builds docs/SkyTrace_Project_Guide.pdf - full project explanation + slide-by-slide speaking script."""
import json, os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
                                KeepTogether, Preformatted)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ppt"))
from content import SLIDES

D = json.load(open(os.path.join(ROOT, "web", "data", "dashboard.json")))
K = D["kpis"]
ACC, DARK, MUT = colors.HexColor("#0b7fab"), colors.HexColor("#0a0f1c"), colors.HexColor("#555f73")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=DARK, fontSize=20, spaceBefore=6, spaceAfter=10)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=ACC, fontSize=14, spaceBefore=12, spaceAfter=6)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], textColor=DARK, fontSize=11.5, spaceBefore=8, spaceAfter=4)
P = ParagraphStyle("P", parent=ss["BodyText"], fontSize=10.5, leading=15.5, spaceAfter=6)
BUL = ParagraphStyle("B", parent=P, leftIndent=14, bulletIndent=4, spaceAfter=3)
NOTE = ParagraphStyle("N", parent=P, backColor=colors.HexColor("#eef6fb"), borderColor=ACC, borderWidth=0.6,
                      borderPadding=8, spaceBefore=14, spaceAfter=14)
SAY = ParagraphStyle("S", parent=P, backColor=colors.HexColor("#fff8e6"), borderColor=colors.HexColor("#e0a800"),
                     borderWidth=0.6, borderPadding=8, spaceBefore=16, spaceAfter=16, fontName="Helvetica-Oblique")
CODE = ParagraphStyle("C", fontName="Courier", fontSize=8.8, leading=11.5, backColor=colors.HexColor("#f2f4f8"),
                      borderPadding=6, spaceAfter=10)

story = []
h1 = lambda t: story.append(Paragraph(t, H1))
h2 = lambda t: story.append(Paragraph(t, H2))
h3 = lambda t: story.append(Paragraph(t, H3))
p = lambda t: story.append(Paragraph(t, P))
note = lambda t: story.append(Paragraph(t, NOTE))
code = lambda t: story.append(Preformatted(t, CODE))


def bullets(items):
    for i in items:
        story.append(Paragraph(i, BUL, bulletText="•"))


def table(rows, widths, head=True):
    t = Table(rows, colWidths=widths, repeatRows=1 if head else 0)
    st = [("FONT", (0, 0), (-1, -1), "Helvetica", 9.3), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d2e0")),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fb")]),
          ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]
    if head:
        st += [("BACKGROUND", (0, 0), (-1, 0), DARK), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
               ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9.3)]
    t.setStyle(TableStyle(st))
    story.append(t); story.append(Spacer(1, 10))


def wrap(rows):
    return [[Paragraph(str(c), ParagraphStyle("t", parent=P, fontSize=9.2, leading=12, spaceAfter=0,
                                              textColor=colors.white if i == 0 else colors.black,
                                              fontName="Helvetica-Bold" if i == 0 else "Helvetica"))
             for c in r] for i, r in enumerate(rows)]


# ---------------- Cover ----------------
story += [Spacer(1, 3 * cm), Paragraph("<font size=40 color='#0a0f1c'><b>Sky</b></font><font size=40 color='#0b7fab'><b>Trace</b></font>", P),
          Spacer(1, 1.2 * cm),
          Paragraph("<font size=18>Flight Trajectory Analysis using Spatio-Temporal Big Data Analytics</font>", P), Spacer(1, .5 * cm),
          Paragraph("<font size=12 color='#555f73'>BDSMA Micro Project · B.E. Computer Engineering · Semester VII<br/>"
                    "SDG 9: Industry, Innovation &amp; Infrastructure</font>", P), Spacer(1, 1 * cm),
          Image(os.path.join(ROOT, "ppt", "map.png"), width=12 * cm, height=12 * cm * 0.74), Spacer(1, 1 * cm),
          Paragraph("<font color='#555f73'>Complete project guide: what we built, how every part works, how to run it, "
                    "and exactly what to say on each slide.</font>", P), PageBreak()]

# ---------------- Contents ----------------
h1("Contents")
bullets(["1. The project in one minute", "2. The problem, with real examples", "3. Why this is SDG 9",
         "4. The dataset", "5. The architecture: how data flows", "6. Every technology explained simply, and what we did with it",
         "7. Formulas and logic used", "8. Results", "9. The dashboard: what each tab shows", "10. Use cases and benefits",
         "11. How to run the project (college PC and Google Colab)", "12. Folder structure: what each file does",
         "13. Slide-by-slide presentation script", "14. Viva questions and simple answers", "15. Limitations and future scope"])
story.append(PageBreak())

# ---------------- 1 ----------------
h1("1. The project in one minute")
p("Every passenger aeroplane carries a device called <b>ADS-B</b> (Automatic Dependent Surveillance–Broadcast). "
  "Every second it broadcasts the plane's <b>position (latitude, longitude)</b>, <b>height</b>, <b>speed</b> and <b>direction</b>. "
  "Anyone with a cheap receiver can pick these signals up, and websites like OpenSky Network collect them from all over the world.")
p("If we join one plane's points in time order, we get its <b>trajectory</b>: the actual path it flew. "
  "<b>SkyTrace</b> collects lakhs of these points, stores them in <b>Hadoop</b>, processes them with <b>MapReduce</b> and <b>Spark</b>, "
  "saves the flight paths in <b>MongoDB</b>, and analyses the airport network with <b>graph algorithms</b> (Louvain, PageRank). "
  "The results appear on an interactive <b>web dashboard</b>.")
note("<b>One-line explanation for anyone:</b> SkyTrace is like Google Maps traffic, but for the sky. It shows where and "
     "when Indian airspace is crowded, which flights waste distance and fuel, and which airports are the most important.")
p("<b>Spatio-temporal</b> means we always look at two things together: <b>space</b> (where on the map) and <b>time</b> (what hour). "
  "Example question: <i>How many planes were in the box around Mumbai between 7 and 8 pm?</i>")

# ---------------- 2 ----------------
h1("2. The problem, with real examples")
bullets([
    "<b>Crowded airports at rush hour.</b> Delhi and Mumbai are among the busiest airports in the world. Most flights "
    "want to depart or land at the same convenient times, early morning and evening.",
    "<b>Holding (planes circling).</b> When the runway is full, air traffic control tells arriving planes to fly in an "
    "oval racetrack pattern and wait their turn. Mumbai has crossing runways that cannot be used at the same time, so "
    "evening holding there is common. Delhi in winter fog has the same problem.",
    "<b>Bent routes.</b> Planes follow fixed air routes (airways) and military restricted areas, not straight lines. "
    "So a flight often covers more kilometres than the straight-line distance.",
    "<b>Cost.</b> An A320 burns about 2.4 kg of fuel per km in cruise and roughly 35–40 kg per minute in a holding "
    "pattern. 15 minutes of holding ≈ 500–600 kg of fuel, and every 1 kg of jet fuel produces about 3.16 kg of CO₂.",
])
note("<b>Real-world proof that this matters:</b> India built new airports at <b>Navi Mumbai</b> and <b>Noida (Jewar)</b> because "
     "Mumbai and Delhi ran out of runway capacity. Decisions like these need exactly the kind of data SkyTrace produces: "
     "where and when the airspace is full.")

# ---------------- 3 ----------------
h1("3. Why this is SDG 9")
p("UN Sustainable Development Goal 9 is <b>Industry, Innovation and Infrastructure</b>. Target <b>9.1</b> asks for "
  "<i>quality, reliable, sustainable and resilient infrastructure</i>. Airports and the airspace above India are national "
  "infrastructure, just like highways and railways.")
bullets(["<b>Infrastructure:</b> we find which airports and which hours are overloaded. That tells planners where to add a runway, a parallel taxiway or a better approach procedure.",
         "<b>Innovation:</b> we use modern big data tools (Hadoop, Spark, NoSQL, graph analytics) on open data.",
         "<b>Sustainability:</b> shorter routes and less holding mean less fuel and less CO₂, which also supports SDG 13 (Climate Action)."])

# ---------------- 4 ----------------
h1("4. The dataset")
h3("Source 1: OpenSky Network (real data)")
p("OpenSky Network (opensky-network.org) is a non-profit project run by universities. It publishes free historical ADS-B "
  "data as one CSV file per hour. Our Colab notebook downloads the hour <b>27 June 2022, 06:00 UTC</b> (11:30 am in India) "
  "and keeps only the points inside India's box (latitude 6°–37° N, longitude 68°–98° E).")
h3("Source 2: Labelled sample day (same format)")
p("Real OpenSky rows do <b>not</b> say where a flight came from or where it is going. Route analysis needs that, so we "
  "wrote <font face=Courier>data/generate_dataset.py</font>. It creates one full 24-hour day in exactly the same column "
  f"format for <b>20 major Indian airports</b>: <b>{K['flights']} flights</b> and <b>{K['state_vectors']:,} position rows</b>. "
  "It copies real-world patterns:")
bullets(["<b>Gravity model:</b> bigger airports get more flights, and nearby airports are connected more often (traffic ∝ size ÷ distance<super>1.3</super>).",
         "<b>Rush hours:</b> more departures 6–10 am and 5–9 pm IST.",
         "<b>Bent routes:</b> about 35% of flights take a dog-leg (a bend in the route) instead of the straight line.",
         "<b>Holding:</b> about 25% of flights arriving at Delhi and Mumbai circle before landing.",
         "<b>Realistic flight profile:</b> climb, cruise at standard flight levels, descend; one point per minute; small GPS noise."])
note("<b>Be honest in the viva:</b> the route-efficiency and network numbers come from the sample day. The Hadoop, Spark "
     "and MongoDB code is written for the real OpenSky format and runs on the real hour too.")
h3("What one row looks like")
table(wrap([["Column", "Meaning", "Example"],
            ["time", "Unix timestamp (seconds since 1970)", "1719469800"],
            ["icao24", "Unique ID of the aircraft's transponder", "8056b8"],
            ["lat, lon", "Position in degrees", "19.21, 72.95"],
            ["velocity", "Ground speed in metres/second", "231.4"],
            ["heading", "Direction in degrees (0 = North, 90 = East)", "184.0"],
            ["vertrate", "Climb (+) or descent (−) rate in m/s", "-6.2"],
            ["callsign", "Flight number used on radio", "AIC7713"],
            ["baroaltitude", "Height in metres", "10050"],
            ["origin, destination", "Airport codes (sample day only)", "PNQ, BOM"]]), [3.2 * cm, 8.3 * cm, 4.5 * cm])
story.append(PageBreak())

# ---------------- 5 ----------------
h1("5. The architecture: how data flows")
table(wrap([["Step", "Tool", "What happens", "Syllabus"],
            ["1. Collect", "OpenSky ADS-B", "Download raw plane positions", "-"],
            ["2. Store", "Hadoop HDFS", "Upload the big CSV; HDFS splits it into blocks across machines", "Exp 1"],
            ["3. Batch process", "MapReduce (Hadoop Streaming, Python)", "Job 1: count planes per map box per hour. Job 2: rebuild each flight and measure extra distance", "Exp 3"],
            ["4. Fast processing", "Apache Spark", "SQL queries, flight phases, holding detection, hotspots", "Big data processing"],
            ["5. Store paths", "MongoDB (NoSQL)", "Each flight saved as a GeoJSON line with a geo index for location searches", "Exp 2"],
            ["6. Network analysis", "NetworkX: Louvain, PageRank, Betweenness", "Find airport groups and hub airports", "Exp 6, 7"],
            ["7. Show", "HTML + Leaflet + Chart.js", "Interactive dashboard with maps and charts", "-"]]),
      [2.6 * cm, 3.6 * cm, 7.2 * cm, 2.6 * cm])

# ---------------- 6 ----------------
h1("6. Every technology explained simply")
h2("6.1 Hadoop HDFS (Experiment 1)")
p("<b>What it is:</b> HDFS (Hadoop Distributed File System) stores very large files by cutting them into blocks "
  "(128 MB each by default) and spreading the blocks over many computers. Each block can be copied (replicated) so "
  "data survives if one computer fails.")
p("<b>Simple example:</b> one big book torn into chapters, with each chapter kept in a different cupboard plus a photocopy somewhere else.")
p("<b>Why we use it:</b> one day of global OpenSky data is about 1 GB, and a year is hundreds of GB. A normal laptop folder cannot store and process that efficiently.")
p("<b>What we did:</b> in Colab we installed Hadoop 3.3.6 in pseudo-distributed mode (NameNode and DataNode on one machine) and ran:")
code("hdfs dfs -mkdir -p /flights/raw /flights/archive      # make folders\n"
     "hdfs dfs -put flights_states.csv /flights/raw/          # upload local -> HDFS\n"
     "hdfs dfs -ls -h /flights/raw                            # list files\n"
     "hdfs dfs -cat /flights/raw/flights_states.csv | head    # view\n"
     "hdfs dfs -du -h /flights                                # size used\n"
     "hdfs dfs -cp ... /flights/archive/                      # copy inside HDFS\n"
     "hdfs dfs -mv ... opensky_backup.csv                     # move / rename\n"
     "hdfs dfs -get /flights/archive/... ./from_hdfs.csv      # HDFS -> local\n"
     "hdfs dfs -rm /flights/archive/opensky_backup.csv        # delete\n"
     "hdfs fsck /flights/raw/flights_states.csv -files -blocks  # see blocks")

h2("6.2 MapReduce (Experiment 3)")
p("<b>What it is:</b> a way to process huge data in parallel in two steps. <b>Map</b>: every machine reads its part and "
  "emits (key, value) pairs. <b>Shuffle/Sort</b>: Hadoop groups all pairs with the same key. <b>Reduce</b>: combine each group into an answer.")
p("<b>Simple example:</b> election counting. Every booth counts its own votes (Map), votes are grouped by candidate "
  "(Shuffle), and the totals are added up (Reduce).")
p("We wrote the jobs in Python and ran them with <b>Hadoop Streaming</b>, which lets any language read from stdin and write to stdout.")
h3("Job 1: spatio-temporal density grid (hadoop/mapper_grid.py + reducer_sum.py)")
bullets(["<b>Map:</b> for each row, find the 0.5° map box (about 55 km × 55 km), the hour, and the height band (GND / LOW &lt;3 km / MID 3–8 km / HIGH &gt;8 km). Emit <font face=Courier>box_lat,box_lon,hour,band → 1</font>.",
         "<b>Reduce:</b> add up the 1s for each key, which gives the number of plane reports in that box at that hour and height.",
         "<b>Use:</b> boxes with the biggest counts are <b>congestion hotspots</b>."])
h3("Job 2: trajectory reconstruction (hadoop/mapper_route.py + reducer_route.py)")
bullets(["<b>Map:</b> emit <font face=Courier>icao24|callsign → time,lat,lon,alt,origin,destination</font>, so all points of one flight reach the same reducer.",
         "<b>Reduce:</b> sort that flight's points by time, add up the distance between consecutive points (flown distance), compare it with the straight great-circle distance, and output the extra %, duration and maximum height.",
         "<b>Use:</b> finds the most inefficient flights and routes."])
code("Real output of Job 2\n# flight -> from,to,flown_km,straight_km,extra%,minutes,max_height\n"
     "8056b8|AIC7713   PNQ,BOM,349.8,123.9,182.40,43,7600\n"
     "# Pune->Mumbai flew ~350 km for a 124 km trip\n# because it circled (held) near Mumbai")

h2("6.3 Apache Spark")
p("<b>What it is:</b> a faster successor to MapReduce. It keeps data in <b>memory (RAM)</b> instead of writing to disk "
  "after every step, and lets us write <b>SQL</b>. It reads directly from HDFS.")
p("<b>Simple example:</b> MapReduce is like writing every rough calculation in a notebook and reading it back; Spark keeps the numbers in your head.")
p("<b>What we did:</b>")
bullets(["Counted active aircraft per hour with Spark SQL (<font face=Courier>COUNT(DISTINCT icao24) GROUP BY hour</font>).",
         "<b>Window functions</b> (<font face=Courier>LAG() OVER (PARTITION BY icao24 ORDER BY time)</font>) compare each point with the plane's previous point to get the turn angle.",
         "<b>Flight phase:</b> vertical rate &gt; +1 m/s = Climb, &lt; −1 = Descent, else Cruise; height &lt; 30 m = Ground.",
         "<b>Holding detection:</b> below 3 km, if the plane's total turning adds up to ≥ 540° (one and a half full circles), it was holding.",
         "<b>Hotspots:</b> group airborne points into 0.5° boxes and take the top 10."])

h2("6.4 MongoDB, a NoSQL document store (Experiment 2)")
p("<b>What it is:</b> a NoSQL database that stores flexible JSON-like <b>documents</b> instead of fixed tables. "
  "It has built-in support for <b>geographic data</b>.")
p("<b>Why NoSQL here:</b> one flight path is a list of hundreds of points. In SQL that becomes hundreds of rows; in MongoDB it is one document. A "
  "<b>2dsphere index</b> lets us search by location quickly.")
code('{ "_id": "8056b8", "callsign": "AIC7713", "origin": "PNQ", "destination": "BOM",\n'
     '  "start": 1719469800, "end": 1719472380, "max_alt": 7600,\n'
     '  "path": { "type": "LineString", "coordinates": [[73.92,18.58], [73.80,18.66], ...] } }')
bullets(["<b>$near:</b> flights passing within 50 km of Nagpur (central India's airway crossroads).",
         "<b>$geoIntersects + time filter:</b> flights entering the Mumbai area polygon during the 5–9 pm rush. This is a true spatio-temporal query.",
         "<b>Aggregation pipeline:</b> the busiest routes ($group + $sort)."])

h2("6.5 Graph analytics: Louvain, PageRank, Betweenness (Experiments 6 and 7)")
p("We build a graph where each <b>airport is a node</b> and each <b>route is an edge</b>, weighted by the number of flights. "
  "This is the same kind of analysis used on social networks.")
bullets([f"<b>Louvain community detection:</b> groups nodes so there are many links inside a group and few between groups. It found <b>{K['communities']} communities</b>: North (DEL, JAI, LKO, IXC, SXR, NAG), West (BOM, PNQ, AMD), South (BLR, MAA, HYD, COK, GOI, TRV) and East (CCU, GAU, PAT, BBI, IXB). Modularity Q = {K['modularity']} (above 0 means real group structure).",
         "<b>PageRank:</b> the Google algorithm. An airport is important if it is connected to other important airports. Delhi and Mumbai rank highest.",
         "<b>Betweenness centrality:</b> how often an airport lies on the shortest path between two others. High betweenness means a transfer hub.",
         "<b>Social media link:</b> Louvain is like finding friend groups on Instagram, and PageRank is like finding influencers."])

h2("6.6 Python analytics pipeline and dashboard")
p("<font face=Courier>analytics/pipeline.py</font> runs the same logic as the Colab notebook using pandas and NetworkX, then writes "
  "<font face=Courier>web/data/dashboard.json</font> (and dashboard.js). The dashboard (<font face=Courier>web/index.html</font>) uses "
  "<b>Leaflet</b> for maps and <b>Chart.js</b> for charts. All libraries and the country outlines are bundled in "
  "<font face=Courier>web/vendor</font>, so it also works offline. Online, a dark street map loads underneath.")

h2("6.7 Google Colab")
p("A free cloud Jupyter notebook from Google. We use it because Hadoop, Spark and MongoDB need Linux and are hard to "
  "install on Windows. The notebook <font face=Courier>notebook/Flight_Trajectory_Analysis.ipynb</font> installs everything and runs end to end.")
story.append(PageBreak())

# ---------------- 7 ----------------
h1("7. Formulas and logic used")
h3("Haversine formula: distance between two points on Earth")
code("a = sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlon/2)\nd = 2 · R · asin(√a)        R = 6371 km")
h3("Route inefficiency")
code("flown   = sum of haversine distances between consecutive points\nstraight = haversine(origin airport, destination airport)\ninefficiency % = (flown / straight − 1) × 100")
h3("Avoidable CO₂")
code("excess_km = flown − straight\nCO₂ (kg)  = excess_km × 2.4 kg fuel/km × 3.16 kg CO₂ per kg fuel  ≈ excess_km × 7.6")
h3("Holding detection")
code("turn_i = ((heading_(i+1) − heading_i + 180) mod 360) − 180     # signed turn, −180..180\nholding if |Σ turn_i over the approach segment| ≥ 540°        # 1.5 full circles")

# ---------------- 8 ----------------
h1("8. Results (sample day)")
table(wrap([["Metric", "Value", "What it means"],
            ["Position records", f"{K['state_vectors']:,}", "Rows of ADS-B data processed"],
            ["Flights", f"{K['flights']}", "Trajectories rebuilt by MapReduce Job 2"],
            ["Airports / routes", f"{K['airports']} / {K['routes']}", "Nodes and directed links in the network"],
            ["Average route inefficiency", f"{K['avg_ineff']}%", "Flights flew this much more than the straight line"],
            ["Extra distance", f"{K['total_excess_km']:,} km / day", "Total wasted flying"],
            ["Avoidable CO₂", f"{K['total_co2_t']} t / day", f"≈ {int(K['total_co2_t'] * 365):,} t per year"],
            ["Holding events", f"{K['holdings']}", "All at DEL and BOM, during rush hours"],
            ["Communities", f"{K['communities']} (Q = {K['modularity']})", "North, West, South, East regions"]]),
      [4.2 * cm, 3.6 * cm, 8.2 * cm])
story.append(Image(os.path.join(ROOT, "ppt", "hourly.png"), width=15 * cm, height=15 * cm * 0.45))
p("<i>Traffic by hour of day: two clear rush-hour peaks.</i>")
hs = ", ".join(f"{h['near']} ({h['n']})" for h in D["hotspots"][:5])
p(f"<b>Top 5 hotspot boxes</b> (nearest airport, reports): {hs}.")

# ---------------- 9 ----------------
h1("9. The dashboard: what each tab shows")
table(wrap([["Tab", "What you see", "What to point out"],
            ["Top KPI cards", "Key numbers", "Size of the data and the CO₂ that could be saved"],
            ["Airspace Map", "Every flight path coloured by height (green low, yellow medium, blue high, red = holding); heatmap; red hotspot boxes; hour slider; 'Holding only'", "Move the slider to 8 and then 19; tick 'Holding only'; zoom into Mumbai to show the circles"],
            ["Temporal Analysis", "Stacked bar chart of traffic by hour and height; departures per hour; holding by airport", "Morning and evening peaks; holding only at DEL and BOM"],
            ["Route Efficiency", "Worst routes, CO₂ impact bars, table of the most inefficient flights", "Pune–Mumbai is worst because of holding"],
            ["Network & Communities", "Airport graph on the map coloured by Louvain community, sized by PageRank; hub ranking table", "4 regional groups; DEL and BOM are the top hubs"],
            ["Architecture", "Pipeline steps and syllabus mapping", "Which experiment each part covers"]]),
      [3.3 * cm, 6.9 * cm, 5.8 * cm])

# ---------------- 10 ----------------
h1("10. Use cases and benefits")
bullets(["<b>Airports Authority of India (AAI):</b> find detours and redesign routes (direct routing / Free Route Airspace), and check whether new procedures reduce holding.",
         "<b>Airport operators:</b> see which hours are saturated and plan runways, taxiways or new airports (as with Navi Mumbai and Noida).",
         "<b>Airlines:</b> move flights away from peak holding hours, plan fuel better, and reduce cost (fuel is about 30–40% of an airline's cost).",
         "<b>Government / DGCA:</b> measure aviation CO₂ and track climate targets.",
         "<b>Passengers:</b> fewer delays and fewer missed connections.",
         "<b>Same method, other domains:</b> ship tracking (AIS), city bus GPS, delivery fleets, and drone traffic management."])
story.append(PageBreak())

# ---------------- 11 ----------------
h1("11. How to run the project")
h2("A. On any college PC (Windows) for the dashboard demo")
bullets(["Install <b>Python 3.9+</b> from python.org (tick 'Add Python to PATH').",
         "Download the repo: github.com/manishraje28/SkyTrace → green <b>Code</b> button → <b>Download ZIP</b>, then extract it.",
         "Double-click <b>run_project.bat</b>. It installs packages, rebuilds the data and analytics, and opens <font face=Courier>http://localhost:8765</font> in the browser.",
         "<b>No internet / no Python?</b> Just double-click <font face=Courier>web/index.html</font>. The prebuilt data and all libraries are included, so it works offline (the street map background needs internet; the country outlines do not).",
         "The demo video is at <font face=Courier>video/SkyTrace_Demo.mp4</font> as a backup."])
h2("B. Hadoop / Spark / MongoDB in Google Colab")
bullets(["Open colab.research.google.com → File → Upload notebook → choose <font face=Courier>notebook/Flight_Trajectory_Analysis.ipynb</font>.",
         "Runtime → <b>Run all</b>. It takes about 6–8 minutes, mostly downloading Hadoop.",
         "Show these sections: HDFS commands, the two MapReduce jobs and their output, Spark SQL tables, MongoDB queries, Louvain communities, and the Folium map.",
         "<b>Tip:</b> run it once before the presentation so the outputs are already saved in the notebook."])
h2("C. On Linux / Mac")
code("chmod +x run_project.sh && ./run_project.sh")
h2("D. Rebuild the PPT, the guide or the video")
code("python ppt/build_ppt.py        # PPT with speaker notes\npython docs/build_guide.py      # this PDF\npython video/record.py          # demo video (needs playwright, edge-tts, ffmpeg)")

# ---------------- 12 ----------------
h1("12. Folder structure: what each file does")
table(wrap([["Path", "Purpose"],
            ["run_project.bat / .sh", "One-click setup and run"],
            ["requirements.txt", "Python packages needed"],
            ["data/generate_dataset.py", "Creates the 24-hour sample day in OpenSky format"],
            ["data/flights_states.csv", "The generated data (67k rows)"],
            ["hadoop/mapper_grid.py, reducer_sum.py", "MapReduce Job 1: density grid"],
            ["hadoop/mapper_route.py, reducer_route.py", "MapReduce Job 2: trajectory and route efficiency"],
            ["analytics/pipeline.py", "Local pipeline: phases, hotspots, routes, holding, graph → dashboard.json"],
            ["notebook/Flight_Trajectory_Analysis.ipynb", "Colab notebook: Hadoop, HDFS, MapReduce, Spark, MongoDB, Louvain"],
            ["notebook/build_notebook.py", "Script that generates the notebook"],
            ["web/index.html", "Dashboard"],
            ["web/data/dashboard.json / .js", "Analytics results used by the dashboard"],
            ["web/vendor/", "Leaflet, Chart.js and country outlines (offline)"],
            ["ppt/SkyTrace_Presentation.pptx", "Presentation with speaker notes"],
            ["ppt/content.py, build_ppt.py", "Slide text and script; PPT builder"],
            ["video/SkyTrace_Demo.mp4", "Narrated demo video"],
            ["docs/SkyTrace_Project_Guide.pdf", "This guide"]]), [6.4 * cm, 9.6 * cm])
story.append(PageBreak())

# ---------------- 13 ----------------
h1("13. Slide-by-slide presentation script")
p("Each slide below shows what is on the slide and what to say. The same script is also in the PowerPoint's speaker notes. "
  "Speak slowly; the whole talk takes about 7–8 minutes plus a 2–3 minute demo.")
for i, sd in enumerate(SLIDES, 1):
    block = [Paragraph(f"Slide {i}: {sd['title']}", H2)]
    for b in sd["bullets"]:
        block.append(Paragraph(b, BUL, bulletText="•"))
    block.append(Paragraph("<b>Say:</b> " + sd["notes"], SAY))
    story.append(KeepTogether(block))
story.append(PageBreak())

# ---------------- 14 ----------------
h1("14. Viva questions and simple answers")
QA = [
 ("What is a trajectory?", "The path of a moving object over time: a list of (time, latitude, longitude, height) points for one flight."),
 ("What does spatio-temporal mean?", "Data that has both a location (space) and a time. We analyse both together, for example the number of planes in a map box during a given hour."),
 ("What is ADS-B?", "A system where aircraft broadcast their GPS position, height and speed about every second. Ground receivers and OpenSky collect it."),
 ("Why Hadoop when the file is small?", "The sample is small so it runs in Colab, but real ADS-B data is about 1 GB per day globally and hundreds of GB per year. The same code scales by adding nodes; nothing changes in the logic."),
 ("What is the difference between HDFS and a normal file system?", "HDFS splits files into large blocks spread over many machines with replication (default 3 copies), so it can store huge files and survive machine failure. A normal file system lives on one disk."),
 ("Explain Map and Reduce in your project.", "In Job 1, Map turns each point into (map box, hour, height band) → 1, and Reduce adds the 1s to get counts per box. In Job 2, Map groups points by flight, and Reduce sorts them by time and calculates the distance flown."),
 ("Why Spark if we have MapReduce?", "Spark keeps data in memory, so it is much faster for multi-step work, and it supports SQL and window functions, which we need to compare each point with the previous one."),
 ("Why MongoDB and not MySQL?", "One flight path is a variable-length list of points. MongoDB stores it as one GeoJSON document and its 2dsphere index supports location queries like $near and $geoIntersects."),
 ("What is Louvain?", "A community detection algorithm. It moves nodes between groups to maximise modularity: many links inside groups and few between them. It found 4 regional airport groups."),
 ("What is modularity?", "A score from about −0.5 to 1 that measures how good a grouping is. Above about 0.2 means a clear group structure; ours is 0.23."),
 ("What is PageRank?", "Google's algorithm: a node is important if important nodes link to it. For airports, it identifies the hubs (Delhi, Mumbai)."),
 ("How do you detect holding?", "We add up a plane's turn angles near the airport. If it turned 540° or more in one direction (1.5 circles), it was circling and waiting."),
 ("How did you calculate CO₂?", "Extra km × 2.4 kg fuel per km (A320 cruise) × 3.16 kg CO₂ per kg of jet fuel, which is about 7.6 kg CO₂ per extra km."),
 ("Is the data real?", "The Colab notebook uses one real hour from OpenSky. Real data has no origin or destination, so route and network analysis use a realistic simulated day in the same format. We say this openly."),
 ("How is this related to SDG 9?", "SDG 9 is about reliable and sustainable infrastructure. Airspace and airports are infrastructure; we show where capacity runs out and how much fuel and CO₂ inefficiency costs, which supports planning decisions."),
 ("How is this related to social media analytics?", "The airport network is analysed with the same structure-based methods used for social networks: community detection (Louvain) and influencer ranking (PageRank, betweenness)."),
 ("What is great-circle distance?", "The shortest distance between two points on a sphere (the Earth). We calculate it with the haversine formula."),
]
for q, a in QA:
    story.append(KeepTogether([Paragraph(f"<b>Q. {q}</b>", P), Paragraph(a, ParagraphStyle("a", parent=P, leftIndent=12, textColor=MUT))]))

# ---------------- 15 ----------------
h1("15. Limitations and future scope")
bullets(["<b>Sample data:</b> route numbers come from a simulated day; next step is matching real OpenSky flights to airports by their first and last positions.",
         "<b>Single-node Hadoop:</b> Colab runs Hadoop on one machine; a real deployment would use a multi-node cluster or cloud (AWS EMR, Google Dataproc).",
         "<b>Future:</b> live streaming with Kafka + Spark Structured Streaming; delay prediction with machine learning; weather data (Delhi fog, monsoon); 3D visualisation of altitude; runway capacity simulation."])

doc = SimpleDocTemplate(os.path.join(ROOT, "docs", "SkyTrace_Project_Guide.pdf"), pagesize=A4,
                        leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
                        title="SkyTrace Project Guide", author="SkyTrace team")


def footer(c, d):
    c.setFont("Helvetica", 8); c.setFillColor(MUT)
    c.drawString(2.2 * cm, 1.2 * cm, "SkyTrace · Flight Trajectory Analysis · BDSMA Micro Project")
    c.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, f"Page {d.page}")


doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=footer)
print("PDF written")
