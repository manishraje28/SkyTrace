#!/usr/bin/env python3
"""MapReduce Job 2 reducer - computes, per flight: flown distance, great-circle
distance, route inefficiency %, duration, max altitude.
Output: flight \t origin,destination,flown_km,gc_km,ineff_pct,dur_min,max_alt"""
import sys, math


def hav(a, b, c, d):
    p1, p2 = math.radians(a), math.radians(c)
    x = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(d - b) / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))


def emit(key, pts):
    pts.sort()
    flown = sum(hav(pts[i][1], pts[i][2], pts[i + 1][1], pts[i + 1][2]) for i in range(len(pts) - 1))
    gc = hav(pts[0][1], pts[0][2], pts[-1][1], pts[-1][2]) or 1
    dur = (pts[-1][0] - pts[0][0]) / 60
    print(f"{key}\t{pts[0][4]},{pts[0][5]},{flown:.1f},{gc:.1f},{(flown / gc - 1) * 100:.2f},"
          f"{dur:.0f},{max(p[3] for p in pts):.0f}")


cur, pts = None, []
for line in sys.stdin:
    key, _, v = line.rstrip("\n").partition("\t")
    t, la, lo, alt, o, d = v.split(",")
    if key != cur and cur is not None:
        emit(cur, pts); pts = []
    cur = key
    pts.append((int(float(t)), float(la), float(lo), float(alt or 0), o, d))
if cur is not None:
    emit(cur, pts)
