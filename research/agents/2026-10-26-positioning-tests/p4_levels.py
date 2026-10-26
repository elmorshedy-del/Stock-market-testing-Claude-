"""P4 (pre-registered at 0277f6c): order-level footprints. P4a stop cascades at prior 20-day highs; P4b round-number clustering (Osler).
Usage: python p4_levels.py <long> <breadth> <splits.json> <etfs>  -> out/p4.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
AG = HERE.parent
sys.path.insert(0, str(AG / "2026-10-25-channel-correction-theory"))
import dossier as Dz                               # noqa: E402
sys.path.insert(0, str(AG / "2026-10-25-momentum-reversal"))
import momentum as Mo                              # noqa: E402
RNG = np.random.default_rng(20261113)


def ohlc(path):
    d = json.loads(Path(path).read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    q = d["indicators"]["quote"][0]
    f = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=idx, dtype=float).dropna()
    f = f[~f.index.duplicated(keep="last")].sort_index()
    return f[(f.low > 0) & (f.high >= f.low)]


def cluster_boot(y, X, dates, k, nb=2000):
    """OLS coefficient k with a bootstrap over 20-day blocks of dates."""
    beta = np.linalg.lstsq(X, y, rcond=None)[0][k]
    ud = np.unique(dates)
    pos = {d: i for i, d in enumerate(ud)}
    di = np.array([pos[d] for d in dates])
    groups = [np.nonzero(di == i)[0] for i in range(len(ud))]
    bs = []
    for _ in range(nb):
        st = RNG.integers(0, len(ud) - 20, int(np.ceil(len(ud) / 20)))
        pick = np.concatenate([np.arange(s, s + 20) for s in st])
        ii = np.concatenate([groups[j] for j in pick])
        bs.append(np.linalg.lstsq(X[ii], y[ii], rcond=None)[0][k])
    bs = np.array(bs)
    return float(beta), float(np.percentile(bs, 5)), float(np.percentile(bs, 95)), float(2 * min((bs <= 0).mean(), (bs >= 0).mean()))


def main(long, bfold, splits, etfs):
    OUT.mkdir(exist_ok=True)
    names = Dz.PANEL + Mo.EXTRA
    spx = Dz.close(etfs, "%5EGSPC")
    R = Mo.market_regimes(spx)
    rows = []
    for s in names:
        f = ohlc(Path(long if s in Dz.PANEL else bfold) / f"{s}.json")
        f = f[(f.index >= "1990-01-01") & (f.index <= "2026-10-23")]
        r = np.log(f.close).diff()
        sd = r.rolling(20).std().shift(1)
        H = f.high.rolling(20).max().shift(1)
        cross = f.high > H
        prior = cross.shift(1).rolling(5).max().fillna(1).astype(bool)
        D = pd.DataFrame({"z": r / sd, "y1": r.shift(-1) / sd, "y5": r[::-1].rolling(5).sum()[::-1].shift(-1) / sd}, index=f.index)
        D["A_cross_close_above"] = (cross & ~prior & (f.close > H)).astype(float)
        D["B_cross_failed"] = (cross & ~prior & (f.close <= H)).astype(float)
        D["C_near_miss"] = (~cross & ~prior & (f.high >= 0.995 * H)).astype(float)
        D["trend"] = np.where(f.close > f.close.rolling(50).mean(), "stock above 50d", "stock below 50d")
        D["sym"] = s
        rows.append(D.dropna(subset=["z", "y1", "y5"]))
    P = pd.concat(rows)
    P["vol"] = R.vol.reindex(P.index).to_numpy()
    res = {"P4a stock-days": int(len(P)), "events A / B / C": [int(P[c].sum()) for c in ("A_cross_close_above", "B_cross_failed", "C_near_miss")]}
    def fit(Z, ycol):
        X = np.column_stack([np.ones(len(Z)), Z.A_cross_close_above, Z.B_cross_failed, Z.C_near_miss, Z.z.clip(-6, 6)])
        y = Z[ycol].clip(-10, 10).to_numpy()
        return {lab: cluster_boot(y, X, Z.index.to_numpy(), k, nb=1000 if len(Z) < 300000 else 600) for k, lab in ((1, "A crossed & closed above"), (2, "B crossed, closed back below"), (3, "C near miss (within 0.5%)"))}
    res["P4a next day (z units; coef, lo90, hi90, p)"] = fit(P, "y1")
    res["P4a next 5 days"] = fit(P, "y5")
    res["P4a next 5 days by market vol"] = {v: fit(P[P.vol == v], "y5") for v in ("low vol", "mid vol", "high vol")}
    res["P4a next 5 days by stock trend"] = {v: fit(P[P.trend == v], "y5") for v in ("stock above 50d", "stock below 50d")}
    # ---- P4b ----
    sp = json.loads(Path(splits).read_text())
    below_h = above_h = below_l = above_l = 0
    cross_rows = []
    for s in names + ["SPY"]:
        src = etfs if s == "SPY" else (long if s in Dz.PANEL else bfold)
        f = ohlc(Path(src) / f"{s}.json")
        start = max([pd.Timestamp("2015-01-01")] + [pd.Timestamp(x) + pd.Timedelta(days=1) for x in sp.get(s, [])])
        f = f[(f.index >= start) & (f.index <= "2026-10-23")]
        if len(f) < 100:
            continue
        step = np.where(f.close > 100, 10.0, np.where(f.close > 20, 5.0, 1.0)) if s != "SPY" else np.full(len(f), 5.0)
        for col, kind in (("high", "h"), ("low", "l")):
            x = f[col].to_numpy()
            up = np.ceil(x / step) * step
            dn = np.floor(x / step) * step
            bel = ((up - x) / up > 0) & ((up - x) / up <= 0.005)
            abv = ((x - dn) / dn > 0) & ((x - dn) / dn <= 0.005)
            if kind == "h":
                below_h += int(bel.sum()); above_h += int(abv.sum())
            else:
                below_l += int(bel.sum()); above_l += int(abv.sum())
        c, pc = f.close.to_numpy(), f.close.shift(1).to_numpy()
        r = np.log(f.close).diff(); sd = r.rolling(20).std().shift(1)
        y1 = (r.shift(-1) / sd).to_numpy()
        lev = np.ceil(pc / step) * step
        crossed = (pc < lev) & (c >= lev)
        short = (pc < lev) & (c < lev) & ((lev - c) / lev <= 0.005) & (f.high.to_numpy() < lev)
        for m, lab in ((crossed, "crossed a round level"), (short, "stopped just short")):
            cross_rows += [(d, lab, v) for d, v in zip(f.index[m], y1[m]) if np.isfinite(v)]
    res["P4b highs just below / just above a round level"] = [below_h, above_h, float(binomtest(below_h, below_h + above_h, 0.5).pvalue)]
    res["P4b lows just above / just below a round level"] = [above_l, below_l, float(binomtest(above_l, above_l + below_l, 0.5).pvalue)]
    Cx = pd.DataFrame(cross_rows, columns=["date", "type", "y1"]).set_index("date")
    a, b = Cx[Cx.type == "crossed a round level"].y1.clip(-10, 10), Cx[Cx.type == "stopped just short"].y1.clip(-10, 10)
    bs = np.array([RNG.choice(a.to_numpy(), len(a)).mean() - RNG.choice(b.to_numpy(), len(b)).mean() for _ in range(4000)])
    res["P4b next-day z: crossed vs stopped short (n, mean)"] = {"crossed": [int(len(a)), float(a.mean())], "stopped short": [int(len(b)), float(b.mean())],
                                                                "difference": float(a.mean() - b.mean()), "p (two-sided)": float(2 * min((bs <= 0).mean(), (bs >= 0).mean()))}
    (OUT / "p4.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:5]), indent=1, default=float))
