"""
End-to-end local analytics pipeline (mirrors the Colab Hadoop/Spark notebook).
Reads data/flights_states.csv, writes web/data/dashboard.json for the frontend.

Stages:
 1. Trajectory reconstruction + flight phase segmentation
 2. Spatio-temporal density grid (same logic as hadoop/mapper_grid.py)
 3. Route efficiency (flown vs great-circle) -> excess fuel/CO2  [SDG 9 / 13]
 4. Holding-pattern detection (cumulative turn angle)
 5. Airport network graph: centrality + Louvain communities   (Exp 6/7)
"""
import json, math, os, sys
import pandas as pd
import networkx as nx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data"))
from generate_dataset import AIRPORTS

CO2_PER_KM = 7.6  # kg CO2 per km for an A320-class jet (~2.4 kg fuel/km x 3.16)


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(a))


def main():
    df = pd.read_csv(os.path.join(ROOT, "data", "flights_states.csv"))
    df = df.sort_values(["icao24", "time"])
    df["hour_ist"] = ((df.time % 86400) / 3600 + 5.5).astype(int) % 24
    df["phase"] = pd.cut(df.vertrate, [-99, -1, 1, 99], labels=["Descent", "Cruise", "Climb"]).astype(str)
    df.loc[df.baroaltitude < 30, "phase"] = "Ground"

    # ---- 1/3/4 per-flight metrics --------------------------------------------------
    flights, trajectories = [], []
    for icao, g in df.groupby("icao24", sort=False):
        la, lo, hd = g.lat.values, g.lon.values, g.heading.values
        flown = sum(hav(la[i], lo[i], la[i + 1], lo[i + 1]) for i in range(len(g) - 1))
        o, d = g.origin.iloc[0], g.destination.iloc[0]
        gc = hav(AIRPORTS[o][1], AIRPORTS[o][2], AIRPORTS[d][1], AIRPORTS[d][2])
        turns = [((hd[i + 1] - hd[i] + 180) % 360) - 180 for i in range(len(hd) - 2)]
        # holding = >= 540 deg net turning in one direction in the last 45 points
        tail = turns[-45:]
        holding = abs(sum(tail)) >= 540
        excess = max(flown - gc, 0)
        f = dict(icao24=icao, callsign=g.callsign.iloc[0], origin=o, destination=d,
                 dep_hour=int(g.hour_ist.iloc[0]), flown_km=round(flown, 1), gc_km=round(gc, 1),
                 ineff_pct=round((flown / gc - 1) * 100, 2), excess_km=round(excess, 1),
                 co2_excess_kg=round(excess * CO2_PER_KM), duration_min=int((g.time.iloc[-1] - g.time.iloc[0]) / 60),
                 max_alt=int(g.baroaltitude.max()), holding=bool(holding))
        flights.append(f)
        step = max(1, len(g) // 40)
        trajectories.append(dict(id=icao, cs=f["callsign"], o=o, d=d, hold=f["holding"], ineff=f["ineff_pct"],
                                 h=f["dep_hour"],
                                 p=[[round(a, 3), round(b, 3), int(c)] for a, b, c in
                                    zip(la[::step], lo[::step], g.baroaltitude.values[::step])]))
    fl = pd.DataFrame(flights)

    # ---- 2 spatio-temporal density grid -------------------------------------------
    df["cell_lat"] = (df.lat // 0.5) * 0.5 + 0.25
    df["cell_lon"] = (df.lon // 0.5) * 0.5 + 0.25
    grid = df.groupby(["cell_lat", "cell_lon"]).size().reset_index(name="n")
    heat = grid.values.tolist()
    hot = grid.sort_values("n", ascending=False).head(10)
    hotspots = []
    for _, r in hot.iterrows():
        near = min(AIRPORTS, key=lambda c: hav(r.cell_lat, r.cell_lon, AIRPORTS[c][1], AIRPORTS[c][2]))
        hotspots.append(dict(lat=r.cell_lat, lon=r.cell_lon, n=int(r.n), near=near))
    grid_hour = df.groupby(["hour_ist"]).size().reindex(range(24), fill_value=0).tolist()
    alt_band = pd.cut(df.baroaltitude, [-1, 30, 3000, 8000, 20000], labels=["GND", "LOW", "MID", "HIGH"])
    band_hour = df.groupby([df.hour_ist, alt_band], observed=False).size().unstack(fill_value=0)
    band_hour = band_hour.reindex(range(24), fill_value=0)

    # ---- 5 airport network graph ----------------------------------------------------
    routes = fl.groupby(["origin", "destination"]).agg(n=("icao24", "size"), ineff=("ineff_pct", "mean"),
                                                         co2=("co2_excess_kg", "sum")).reset_index()
    G = nx.Graph()
    for _, r in routes.iterrows():
        w = G.get_edge_data(r.origin, r.destination, {"weight": 0})["weight"]
        G.add_edge(r.origin, r.destination, weight=w + int(r.n))
    comms = nx.community.louvain_communities(G, weight="weight", seed=7)
    cid = {n: i for i, c in enumerate(comms) for n in c}
    modularity = nx.community.modularity(G, comms, weight="weight")
    btw = nx.betweenness_centrality(G, weight=None)
    pr = nx.pagerank(G, weight="weight")
    wdeg = dict(G.degree(weight="weight"))
    airports = [dict(code=c, name=AIRPORTS[c][0], lat=AIRPORTS[c][1], lon=AIRPORTS[c][2],
                     movements=int(wdeg.get(c, 0)), degree=G.degree(c) if c in G else 0,
                     betweenness=round(btw.get(c, 0), 4), pagerank=round(pr.get(c, 0), 4),
                     community=cid.get(c, -1),
                     holds=int(fl[(fl.destination == c) & fl.holding].shape[0]))
                for c in AIRPORTS]

    out = dict(
        kpis=dict(state_vectors=len(df), flights=len(fl), aircraft=df.icao24.nunique(), airports=len(AIRPORTS),
                  routes=len(routes), avg_ineff=round(fl.ineff_pct.mean(), 2),
                  total_excess_km=int(fl.excess_km.sum()), total_co2_t=round(fl.co2_excess_kg.sum() / 1000, 1),
                  holdings=int(fl.holding.sum()), modularity=round(modularity, 3), communities=len(comms)),
        hourly=grid_hour,
        band_hour={b: band_hour[b].tolist() for b in ["LOW", "MID", "HIGH"]},
        phase_counts=df.phase.value_counts().to_dict(),
        heat=heat, hotspots=hotspots,
        airports=airports,
        routes=[dict(o=r.origin, d=r.destination, n=int(r.n), ineff=round(r.ineff, 2), co2=int(r.co2))
                for _, r in routes.iterrows()],
        worst_routes=[dict(o=r.origin, d=r.destination, n=int(r.n), ineff=round(r.ineff, 2), co2=int(r.co2))
                      for _, r in routes[routes.n >= 3].sort_values("ineff", ascending=False).head(8).iterrows()],
        trajectories=trajectories,
        flights=fl.sort_values("ineff_pct", ascending=False).head(25).to_dict("records"),
    )
    os.makedirs(os.path.join(ROOT, "web", "data"), exist_ok=True)
    with open(os.path.join(ROOT, "web", "data", "dashboard.json"), "w") as fh:
        json.dump(out, fh, default=float)
    # also emit as JS so index.html works by double-click (no server / CORS)
    with open(os.path.join(ROOT, "web", "data", "dashboard.js"), "w") as fh:
        fh.write("window.DASHBOARD = "); json.dump(out, fh, default=float); fh.write(";")
    print(json.dumps(out["kpis"], indent=1))


if __name__ == "__main__":
    main()
