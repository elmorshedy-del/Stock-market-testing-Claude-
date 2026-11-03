"""A4: exit-rule variants for the TSLA 5-min breakout + early-loss diagnostics. Usage: python exits.py -> out/exits.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"; O = HERE / "out"; C = 0.01; M = 5
VARS = ["base", "T15", "T30", "T60", "BE1R", "MID", "REIN30", "TRAIL1R", "REIN30+BE1R"]


def day_paths(lab):
    rth = pd.read_parquet(D / f"{lab}_rth_d2.parquet"); out = {}
    for d, g in rth.groupby("date"):
        g = g.set_index("hm").reindex(pd.date_range("09:30", "15:59", freq="1min").strftime("%H:%M"))
        if g.open.isna().iloc[:30].any(): continue
        out[d] = g[["open", "high", "low", "close"]].ffill().to_numpy()
    return out


def sim(x, rule):
    """Returns (pnl_bp, info) for the S1 5-min breakout on one day under an exit rule; long/short via mirroring."""
    hi, lo = x[:M, 1].max(), x[:M, 2].min()
    up = np.flatnonzero(x[M:330, 1] > hi + 0.01); dn = np.flatnonzero(x[M:330, 2] < lo - 0.01)
    iu = up[0] + M if len(up) else None; idn = dn[0] + M if len(dn) else None
    if iu is None and idn is None: return 0.0, None
    if idn is None or (iu is not None and iu < idn): side, i = 1, iu
    elif iu is None or idn < iu: side, i = -1, idn
    else: return 0.0, None
    y = x if side > 0 else -x[:, [0, 2, 1, 3]]; H, L = (hi, lo) if side > 0 else (-lo, -hi)
    e = max(H + 0.01, y[i, 0]); ein = e + C
    stop = (L + H) / 2 if rule == "MID" else L
    R = ein - stop; best = y[i, 1]; trailing = False; be = False
    path = []
    # entry bar: conservative stop check on its close only (as in the engine)
    if y[i, 3] <= stop: px = min(stop, y[i, 3]) - 2 * C; return _ret(px, ein, side), {"exit": "stop", "R": R / abs(ein) * 1e4, "path": path}
    for j in range(i + 1, 390):
        o, h, l, c = y[j]
        if l <= stop:
            px = min(stop, o) - 2 * C; return _ret(px, ein, side), {"exit": "be" if be else ("trail" if trailing else "stop"), "R": R / abs(ein) * 1e4, "path": path}
        best = max(best, h); mins = j - i
        path.append((mins, (c - C - ein) / ein * 1e4 / (R / ein * 1e4)))
        if rule in ("T15", "T30", "T60") and mins == int(rule[1:]) and c - C <= ein:
            return _ret(c - C, ein, side), {"exit": "time", "R": R / abs(ein) * 1e4, "path": path}
        if rule in ("REIN30", "REIN30+BE1R") and mins <= 30 and c < H:
            return _ret(c - C, ein, side), {"exit": "rein", "R": R / abs(ein) * 1e4, "path": path}
        if rule in ("BE1R", "REIN30+BE1R") and not be and best >= ein + R: stop = max(stop, ein); be = True
        if rule == "TRAIL1R" and best >= ein + R: stop = max(stop, best - R); trailing = True
    return _ret(y[389, 3] - C, ein, side), {"exit": "close", "R": R / abs(ein) * 1e4, "path": path}


def _ret(px, ein, side):
    return (px - ein) / abs(ein) * 1e4   # mirrored (negative) prices for shorts: divide by |entry|


def summ(p):
    p = np.asarray(p); t = p[p != 0]; eq = np.cumsum(p)
    return {"mean bp/day": round(float(p.mean()), 2), "Sharpe": round(float(p.mean() / p.std() * np.sqrt(252)), 2), "win %": round(float((t > 0).mean() * 100), 1),
            "avg win bp": round(float(t[t > 0].mean()), 1), "avg loss bp": round(float(t[t < 0].mean()), 1), "worst day bp": round(float(p.min()), 0),
            "max drawdown bp (1x, simple)": round(float((eq - np.maximum.accumulate(eq)).min()), 0)}


def boot_diff(a, b, n=2000, blk=10, seed=1):
    rng = np.random.default_rng(seed); N = len(a); d = np.asarray(a) - np.asarray(b); out = []
    for _ in range(n):
        idx = np.concatenate([np.arange(s, min(s + blk, N)) for s in rng.integers(0, N, N // blk + 1)])[:N]; out.append(d[idx].mean())
    return [round(float(np.quantile(out, 0.05)), 2), round(float(np.quantile(out, 0.95)), 2)]



def main():
    res = {}
    for lab, nm in (("TSLA", "2024-26 design"), ("TSLA2020", "2020-23 confirm")):
        P = day_paths(lab); per = {v: [] for v in VARS}; diag = []
        for d, x in P.items():
            for v in VARS:
                r, info = sim(x, v); per[v].append(r)
                if v == "base" and info is not None: diag.append((r, info))
        res[nm] = {"days": len(P), "variants": {v: summ(per[v]) for v in VARS}}
        base = np.array(per["base"])
        for v in VARS[1:]: res[nm]["variants"][v]["mean diff vs base, 90% CI"] = boot_diff(per[v], base)
        # early-loss diagnostics on the base rule
        fin = np.array([r for r, _ in diag]); dg = {}
        for T in (15, 30, 60):
            at = np.array([next((q for m, q in info["path"] if m == T), np.nan) for _, info in diag])
            ok = ~np.isnan(at)
            dg[f"at +{T} min: P(final win | in profit) / P(final win | not in profit) / share not in profit"] = [round(float((fin[ok & (at > 0)] > 0).mean()), 3), round(float((fin[ok & (at <= 0)] > 0).mean()), 3), round(float((at[ok] <= 0).mean()), 3)]
            dg[f"at +{T} min: P(final win | below -0.5R)"] = round(float((fin[ok & (at <= -0.5)] > 0).mean()), 3)
        mae = np.array([min([q for _, q in info["path"]] + [0]) for r, info in diag if r > 0])
        dg["winners' worst point (MAE, R): median / 75th / 90th pct"] = [round(float(np.median(mae)), 2), round(float(np.quantile(mae, 0.25)), 2), round(float(np.quantile(mae, 0.10)), 2)]
        dg["exit mix (base)"] = pd.Series([i["exit"] for _, i in diag]).value_counts(normalize=True).round(3).to_dict()
        res[nm]["early-loss diagnostics (base)"] = dg
        if nm.startswith("2024"):
            best = max(VARS[1:], key=lambda v: res[nm]["variants"][v]["Sharpe"]); res["named best (2024-26, by Sharpe)"] = best
    b = res["named best (2024-26, by Sharpe)"]; c = res["2020-23 confirm"]["variants"]
    res["CONFIRMED on 2020-23"] = bool(c[b]["Sharpe"] > c["base"]["Sharpe"] and c[b]["mean bp/day"] >= 0.8 * c["base"]["mean bp/day"] and c[b]["mean diff vs base, 90% CI"][1] > 0)
    json.dump(res, open(O / "exits.json", "w"), indent=1, default=str)
    for nm in ("2024-26 design", "2020-23 confirm"):
        print("=====", nm, res[nm]["days"], "days")
        for v, s in res[nm]["variants"].items(): print(f"  {v:12s} {s}")
        for k, v in res[nm]["early-loss diagnostics (base)"].items(): print("   ", k, v)
    print("named best:", b, "| confirmed:", res["CONFIRMED on 2020-23"])


if __name__ == "__main__":
    main()
