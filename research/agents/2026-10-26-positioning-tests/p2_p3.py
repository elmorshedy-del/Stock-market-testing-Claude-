"""P2 correlation x gamma and P3 large put closes (pre-registered at 8266317). Usage: python p2_p3.py <long> <etfs>  -> out/p2.json, out/p3.json"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
AG = HERE.parent
MICRO = AG.parent / "microstructure"
sys.path.insert(0, str(AG / "2026-10-25-channel-correction-theory"))
import dossier as Dz                               # noqa: E402
sys.path.insert(0, str(MICRO))
_c = os.getcwd(); os.chdir(MICRO)
import td_gamma as t                               # noqa: E402
os.chdir(_c)
RNG = np.random.default_rng(20261114)


def blocks(n, L=20):
    st = RNG.integers(0, n - L, int(np.ceil(n / L)))
    return np.concatenate([np.arange(s, s + L) for s in st])[:n]


def p2(long, etfs):
    spx = Dz.close(etfs, "%5EGSPC")
    C = pd.DataFrame({s: Dz.close(long, s) for s in Dz.PANEL}).reindex(spx.index)
    C = C[C.index >= "2009-06-01"]
    r = np.log(C).diff()
    vals, idx = [], C.index
    for t_ in range(10, len(idx)):
        X = r.iloc[t_ - 9:t_ + 1].dropna(axis=1)
        cc = np.corrcoef(X.to_numpy().T)
        vals.append(cc[np.triu_indices_from(cc, 1)].mean())
    corr = pd.Series(np.r_[np.full(10, np.nan), vals], index=idx)
    d5 = corr.diff(5)
    rising = d5.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True) >= 2 / 3
    gex = pd.read_csv(Path(etfs) / "DIX.csv", parse_dates=["date"]).set_index("date").gex
    gex = gex[~gex.index.duplicated()].reindex(idx)
    s = spx.reindex(idx)
    r10 = np.log(s.shift(-10) / s)
    hi = s.rolling(252, min_periods=60).max()
    near = s / hi - 1 > -0.05
    fwdmin = pd.concat([s.shift(-k) for k in range(1, 21)], axis=1).min(axis=1)
    dd = (fwdmin <= 0.95 * hi).astype(float).where(near & fwdmin.notna())
    D = pd.DataFrame({"neg": gex < 0, "rise": rising, "r10": r10, "dd": dd}).loc["2011-06-01":"2026-09-25"].dropna(subset=["r10"])
    D = D[gex.reindex(D.index).notna()]
    cells = {}
    for g in (True, False):
        for rr in (True, False):
            m = (D.neg == g) & (D.rise == rr)
            cells[f"GEX {'<0' if g else '>0'}, corr {'rising' if rr else 'not rising'}"] = {"days": int(m.sum()), "next 10d %": float(100 * D.r10[m].mean()),
                                                                                         "P(-5% within 20d | near high)": float(D.dd[m].mean())}
    def con(g):
        Z = D[D.neg == g].reset_index(drop=True)
        f = lambda Q: (Q.r10[Q.rise].mean() - Q.r10[~Q.rise].mean(), Q.dd[Q.rise].mean() - Q.dd[~Q.rise].mean())
        o = f(Z)
        bs = np.array([f(Z.iloc[blocks(len(Z))]) for _ in range(3000)])
        return {"next 10d return, rising minus not %": float(100 * o[0]), "p (<= 0 is the prediction; P(diff >= 0))": float(np.nanmean(bs[:, 0] >= 0)),
                "drawdown odds, rising minus not": float(o[1]), "p (P(diff <= 0))": float(np.nanmean(bs[:, 1] <= 0))}
    res = {"cells 2011-2026": cells, "PRIMARY: within GEX < 0": con(True), "same contrast within GEX > 0": con(False)}
    res["today"] = {"10d corr (41 panel) Oct 23": float(corr.iloc[-1]), "5d change": float(d5.iloc[-1]), "rising (top third)": bool(rising.iloc[-1]),
                    "SqueezeMetrics GEX Oct 23 $bn": float(gex.iloc[-1] / 1e9)}
    (OUT / "p2.json").write_text(json.dumps(res, indent=1, default=float))
    return res


def p3(etfs):
    out = {}
    ev_all = []
    for sym in ("SPY", "QQQ"):
        px = Dz.close(etfs, sym)
        r10 = px / px.shift(10) - 1
        spot = pd.read_csv(MICRO / "out" / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date").spot
        oi = t.read(sym, "oi")
        oi = oi.rename(columns={next(c for c in oi.columns if "open_interest" in c): "oi"})
        oi = oi[oi.cp == "P"][["date", "expiration", "strike", "oi"]]
        piv = oi.set_index(["expiration", "strike", "date"]).oi.sort_index()
        dates = sorted(oi.date.unique())
        rows = []
        prev = None
        for d in dates:
            cur = oi[oi.date == d].set_index(["expiration", "strike"]).oi
            if prev is not None:
                j = cur.to_frame("now").join(prev.to_frame("before"), how="inner")
                j["chg"] = j.now - j.before
                e = j.index.get_level_values(0)
                k = j.index.get_level_values(1)
                S = spot.asof(d) if len(spot[spot.index <= d]) else np.nan
                ok = ((e - d).days >= 3) & ((e - d).days <= 60) & (np.abs(k / S - 1) <= 0.15)
                jj = j[ok]
                big = jj[jj.chg <= -40000]
                sess = px.index[px.index < d]
                if len(sess):
                    s0 = sess[-1]
                    rows.append({"session": s0, "max drop": float(-jj.chg.min()) if len(jj) else 0.0, "large close": bool(len(big)),
                                 "contracts": int(-big.chg.sum()) if len(big) else 0, "r10 at session": float(r10.get(s0, np.nan))})
            prev = cur
        E = pd.DataFrame(rows).drop_duplicates("session").set_index("session")
        for h in (5, 10, 20):
            E[f"fwd{h}"] = np.log(px.shift(-h) / px).reindex(E.index)
        sell = E[(E["r10 at session"] <= -0.03)].dropna(subset=["fwd20"])
        ev = sell[sell["large close"]]
        keep, last = [], None
        for d in ev.index:
            if last is None or px.index.get_loc(d) - px.index.get_loc(last) >= 5:
                keep.append(d); last = d
        ev = ev.loc[keep]
        non = sell[~sell["large close"]]
        res = {"selloff sessions": int(len(sell)), "with a large put close (de-duplicated)": int(len(ev)), "large-close sessions overall": int(E["large close"].sum())}
        for h in (5, 10, 20):
            a, b = ev[f"fwd{h}"].to_numpy(), non[f"fwd{h}"].to_numpy()
            bs = np.array([RNG.choice(a, len(a)).mean() - RNG.choice(b, len(b)).mean() for _ in range(4000)]) if len(a) > 2 else np.array([np.nan])
            res[f"next {h}d %: with / without / diff / p"] = [float(100 * a.mean()) if len(a) else None, float(100 * b.mean()), float(100 * (a.mean() - b.mean())) if len(a) else None,
                                                              float(2 * min(np.nanmean(bs <= 0), np.nanmean(bs >= 0))) if len(a) > 2 else None]
        res["events"] = [str(d.date()) for d in ev.index]
        out[sym] = res
        ev_all.append(ev.assign(sym=sym))
    (OUT / "p3.json").write_text(json.dumps(out, indent=1, default=float))
    return out


if __name__ == "__main__":
    print("P2", json.dumps(p2(sys.argv[1], sys.argv[2]), indent=1, default=float))
    print("P3", json.dumps(p3(sys.argv[2]), indent=1, default=float))
