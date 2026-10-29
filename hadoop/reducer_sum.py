#!/usr/bin/env python3
"""Generic sum reducer (input sorted by key, as Hadoop guarantees)."""
import sys

cur, total = None, 0
for line in sys.stdin:
    key, _, val = line.rstrip("\n").partition("\t")
    if key != cur:
        if cur is not None:
            print(f"{cur}\t{total}")
        cur, total = key, 0
    total += int(val)
if cur is not None:
    print(f"{cur}\t{total}")
