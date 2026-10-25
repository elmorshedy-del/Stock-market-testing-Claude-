"""Amendment 1: do SPY rallies hold better when the close is above the gamma flip? Usage: python rallies.py  -> out/rallies.json, out/reclaims.csv"""
import json

import numpy as np
import pandas as pd

import spy_gamma as G

RNG = np.random.default_rng(20261109)
NB = 4000


def slope(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    xc = x - x.mean()
    return float((xc * (y - y.mean())).sum() / (xc ** 2).sum())


def blocks(n, L=20):
    st = RNG.integers(0, n - L, int(np.ceil(n / L)))
    return np.concatenate([np.arange(s, s + L) for s in st])[:n]


def main():
    eng = pd.read_csv(G.t.OUT / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date")[["spot", "flip_classic"]]
    new = pd.read_csv(G.OUT / "daily.csv", index_col=0, parse_dates=True)[["spot", "flip_classic"]]
    h = pd.concat([eng, new])
    h = h[~h.index.duplicated(keep="last")].sort_index().dropna()
    r = np.log(h.spot).diff()
    sd = r.rolling(20).std().shift(1)
    D = pd.DataFrame({"x": r / sd, "above": (h.spot > h.flip_classic).astype(float)}, index=h.index)
    D["c10"] = r[::-1].rolling(10).sum()[::-1].shift(-1) / sd
    D = D.dropna()
    def split(Z, side):
        Z = Z[Z.x > 0] if side == "up" else Z[Z.x < 0]
        A, B = Z[Z.above == 1], Z[Z.above == 0]
        sa, sb = slope(A.x.to_numpy(), A.c10.to_numpy()), slope(B.x.to_numpy(), B.c10.to_numpy())
        ZZ = Z.reset_index(drop=True)
        bs = []
        for _ in range(NB):
            ii = blocks(len(ZZ))
            q = ZZ.iloc[ii]
            qa, qb = q[q.above == 1], q[q.above == 0]
            bs.append(slope(qa.x.to_numpy(), qa.c10.to_numpy()) - slope(qb.x.to_numpy(), qb.c10.to_numpy()))
        bs = np.array(bs)
        return {"above flip: share of day's move added (+) / given back (-) by day 10": sa, "below flip": sb, "A - B": sa - sb,
                "p (A - B <= 0)": float((bs <= 0).mean()), "days above / below": [int(len(A)), int(len(B))]}
    res = {"period": [str(D.index[0].date()), str(D.index[-1].date())]}
    res["PRIMARY up days, 2020-2026"] = split(D, "up")
    res["down days, 2020-2026"] = split(D, "down")
    res["up days, 2020-2022"] = split(D[D.index < "2023-01-01"], "up")
    res["up days, 2023-2026 (channel era)"] = split(D[D.index >= "2023-01-01"], "up")
    ab = (h.spot > h.flip_classic).astype(int).to_numpy()
    rows = []
    for i in range(3, len(h) - 10):
        if ab[i] == 1 and ab[i - 3:i].sum() == 0:
            rows.append({"date": h.index[i].date(), "still above flip after 10 sessions": bool(ab[i + 10]),
                         "share of next 10 sessions above flip": float(ab[i + 1:i + 11].mean()),
                         "next 10-day return %": float(100 * (h.spot.iloc[i + 10] / h.spot.iloc[i] - 1))})
    Rc = pd.DataFrame(rows)
    Rc.to_csv(G.OUT / "reclaims.csv", index=False)
    f10 = 100 * (h.spot.shift(-10) / h.spot - 1)
    res["flip reclaims (first close above after >= 3 below)"] = {
        "events": int(len(Rc)), "still above after 10 sessions": float(Rc["still above flip after 10 sessions"].mean()),
        "mean share of next 10 sessions above": float(Rc["share of next 10 sessions above flip"].mean()),
        "mean next 10-day return %": float(Rc["next 10-day return %"].mean()), "median": float(Rc["next 10-day return %"].median()),
        "all days: mean next 10-day return %": float(f10.mean()), "all days: share of days above flip": float(ab.mean()),
        "channel era (2023+) events / still above / mean 10d %": [int((pd.to_datetime(Rc.date) >= "2023-01-01").sum()),
                                                                  float(Rc[pd.to_datetime(Rc.date) >= "2023-01-01"]["still above flip after 10 sessions"].mean()),
                                                                  float(Rc[pd.to_datetime(Rc.date) >= "2023-01-01"]["next 10-day return %"].mean())]}
    pu = res["PRIMARY up days, 2020-2026"]
    res["verdict"] = "rallies hold better above the flip" if pu["A - B"] > 0 and pu["p (A - B <= 0)"] < 0.05 else "no reliable difference"
    (G.OUT / "rallies.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=float))
