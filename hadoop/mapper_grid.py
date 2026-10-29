#!/usr/bin/env python3
"""MapReduce Job 1 (Hadoop Streaming) - spatio-temporal airspace density.
Emits key = <lat_cell>,<lon_cell>,<hour_utc>,<altitude_band>  value = 1
Grid = 0.5 deg cells; altitude bands: GND / LOW(<3km) / MID(3-8km) / HIGH(>8km)."""
import sys

for line in sys.stdin:
    p = line.strip().split(",")
    if not p or p[0] == "time" or len(p) < 10:
        continue
    try:
        t, lat, lon, alt = int(float(p[0])), float(p[2]), float(p[3]), float(p[9] or 0)
    except ValueError:
        continue
    band = "GND" if alt < 30 else "LOW" if alt < 3000 else "MID" if alt < 8000 else "HIGH"
    print(f"{int(lat // 0.5)},{int(lon // 0.5)},{(t // 3600) % 24},{band}\t1")
