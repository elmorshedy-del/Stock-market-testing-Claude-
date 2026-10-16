"""Follow-up B (pre-registered in README.md at 6e17d28): can RSI tell a true TSLA low from a false one in real time?
(a) at a new 20-session closing low; (b) after the first bounce of 1 ATR off it. Outcome: the low holds (no close
below it) for the next 10 sessions. Predictors: bullish RSI divergence (primary), RSI bottom tenth, the options setup.
Usage: OMP_NUM_THREADS=1 python followup_false_lows.py -> out/followup_false_lows.json, out/followup_false_lows.png
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import followup_rsi_lows as F
import indicators as I

BLUE, ORANGE, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
ALPHA = 0.05 / 2
H = 10


def frame():
    D = F.data()
    b, raw, _, _ = I.frame("TSLA", "daily")
    D["atr"] = (raw["ATR%"] * b.close).reindex(D.index)
    D = D[D.index >= "2010-08-01"]
    S = I.setups()["TSLA"].setup
    D["setup"] = S.reindex(D.index)                        # NaN before 2021 (no options history)
    return D.reset_index().rename(columns={"index": "date"})


def new_lows(c):
    prior = pd.Series(c).shift(1).rolling(19, min_periods=19).min().to_numpy()
    return np.where(c < prior)[0]


def holds(c, i, level):
    w = c[i + 1:i + 1 + H]
    return float(w.min() >= level) if len(w) == H else np.nan


def divergence(D, lows_set, k):
    """At low k: the lowest close 5-30 sessions earlier, if it was a 20-session low and above c[k], vs RSI."""
    c, r = D.c.to_numpy(), D.rsi.to_numpy()
    if k < 30:
        return np.nan
    j = k - 30 + int(np.argmin(c[k - 30:k - 4]))
    if j not in lows_set or not c[k] < c[j] or not (np.isfinite(r[k]) and np.isfinite(r[j])):
        return np.nan
    return float(r[k] > r[j])


def candidates(D):
    c = D.c.to_numpy()
    lows = new_lows(c)
    ls = set(lows.tolist())
    A = []
    for k in lows:
        A.append({"day": k, "low": k, "true low": holds(c, k, c[k]), "D": divergence(D, ls, k),
                  "L": float(D.rsi_pct.iloc[k] <= 0.10) if np.isfinite(D.rsi_pct.iloc[k]) else np.nan,
                  "S": float(D.setup.iloc[k]) if pd.notna(D.setup.iloc[k]) else np.nan, "burst10": D.burst10.iloc[k]})
    B, used = [], set()
    atr = D.atr.to_numpy()
    for u in range(len(c)):
        prev = lows[(lows < u) & (lows >= u - 10)]
        if not len(prev):
            continue
        k = int(prev.max())
        if k in used or not np.isfinite(atr[u]) or c[u] < c[k] + atr[u]:
            continue
        used.add(k)
        B.append({"day": u, "low": k, "true low": holds(c, u, c[k]), "D": divergence(D, ls, k),
                  "L": float(D.rsi_pct.iloc[k] <= 0.10) if np.isfinite(D.rsi_pct.iloc[k]) else np.nan,
                  "S": float(D.setup.iloc[u]) if pd.notna(D.setup.iloc[u]) else np.nan, "burst10": D.burst10.iloc[u]})
    return pd.DataFrame(A), pd.DataFrame(B)


def test(C, col):
    z = C.dropna(subset=[col, "true low"]).reset_index(drop=True)
    p, y = z[col].to_numpy(bool), z["true low"].to_numpy()
    n = len(z)
    if p.sum() == 0 or (~p).sum() == 0 or n < 25:
        return {"n": n, "testable": False}
    obs = y[p].mean() - y[~p].mean()
    offs = np.arange(10, n - 9)
    null = np.array([(lambda q: y[q].mean() - y[~q].mean())(np.roll(p, o)) for o in offs])
    pv = (np.sum(np.abs(null) >= abs(obs)) + 1) / (len(offs) + 1)
    return {"n": n, "on": int(p.sum()), "off": int((~p).sum()), "P(true | on)": float(y[p].mean()), "P(true | off)": float(y[~p].mean()),
            "difference": float(obs), "p": float(pv), "smallest possible p": float(1 / (len(offs) + 1)),
            "burst10 | on": float(np.nanmean(z.burst10.to_numpy()[p])), "burst10 | off": float(np.nanmean(z.burst10.to_numpy()[~p])),
            "testable": True}


def figure(R):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, axs = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"wspace": 0.42})
    for ax, key, title in ((axs[0], "a", "(a) Entering AT a new 20-day closing low"), (axs[1], "b", "(b) Entering after the first 1-ATR bounce off it")):
        r = R[key]
        labels, vals, ns, cols = [f"all candidates"], [100 * r["base"]], [r["n"]], [MUTED]
        for col, on, off in (("D", "RSI divergence (higher RSI low)", "no divergence"), ("L", "RSI in its bottom tenth", "RSI not that low"),
                             ("S", "options setup on (2021+)", "setup off (2021+)")):
            t = r[col]
            if not t.get("testable"):
                continue
            labels += [on, off]
            vals += [100 * t["P(true | on)"], 100 * t["P(true | off)"]]
            ns += [t["on"], t["off"]]
            cols += [BLUE, "#9db9e6"]
        y = np.arange(len(labels))[::-1]
        ax.barh(y, vals, color=cols, height=0.62)
        for yy, v, n in zip(y, vals, ns):
            ax.text(v + 1, yy, f"{v:.0f}%  (n={n})", va="center", fontsize=8, color=INK)
        ax.set_yticks(y, labels, fontsize=8.5)
        ax.set_xlim(0, 100)
        ax.axvline(100 * r["base"], color=MUTED, ls=":", lw=1)
        ax.set_xlabel("% of candidate lows that held for the next 10 sessions")
        d = r["D"]
        ax.set_title(f"{title}\nheld {100 * r['base']:.0f}% of the time; divergence {d['difference'] * 100:+.0f} pts (p {d['p']:.2f})",
                     loc="left", fontsize=9.5, color=INK)
        ax.set_axisbelow(True)
        ax.grid(axis="x", color=GRID)
    f.suptitle(R["headline"], x=0.01, ha="left", fontsize=11, color=INK, weight="bold", y=1.03)
    f.savefig(I.OUT / "followup_false_lows.png", dpi=150, bbox_inches="tight", facecolor=SURF)


def main():
    D = frame()
    A, B = candidates(D)
    R = {}
    for key, C in (("a", A), ("b", B)):
        C = C.dropna(subset=["true low"])
        R[key] = {"n": len(C), "base": float(C["true low"].mean()), "burst10 base": float(np.nanmean(C.burst10)),
                  "D": test(C, "D"), "L": test(C, "L"), "S": test(C, "S")}
        R[key]["D passes (p < 0.025, positive)"] = bool(R[key]["D"].get("testable") and R[key]["D"]["p"] < ALPHA and R[key]["D"]["difference"] > 0)
        print(f"({key}) candidates {len(C)}; D smallest possible p {R[key]['D'].get('smallest possible p')}", flush=True)
    ok = R["a"]["D passes (p < 0.025, positive)"] or R["b"]["D passes (p < 0.025, positive)"]
    R["headline"] = ("TSLA: RSI " + ("does" if ok else "doesn't") + " reliably separate true lows from false ones; the bounce itself is the filter: "
                     f"a new 20-day low holds {100 * R['a']['base']:.0f}% of the time, after a 1-ATR bounce {100 * R['b']['base']:.0f}%")
    (I.OUT / "followup_false_lows.json").write_text(json.dumps(R, indent=1, default=float))
    figure(R)
    return R


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=lambda v: round(float(v), 4)))
