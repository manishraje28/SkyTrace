# SkyTrace — Flight Trajectory Analysis (Spatio-Temporal Big Data Analytics)
**BDSMA Micro Project · SDG 9: Industry, Innovation & Infrastructure**

Big-data pipeline over ADS-B aircraft *state vectors* (OpenSky Network schema) for Indian airspace. It finds
**where and when** the airspace is congested, **which routes waste distance and fuel**, **where aircraft hold**, and
**which airports hold the network together**. These are the questions an air-navigation provider asks when planning
infrastructure (SDG target 9.1).

## Quick start (any college PC)
1. Install Python 3.9+ (tick "Add Python to PATH").
2. Download this repo (Code → Download ZIP) and extract it.
3. Double-click **`run_project.bat`** (Windows) or run `./run_project.sh` (Linux/Mac).
   The dashboard opens at http://localhost:8765.

No Python or no internet? Double-click `web/index.html`. The data and all libraries are bundled, so it works offline.
The online street map is optional; country outlines are built in.

## What's inside
| Path | What it is |
|---|---|
| `video/SkyTrace_Demo.mp4` | Narrated demo video (~5 min) |
| `ppt/SkyTrace_Presentation.pptx` | Presentation (13 slides, speaker notes included) |
| `docs/SkyTrace_Project_Guide.pdf` | Full project guide: every technology explained, slide-by-slide script, viva Q&A |
| `notebook/Flight_Trajectory_Analysis.ipynb` | Google Colab: Hadoop HDFS, MapReduce, Spark, MongoDB, Louvain |
| `web/index.html` | Interactive dashboard (Leaflet + Chart.js, bundled in `web/vendor`) |
| `data/generate_dataset.py` | 24-hour labelled dataset in OpenSky format (20 airports, 900 flights) |
| `hadoop/` | MapReduce jobs (Hadoop Streaming, Python): density grid and trajectory/route efficiency |
| `analytics/pipeline.py` | Local analytics pipeline → `web/data/dashboard.json` |
| `ppt/build_ppt.py`, `docs/build_guide.py`, `video/record.py` | Scripts that regenerate the PPT, the PDF and the video |

## Hadoop / Spark / MongoDB in Colab
Upload `notebook/Flight_Trajectory_Analysis.ipynb` to [colab.research.google.com](https://colab.research.google.com) and
choose Runtime → Run all (about 6–8 min). It is self-contained: it writes the scripts with `%%writefile`, installs
Hadoop 3.3.6, Spark and MongoDB 7, and downloads one real hour of OpenSky data.

**Test the MapReduce jobs without Hadoop:**
```bash
python hadoop/mapper_grid.py < data/flights_states.csv | sort | python hadoop/reducer_sum.py
```

## Dataset
- **Real data:** the [OpenSky Network historical state vectors](https://opensky-network.org/datasets/states).
  These are ADS-B reports with time, icao24, lat, lon, velocity, heading, vertrate, callsign and baro/geo altitude.
  The notebook downloads 2022-06-27 06:00 UTC and crops it to the Indian FIR.
- **Labelled sample:** OpenSky reports carry no origin or destination, so `generate_dataset.py` produces a
  reproducible day in the same schema. Traffic follows a gravity model (size / distance^1.3) with IST morning and
  evening peaks. About 35% of flights fly airway dog-legs, and about 25% of DEL/BOM arrivals hold. This sample feeds
  the route-efficiency and network analysis.

## Syllabus mapping
| Exp | Concept | Used for |
|---|---|---|
| 1 | HDFS | storage plus put/ls/cat/cp/mv/get/rm/du/fsck |
| 2 | NoSQL (MongoDB) | GeoJSON trajectory documents, `2dsphere` index, `$near`, `$geoIntersects`, aggregation |
| 3 | MapReduce | density grid, trajectory reconstruction |
| 6 | Community detection | Louvain on the airport graph (4 regional communities, Q≈0.23) |
| 7 | Structure-based model | PageRank and betweenness hub analysis |

## Key results (sample day)
- 900 flights, 67,279 state vectors, 235 routes
- Mean route inefficiency 4.1%: 17,856 km of extra distance, about 136 t of avoidable CO₂ per day
- 52 holding patterns, all at DEL and BOM, during the 06–10 and 17–21 IST banks
- Louvain splits the network into North, West, South and East regions; DEL and BOM rank highest on PageRank
