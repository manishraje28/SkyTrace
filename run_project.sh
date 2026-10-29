#!/usr/bin/env bash
# SkyTrace - run on Linux / macOS (needs Python 3.9+)
cd "$(dirname "$0")"
python3 -m pip install -q -r requirements.txt
python3 data/generate_dataset.py
python3 analytics/pipeline.py
echo "Dashboard: http://localhost:8765"
(sleep 2; (xdg-open http://localhost:8765 || open http://localhost:8765) >/dev/null 2>&1) &
python3 -m http.server 8765 --directory web
