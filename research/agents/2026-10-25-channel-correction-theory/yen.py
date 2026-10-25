"""Amendment 2 (pre-registered at afff0ea): the yen carry trade as spark (dip anatomy), pre-top signal, or fuel (during the decline).
USD/JPY bars are labelled by their London date; Yahoo's FX 'close' for date D is effectively the level at the start of D, so it is known
before the US session (no look-ahead). Usage: python yen.py <etfs folder>  -> out/yen.json, out/yen_episodes.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import dips as Dp
import dossier as Dz

RNG = np.random.default_rng(20261104)
YEN = ["yen 20-day (USD/JPY change)", "yen 5-day (USD/JPY change)", "yen volatility percentile"]


def usdjpy(etfs):
    d = json.loads((Path(etfs) / "JPY=X.json").read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("Europe/London").normalize().tz_localize(None)
    s = pd.Series(d["indicators"]["quote"][0]["close"], index=idx, dtype=float).dropna()
    s = s[~s.index.duplicated(keep="last")].sort_index()
    return s[s > 0]


def main(etfs):
    D = pd.read_csv(Dz.OUT / "daily.csv", index_col=0, parse_dates=True)
    spx = Dz.close(etfs, "%5EGSPC").reindex(D.index)
    D["margin debt growth"], D["margin debt vs prices"] = Dp.margin_daily(D.index, spx)
    j = usdjpy(etfs).reindex(D.index, method="ffill")
    lj = np.log(j)
    D[YEN[0]] = lj.diff(20)
    D[YEN[1]] = lj.diff(5)
    D[YEN[2]] = Dz.pct(lj.diff().rolling(20).std())
    dist = D.pop("dist")
    D = D.drop(columns=["similarity"], errors="ignore")
    idx = D.index
    ref = (idx >= Dz.CH0) & (idx <= Dz.CH1) & (dist >= -0.03).to_numpy()
    mu, sd = D[ref].mean(), D[ref].std()
    Z5 = (D.rolling(5, min_periods=4).mean() - mu) / sd
    Z10 = (D.rolling(10, min_periods=7).mean() - mu) / sd
    E = pd.read_csv(Dz.OUT / "dips.csv", parse_dates=["high date", "start", "decided"])
    prof = pd.DataFrame({f"{r.outcome[:4]} {r['high date'].date()}": Z5.loc[r.start] for _, r in E.iterrows()})
    dec = [c for c in prof.columns if not c.startswith("open")]
    lab = np.array([c.startswith("corr") for c in dec])
    major = np.array([any(m in c for m in Dz.MAJOR) for c in dec])
    res = {"(a) spark: dip anatomy": {}}
    for k in YEN:
        v = prof.loc[k, dec].to_numpy(float)
        c, b = v[lab], v[~lab]
        med, diff = np.median(b), c.mean() - b.mean()
        side = 1 if diff > 0 else -1
        a = (c[:, None] > b[None, :]).mean()
        res["(a) spark: dip anatomy"][k] = {
            "mean z corrections": float(c.mean()), "mean z bounces": float(b.mean()), "corrections beyond bounce median": int((side * (c - med) > 0).sum()),
            "main corrections beyond": int((side * (v[major] - med) > 0).sum()), "AUC": float(max(a, 1 - a)),
            "passes rule": bool((side * (c - med) > 0).sum() >= 7 and np.all(side * (v[major] - med) > 0) and abs(diff) >= 0.5),
            "per episode": dict(zip(dec, np.round(v, 2))), "today (open episode)": float(prof.loc[k, [c for c in prof.columns if c.startswith("open")][0]])}
    V = prof[dec].dropna()
    W = V.to_numpy(float)
    def aucs(l):
        cc, bb = W[:, l], W[:, ~l]
        x = (cc[:, :, None] > bb[:, None, :]).mean(axis=(1, 2))
        return np.maximum(x, 1 - x)
    labV = np.array([c.startswith("corr") for c in V.columns])
    obs = pd.Series(aucs(labV), index=V.index).sort_values(ascending=False)
    best = np.array([aucs(RNG.permutation(labV)).max() for _ in range(5000)])
    res["best-of-29 luck check"] = {"indicators": int(len(V)), "top 5 AUC": obs.head(5).round(3).to_dict(),
                                    "family-wise p": {k: float((best >= obs[k]).mean()) for k in list(obs.index[:3]) + YEN}}
    tops = Dz.MAJOR + Dz.MINOR
    res["(b) pre-top 10-day profile (z)"] = {k: {e: float(Z10.loc[pd.Timestamp(e), k]) for e in tops} for k in YEN}
    rows = []
    for _, r in E[E.outcome != "open"].iterrows():
        jd = float(100 * (lj.loc[r.decided] - lj.loc[r.start]))
        hi = r["high date"]
        after = spx[spx.index > hi]
        nxt = after[after > spx.loc[hi]]
        end = nxt.index[0] if len(nxt) else spx.index[-1]
        seg = spx[(spx.index >= hi) & (spx.index <= end)]
        trough = seg.idxmin()
        rows.append({"episode": f"{r.outcome[:4]} {hi.date()}", "outcome": r.outcome,
                     "USD/JPY % start -> decided": jd, "S&P depth % (high -> trough)": float(100 * (seg.min() / spx.loc[hi] - 1)),
                     "USD/JPY % high -> trough": float(100 * (lj.loc[trough] - lj.loc[hi])), "trough": str(trough.date())})
    Y = pd.DataFrame(rows)
    Y.to_csv(Dz.OUT / "yen_episodes.csv", index=False)
    cr, bo = Y[Y.outcome == "correction"], Y[Y.outcome == "bounce"]
    strengthen = lambda s: int((s < 0).sum())
    res["(c) fuel: yen during the decline"] = {
        "corrections with yen strengthening (start -> decided)": f"{strengthen(cr['USD/JPY % start -> decided'])} of {len(cr)}",
        "bounces with yen strengthening (start -> decided)": f"{strengthen(bo['USD/JPY % start -> decided'])} of {len(bo)}",
        "median USD/JPY % start -> decided: corrections / bounces": [float(cr["USD/JPY % start -> decided"].median()), float(bo["USD/JPY % start -> decided"].median())],
        "corrections: USD/JPY % high -> trough": dict(zip(cr.episode, cr["USD/JPY % high -> trough"].round(2))),
        "corrections: S&P depth %": dict(zip(cr.episode, cr["S&P depth % (high -> trough)"].round(1))),
        "corr(yen move high->trough, depth) across corrections": float(np.corrcoef(cr["USD/JPY % high -> trough"], cr["S&P depth % (high -> trough)"])[0, 1])}
    sp = res["(a) spark: dip anatomy"]
    fuel_ok = strengthen(cr["USD/JPY % start -> decided"]) >= 6 and strengthen(bo["USD/JPY % start -> decided"]) <= len(bo) / 2
    res["reading"] = "spark" if any(v["passes rule"] for v in sp.values()) else ("fuel" if fuel_ok else "context only")
    res["today"] = {"USD/JPY": float(j.iloc[-1]), "Oct 6 (S&P high)": float(j.loc["2026-10-06"]),
                    "USD/JPY % since Oct 6": float(100 * (lj.iloc[-1] - lj.loc["2026-10-06"])),
                    "10-day z": {k: float(Z10[k].iloc[-1]) for k in YEN}, "yen 20-day raw %": float(100 * D[YEN[0]].iloc[-1]),
                    "yen vol percentile raw": float(D[YEN[2]].iloc[-1]), "USD/JPY 1y range": [float(j.iloc[-252:].min()), float(j.iloc[-252:].max())]}
    (Dz.OUT / "yen.json").write_text(json.dumps(res, indent=1, default=float))
    return res, Y


if __name__ == "__main__":
    res, Y = main(sys.argv[1])
    pd.set_option("display.width", 250)
    print(Y.round(2).to_string())
    print(json.dumps(res, indent=1, default=float))
