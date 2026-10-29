@echo off
REM SkyTrace - one-click run on any Windows PC (needs Python 3.9+)
cd /d "%~dp0"
echo Installing Python packages...
python -m pip install -q -r requirements.txt
echo Building dataset and analytics...
python data\generate_dataset.py
python analytics\pipeline.py
echo Opening dashboard at http://localhost:8765
start "" http://localhost:8765
python -m http.server 8765 --directory web
