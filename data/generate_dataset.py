"""
Generates an ADS-B state-vector dataset in the exact OpenSky Network schema
(https://opensky-network.org/datasets/states) for Indian domestic airspace.

Columns: time, icao24, lat, lon, velocity, heading, vertrate, callsign,
         onground, baroaltitude, geoaltitude, origin, destination

The Colab notebook downloads REAL OpenSky data; this generator gives an
offline, reproducible sample with the same schema (plus origin/destination
labels) so the local pipeline + dashboard work without internet.
"""
import csv, math, random, os

random.seed(42)

AIRPORTS = {  # IATA: (name, lat, lon, weight = relative traffic)
    "DEL": ("Delhi", 28.5562, 77.1000, 10), "BOM": ("Mumbai", 19.0896, 72.8656, 9),
    "BLR": ("Bengaluru", 13.1986, 77.7066, 8), "HYD": ("Hyderabad", 17.2403, 78.4294, 6),
    "MAA": ("Chennai", 12.9941, 80.1709, 6), "CCU": ("Kolkata", 22.6547, 88.4467, 5),
    "AMD": ("Ahmedabad", 23.0772, 72.6347, 4), "PNQ": ("Pune", 18.5821, 73.9197, 4),
    "COK": ("Kochi", 10.1520, 76.4019, 3), "GOI": ("Goa", 15.3808, 73.8314, 3),
    "JAI": ("Jaipur", 26.8242, 75.8122, 2), "LKO": ("Lucknow", 26.7606, 80.8893, 2),
    "GAU": ("Guwahati", 26.1061, 91.5859, 2), "PAT": ("Patna", 25.5913, 85.0880, 2),
    "BBI": ("Bhubaneswar", 20.2444, 85.8178, 2), "IXC": ("Chandigarh", 30.6735, 76.7885, 2),
    "NAG": ("Nagpur", 21.0922, 79.0472, 2), "TRV": ("Trivandrum", 8.4821, 76.9200, 2),
    "SXR": ("Srinagar", 33.9871, 74.7742, 1), "IXB": ("Bagdogra", 26.6812, 88.3286, 1),
}
AIRLINES = ["AIC", "IGO", "VTI", "AKJ", "SEJ", "IAD"]
R = 6371.0


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def bearing(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def build_path(o, d):
    """Waypoints: origin -> (optional airway dog-leg) -> destination."""
    (_, la1, lo1, _), (_, la2, lo2, _) = AIRPORTS[o], AIRPORTS[d]
    pts = [(la1, lo1)]
    if random.random() < 0.35:  # airway routing / ATC vectoring detour
        f = random.uniform(0.3, 0.7)
        mla, mlo = la1 + (la2 - la1) * f, lo1 + (lo2 - lo1) * f
        off = random.uniform(0.4, 1.6) * random.choice([-1, 1])
        pts.append((mla + off * (lo2 - lo1) / 10, mlo - off * (la2 - la1) / 10))
    pts.append((la2, lo2))
    return pts


def sample_path(pts, n):
    segs = [hav(*pts[i], *pts[i + 1]) for i in range(len(pts) - 1)]
    total, out = sum(segs), []
    for k in range(n):
        s, i = total * k / (n - 1), 0
        while i < len(segs) - 1 and s > segs[i]:
            s -= segs[i]; i += 1
        f = s / segs[i] if segs[i] else 0
        (a, b), (c, e) = pts[i], pts[i + 1]
        out.append((a + (c - a) * f, b + (e - b) * f))
    return out, total


def main():
    codes = list(AIRPORTS)
    weights = [AIRPORTS[c][3] for c in codes]
    base_t = 1719446400  # 2024-06-27 00:00:00 UTC (OpenSky dataset day style)
    out = os.path.join(os.path.dirname(__file__), "flights_states.csv")
    rows = 0
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["time", "icao24", "lat", "lon", "velocity", "heading", "vertrate",
                    "callsign", "onground", "baroaltitude", "geoaltitude", "origin", "destination"])
        for fid in range(900):
            # gravity model: traffic ~ size(dest) / distance^1.3 -> regional structure
            o = random.choices(codes, weights)[0]
            dw = [0 if c == o else AIRPORTS[c][3] / hav(AIRPORTS[o][1], AIRPORTS[o][2],
                  AIRPORTS[c][1], AIRPORTS[c][2]) ** 1.3 for c in codes]
            d = random.choices(codes, dw)[0]
            # IST traffic peaks: morning 06-10, evening 17-21 (UTC = IST-5.5)
            hour_ist = random.choices(range(24), [1,1,1,1,2,4,9,10,9,7,5,5,5,5,5,6,7,9,10,9,7,4,2,1])[0]
            t0 = base_t + int(((hour_ist - 5.5) % 24) * 3600) + random.randint(0, 3599)
            pts = build_path(o, d)
            gc = hav(*pts[0], *pts[-1])
            cruise_v = random.uniform(220, 245)  # m/s
            dur = gc * 1000 / cruise_v * 1.15 + 600
            n = max(20, int(dur / 60))  # one state vector per minute
            path, _ = sample_path(pts, n)
            hold = d in ("DEL", "BOM") and random.random() < 0.25  # congestion holding
            icao = "%06x" % (0x800000 + fid * 37)
            cs = random.choice(AIRLINES) + str(random.randint(100, 9999))
            cruise_alt = random.choice([9450, 10050, 10650, 11250, 11850]) if gc > 400 else 7600
            seq = []
            for k, (la, lo) in enumerate(path):
                f = k / (n - 1)
                if f < 0.15:   alt, vr = cruise_alt * f / 0.15, cruise_alt / (0.15 * dur)
                elif f > 0.85: alt, vr = cruise_alt * (1 - f) / 0.15, -cruise_alt / (0.15 * dur)
                else:          alt, vr = cruise_alt, random.uniform(-0.5, 0.5)
                seq.append([la, lo, alt, vr])
            if hold:  # insert racetrack orbits ~40 km before destination
                la_h, lo_h = seq[-8][0], seq[-8][1]
                orbit = [[la_h + 0.12 * math.sin(a / 6 * math.pi), lo_h + 0.18 * math.cos(a / 6 * math.pi),
                          2400, 0] for a in range(24)]
                seq = seq[:-8] + orbit + seq[-8:]
            for k, (la, lo, alt, vr) in enumerate(seq):
                nxt = seq[min(k + 1, len(seq) - 1)]
                hd = bearing(la, lo, nxt[0], nxt[1]) if k < len(seq) - 1 else 0
                v = 75 if alt < 300 else (140 if alt < 3000 else cruise_v + random.gauss(0, 4))
                la += random.gauss(0, 0.004); lo += random.gauss(0, 0.004)
                ground = alt < 30
                w.writerow([t0 + k * 60, icao, round(la, 5), round(lo, 5), round(v, 1), round(hd, 1),
                            round(vr, 2), cs, ground, round(max(alt, 0), 1),
                            round(max(alt, 0) + 120, 1), o, d])
                rows += 1
    print(f"wrote {rows} state vectors -> {out}")


if __name__ == "__main__":
    main()
