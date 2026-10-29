#!/usr/bin/env python3
"""MapReduce Job 2 - per-flight trajectory reconstruction (key = icao24|callsign).
Emits flight_key \t time,lat,lon,alt,origin,destination so the reducer receives
all points of one flight together (secondary sort on time done in reducer)."""
import sys

for line in sys.stdin:
    p = line.strip().split(",")
    if not p or p[0] == "time" or len(p) < 13:
        continue
    print(f"{p[1]}|{p[7]}\t{p[0]},{p[2]},{p[3]},{p[9]},{p[11]},{p[12]}")
