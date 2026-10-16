"""Part B (pre-registered at 12d46cd): do call gamma and put gamma damp or amplify the next day's range?
Usage: OMP_NUM_THREADS=1 python behaviour.py -> out/behaviour.json, out/behaviour_table.csv, out/behaviour.png"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
sys.path.insert(0, str(MICRO))
from common import load_bars                       # noqa: E402  (original, imported unchanged)

ASSETS = ["TSLA", "MSFT", "NVDA", "SPY", "QQQ"]
OWN_IV = {"TSLA", "MSFT", "NVDA"}
END = pd.Timestamp("2026-10-14")                   # last outcome day: the committed Oct 15 bars are intraday snapshots
NSHIFT, MINSHIFT = 1000, 60
RNG = np.random.default_rng(20261016)
FLOOR = 1e-4
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def frame(sym):
    g = pd.read_csv(MICRO / "out" / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date").sort_index()
    b = load_bars(sym)
    b = b[b.index <= END]
    lr = np.log(b.close).diff()
    x = pd.DataFrame(index=g.index.intersection(b.index))
    gc = (g.gex_classic - g.gex_short) / 2
    gp = -(g.gex_classic + g.gex_short) / 2
    dv = (b.close * b.volume).rolling(20).mean()
    x["ln_gc"] = np.log((gc / dv).reindex(x.index))
    x["ln_gp"] = np.log((gp / dv).reindex(x.index))
    x["comp_classic"] = (g.gex_classic / dv).reindex(x.index)
    x["comp_short"] = (g.gex_short / dv).reindex(x.index)
    rng = np.log(b.high / b.low).replace(0, np.nan)
    x["y_range"] = np.log(rng.shift(-1)).reindex(x.index)
    x["y_abs"] = np.log(lr.abs().clip(lower=FLOOR).shift(-1)).reindex(x.index)
    x["y_rv5"] = np.log(lr[::-1].rolling(5).std()[::-1].shift(-1)).reindex(x.index)
    x["c_range"] = np.log(rng).reindex(x.index)
    x["c_abs"] = np.log(lr.abs().clip(lower=FLOOR)).reindex(x.index)
    x["c_rv5"] = np.log(lr.rolling(5).std()).reindex(x.index)
    x["c_rv20"] = np.log(lr.rolling(20).std()).reindex(x.index)
    iv = g.atm_iv_30d.ffill() if sym in OWN_IV else load_bars("^VIX").close / 100
    x["c_iv"] = np.log(iv.reindex(x.index).ffill())
    return x.replace([np.inf, -np.inf], np.nan).dropna()


CONTROLS = ["c_range", "c_abs", "c_rv5", "c_rv20", "c_iv"]


def ols(y, X):
    A = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    return beta[1:], 1 - resid.var() / y.var()


def legs(x, yname, rng=RNG):
    z = lambda s: (s - s.mean()) / s.std()
    G = np.column_stack([z(x.ln_gc), z(x.ln_gp)])
    C = x[CONTROLS].to_numpy()
    y = x[yname].to_numpy()
    b, r2 = ols(y, np.column_stack([G, C]))
    n = len(y)
    null = np.empty((NSHIFT, 2))
    for k, s in enumerate(rng.integers(MINSHIFT, n - MINSHIFT, NSHIFT)):
        null[k] = ols(y, np.column_stack([np.roll(G, s, axis=0), C]))[0][:2]
    p = [(np.abs(null[:, j]) >= abs(b[j])).mean() for j in range(2)]
    return {"beta_call": float(b[0]), "beta_put": float(b[1]), "p_call": float(p[0]), "p_put": float(p[1]),
            "null95_call": float(np.quantile(np.abs(null[:, 0]), 0.95)), "null95_put": float(np.quantile(np.abs(null[:, 1]), 0.95)),
            "r2": float(r2), "days": int(n), "corr_ln_gc_ln_gp": float(np.corrcoef(x.ln_gc, x.ln_gp)[0, 1])}


def composites(x):
    z = lambda s: (s - s.mean()) / s.std()
    y, C = x.y_range.to_numpy(), x[CONTROLS].to_numpy()
    base = ols(y, C)[1]
    out = {}
    for k in ("comp_classic", "comp_short"):
        b, r2 = ols(y, np.column_stack([z(x[k]).to_numpy(), C]))
        out[k] = {"beta": float(b[0]), "delta_r2": float(r2 - base)}
    return out


def main():
    OUT.mkdir(exist_ok=True)
    res, rows = {}, []
    for sym in ASSETS:
        x = frame(sym)
        r = {"primary (next-day range)": legs(x, "y_range"), "next-day |return|": legs(x, "y_abs"), "next 5-day RV": legs(x, "y_rv5"),
             "2020-22": legs(x[x.index < "2023-01-01"], "y_range"), "2023-26": legs(x[x.index >= "2023-01-01"], "y_range"),
             "composites": composites(x), "period": [str(x.index[0].date()), str(x.index[-1].date())]}
        res[sym] = r
        for k in ("primary (next-day range)", "next-day |return|", "next 5-day RV", "2020-22", "2023-26"):
            v = r[k]
            rows.append({"asset": sym, "outcome": k, "days": v["days"], "beta_call": v["beta_call"], "p_call": v["p_call"],
                         "beta_put": v["beta_put"], "p_put": v["p_put"], "corr(ln Γc, ln Γp)": v["corr_ln_gc_ln_gp"]})
    t = res["TSLA"]["primary (next-day range)"]
    verdict = {}
    for leg, sgn_classic in (("call", -1), ("put", +1)):
        b, p = t[f"beta_{leg}"], t[f"p_{leg}"]
        if p >= 0.025:
            verdict[leg] = "inconclusive"
        else:
            dealer = "long" if b < 0 else "short"
            verdict[leg] = f"dealers net {dealer} {leg}s: classic {'right' if np.sign(b) == sgn_classic else 'wrong'}"
    res["TSLA verdict (pre-registered rule)"] = verdict
    (OUT / "behaviour.json").write_text(json.dumps(res, indent=1))
    T = pd.DataFrame(rows)
    T.to_csv(OUT / "behaviour_table.csv", index=False)
    figure(res)
    return res, T


def figure(res):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, ax = plt.subplots(figsize=(11, 5.2))
    for i, sym in enumerate(ASSETS):
        v = res[sym]["primary (next-day range)"]
        for dx, leg, col in ((-0.15, "call", GREEN), (0.15, "put", ORANGE)):
            b, band = v[f"beta_{leg}"], v[f"null95_{leg}"]
            ax.add_patch(plt.Rectangle((i + dx - 0.11, -band), 0.22, 2 * band, color=MUTED, alpha=0.15, lw=0))
            ax.scatter([i + dx], [b], s=70, color=col, edgecolor=INK, lw=0.6, zorder=5, label=f"{leg} gamma" if i == 0 else None)
            ax.text(i + dx, b + (0.012 if b >= 0 else -0.012), ("p < 0.001" if v[f'p_{leg}'] < 0.001 else f"p {v[f'p_{leg}']:.3f}"), ha="center", va="bottom" if b >= 0 else "top", fontsize=7.5, color=INK)
    ax.axhline(0, color=INK, lw=0.8)
    ax.set_xticks(range(len(ASSETS)), ASSETS)
    ax.set_ylabel("effect of +1 sd of log gamma on the log next-day range\nabove 0: amplifies (dealers short that leg)   below 0: damps (dealers long it)", fontsize=8.5)
    ax.set_ylim(-0.2, 0.18)
    ax.legend(loc="upper left", frameon=False, fontsize=8.5)
    ax.set_title("Does call or put gamma damp the next day's range? 2020-2026. Grey bars = 95% of time-shifted (luck) results.\nControls: today's range and |return|, 5- and 20-day realized vol, implied vol",
                 loc="left", fontsize=9.5, color=INK)
    f.savefig(OUT / "behaviour.png", dpi=145, bbox_inches="tight", facecolor=SURF)


if __name__ == "__main__":
    res, T = main()
    pd.set_option("display.width", 220)
    print(T.round(3).to_string(index=False))
    for sym in ASSETS:
        print(sym, res[sym]["period"], {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in res[sym]["composites"].items()})
    print("TSLA verdict:", res["TSLA verdict (pre-registered rule)"])
