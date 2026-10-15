"""edge_lab: how big must an edge be before this repository's backtest method can see it? (REPORT 4ad)
Planted-truth and acceptance-gate protocols from BootLoops (github.com/BootLoops-ai/skills), applied
to the TSLA burst pipeline. The controls and pass criteria were frozen in edge_lab_controls.md
(committed before this file ran); this script runs exactly that battery and prints counts with denominators.
Usage: python edge_lab.py [--quick]      -> out/edge_lab.json, out/edge_lab_power.csv, out/edge_lab.png
       (--quick: 20 replicates, about 10 seconds, writes the same files with a _quick suffix)
"""
import json
import sys

import numpy as np
import pandas as pd

from burst_gamma import state
from common import OUT, load_bars
from stock_gamma import START, frame
from stock_now import burst_days

QUICK = "--quick" in sys.argv
TAG = "_quick" if QUICK else ""        # a quick run never overwrites the full results
NSHIFT, MINSHIFT = 1000, 60
REPS = {"P1": 400, "P2": 400, "P3": 200, "P4": 300}
if QUICK:
    REPS = {k: 20 for k in REPS}
JUMP = np.log(1.06)
RNG = np.random.default_rng(20261014)


# ---------- production path (same logic as tsla_live.ladder / §4w) ----------
def marks(close, sign=1):
    return pd.Series(burst_days(close, sign), index=close.index)


def outcome(mk, idx, h, same_day=False):
    s = mk if same_day else mk.shift(-1)
    return s[::-1].rolling(h, min_periods=h).max()[::-1].reindex(idx).to_numpy(float)


def marks_nodedupe(close):
    """Diagnostic only (P3 fired): burst_days without its 3-day de-duplication."""
    rr, r2 = np.log(close).diff(), np.log(close / close.shift(2))
    hit = ((rr >= 0.05) | (r2 >= 0.09)).to_numpy()
    out = np.zeros(len(close), bool)
    for i in np.where(hit)[0]:
        out[i - 1 if (r2.iloc[i] >= 0.09 and rr.iloc[i] < 0.05) else i] = True
    return pd.Series(out, index=close.index)


def edge_test(sig, y, rng, minshift=MINSHIFT, nshift=NSHIFT, iid_null=False):
    ok = ~np.isnan(y)
    s, yy = np.asarray(sig, bool)[ok], y[ok]
    n = len(yy)
    if s.sum() == 0:
        return {"n_days": 0, "episodes": 0, "lift": None, "p": None}
    base = yy.mean()
    lift = yy[s].mean() - base
    pos = np.where(s)[0]
    if iid_null:      # F1 break: random days, persistence ignored
        null = np.array([yy[rng.choice(n, len(pos), replace=False)].mean() for _ in range(nshift)]) - base
    else:
        shifts = rng.integers(minshift, n - minshift, nshift)
        null = yy[(pos[None, :] + shifts[:, None]) % n].mean(axis=1) - base
    p = float(np.mean(null >= lift))
    eps = int((s & ~np.r_[False, s[:-1]]).sum())
    return {"n_days": int(s.sum()), "episodes": eps, "lift": float(lift), "p": p}


# ---------- independent implementation for expectations (explicit loop, no de-duplication) ----------
def simple_outcome(r, idx_pos, h):
    """r: log returns on the close index; idx_pos: positions of analysis days in that index."""
    n = len(r)
    hit = np.zeros(n, bool)
    for i in range(1, n):
        if r[i] >= 0.05:
            hit[i] = True
        elif r[i] + r[i - 1] >= 0.09:
            hit[i - 1] = True
    out = np.full(len(idx_pos), np.nan)
    for k, t in enumerate(idx_pos):
        if t + h < n:
            out[k] = float(hit[t + 1:t + h + 1].any())
    return out


def load():
    x = frame("TSLA").join(state("TSLA")[["near_pct"]])
    x = x[x.index >= START].dropna(subset=["near_pct"])
    c = load_bars("TSLA").close
    c = c[c.index >= x.index[0] - pd.Timedelta(days=10)]
    x = x[x.index.isin(c.index)]
    sig = ((x.near_pct <= 1 / 3) & x.below.astype(bool)).to_numpy()
    freed = (x.near_pct <= 1 / 3).to_numpy()
    pos = c.index.get_indexer(x.index)
    return x, c, sig, freed, pos


def rebuild(c0, r):
    return pd.Series(c0.iloc[0] * np.exp(np.r_[0.0, np.cumsum(r[1:])]), index=c0.index)


def plant(r, pos, sig, q, rng, ks=(1, 2, 3)):
    r2 = r.copy()
    for t in pos[sig]:
        if rng.random() < q:
            j = t + rng.choice(ks)
            if j < len(r2):
                r2[j] = max(r2[j], JUMP)
    return r2


def shifted(sig, rng, lo=120):
    return np.roll(sig, int(rng.integers(lo, len(sig) - lo)))


def spaced_events(n, k, gap, rng, margin=15):
    while True:
        e = np.sort(rng.choice(np.arange(margin, n - margin), k, replace=False))
        if np.all(np.diff(e) >= gap):
            s = np.zeros(n, bool)
            s[e] = True
            return s


def stationary_bootstrap(r, rng, mean_block=20):
    n, out, i = len(r), [], int(rng.integers(len(r)))
    while len(out) < n:
        out.append(r[i])
        i = int(rng.integers(n)) if rng.random() < 1 / mean_block else (i + 1) % n
    return np.array(out)


def main():
    x, c, sig, freed, pos = load()
    idx = x.index
    r = np.r_[0.0, np.diff(np.log(c.to_numpy()))]
    y3 = outcome(marks(c), idx, 3)
    res = {"denominators": {"analysis days": int(len(idx)), "freed&below days": int(sig.sum()), "freed days": int(freed.sum())}}

    # reproduction of the published number through this entry point (§4w: +22.8 pts)
    real = edge_test(sig, y3, RNG)
    res["real freed&below, up-burst in 3"] = real
    res["real freed only, up-burst in 3"] = edge_test(freed, y3, RNG)

    # N1-N3 machinery nulls
    res["N1 all-False signal"] = edge_test(np.zeros(len(idx), bool), y3, RNG)
    res["N2 all-True signal lift"] = edge_test(np.ones(len(idx), bool), y3, RNG)["lift"]
    res["N3 all-zero outcome lift"] = edge_test(sig, np.where(np.isnan(y3), np.nan, 0.0), RNG)["lift"]

    # P1 shift-null calibration (+ F1 wrong-way p must break it)
    fp, fp_wrong = [], []
    for _ in range(REPS["P1"]):
        s = shifted(sig, RNG)
        fp.append(edge_test(s, y3, RNG)["p"] < 0.05)
        fp_wrong.append(edge_test(s, y3, RNG, iid_null=True, nshift=300)["p"] < 0.05)
    res["P1 false-positive rate"] = {"rate": float(np.mean(fp)), "n": len(fp), "pass": bool(0.025 <= np.mean(fp) <= 0.08)}
    res["F1 iid null breaks P1"] = {"rate": float(np.mean(fp_wrong)), "check fails as it should": bool(not (0.025 <= np.mean(fp_wrong) <= 0.08))}

    # P2 bootstrap-null calibration
    fp2 = []
    for _ in range(REPS["P2"]):
        rb = stationary_bootstrap(r, RNG)
        cb = rebuild(c, rb)
        fp2.append(edge_test(sig, outcome(marks(cb), idx, 3), RNG)["p"] < 0.05)
    res["P2 false-positive rate"] = {"rate": float(np.mean(fp2)), "n": len(fp2), "pass": bool(0.025 <= np.mean(fp2) <= 0.08)}

    # P3 plant recovery (+ F2 a plant that can land on day t must miss)
    p3 = {}
    for q in (0.1, 0.2, 0.3):
        got, exp_, got_bad = [], [], []
        for _ in range(REPS["P3"]):
            s = shifted(sig, RNG)
            seed = int(RNG.integers(1 << 30))
            r2 = plant(r, pos, s, q, np.random.default_rng(seed))
            got.append(edge_test(s, outcome(marks(rebuild(c, r2)), idx, 3), RNG)["lift"])
            ys = simple_outcome(r2, pos, 3)
            exp_.append(np.nanmean(ys[s]) - np.nanmean(ys))
            rb = plant(r, pos, s, q, np.random.default_rng(seed), ks=(0, 1, 2))
            got_bad.append(edge_test(s, outcome(marks(rebuild(c, rb)), idx, 3), RNG)["lift"])
        d = float(np.mean(got) - np.mean(exp_))
        p3[str(q)] = {"recovered": float(np.mean(got)), "expected": float(np.mean(exp_)), "diff": d, "pass": bool(abs(d) <= 0.02),
                      "F2 broken plant diff": float(np.mean(got_bad) - np.mean(exp_)),
                      "F2 check fails as it should": bool(abs(np.mean(got_bad) - np.mean(exp_)) > 0.02)}
    res["P3 plant recovery"] = p3

    # P3 fired: diagnosis recorded alongside, criteria unchanged
    diag = {}
    for q in (0.1, 0.3):
        g1, g0, ex = [], [], []
        for _ in range(REPS["P3"] // 2):
            s = shifted(sig, RNG)
            r2 = plant(r, pos, s, q, RNG)
            c2 = rebuild(c, r2)
            g1.append(edge_test(s, outcome(marks(c2), idx, 3), RNG)["lift"])
            g0.append(edge_test(s, outcome(marks_nodedupe(c2), idx, 3), RNG)["lift"])
            ys = simple_outcome(r2, pos, 3)
            ex.append(np.nanmean(ys[s]) - np.nanmean(ys))
        diag[str(q)] = {"expected": float(np.mean(ex)), "production": float(np.mean(g1)), "production without de-dup": float(np.mean(g0))}
    yn = outcome(marks_nodedupe(c), idx, 3)
    diag["real TSLA big days hidden by de-dup"] = f"{int(marks_nodedupe(c).loc[idx[0]:].sum() - marks(c).loc[idx[0]:].sum())} of {int(marks_nodedupe(c).loc[idx[0]:].sum())}"
    diag["real freed&below without de-dup"] = edge_test(sig, yn, RNG)
    res["P3 diagnosis (after it fired)"] = diag

    # P4 power curves
    rows = []
    profiles = {"a: freed & below flip (real persistence), 3 sessions": (sig, 3, (1, 2, 3)),
                "b: freed (real persistence), 3 sessions": (freed, 3, (1, 2, 3)),
                "c: 7 hand-picked events, 10 sessions": (None, 10, tuple(range(1, 11)))}
    for name, (base_sig, h, ks) in profiles.items():
        for q in (0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.45):
            det, lifts, exps = [], [], []
            for _ in range(REPS["P4"]):
                s = shifted(base_sig, RNG) if base_sig is not None else spaced_events(len(idx), 7, 60, RNG)
                r2 = plant(r, pos, s, q, RNG, ks=ks)
                out = edge_test(s, outcome(marks(rebuild(c, r2)), idx, h), RNG)
                det.append(out["p"] < 0.05)
                lifts.append(out["lift"])
                ys = simple_outcome(r2, pos, h)
                exps.append(np.nanmean(ys[s]) - np.nanmean(ys))
            rows.append({"profile": name, "q": q, "true lift (pts)": 100 * float(np.mean(exps)), "detected %": 100 * float(np.mean(det)),
                         "recovered lift (pts)": 100 * float(np.mean(lifts)), "reps": len(det)})
    pw = pd.DataFrame(rows)
    pw.to_csv(OUT / f"edge_lab_power{TAG}.csv", index=False)
    mdl = {}
    for name, g in pw.groupby("profile", sort=False):
        g = g.sort_values("true lift (pts)")
        above = g[g["detected %"] >= 80]
        mdl[name] = float(np.interp(80, g["detected %"], g["true lift (pts)"])) if len(above) else None
    res["P4 lift detected 80% of the time (pts)"] = mdl

    # C1 same-day timing leak: dip-triggered signal, down-bursts
    dip = (pd.Series(r, index=c.index).reindex(idx) <= -0.04).to_numpy()
    dn = marks(c, -1)
    leak = edge_test(dip, outcome(dn, idx, 3, same_day=True), RNG)
    clean = edge_test(dip, outcome(dn, idx, 3), RNG)

    def detector(pipeline):
        return bool(pipeline["lift"] - clean["lift"] > 0.05 and clean["p"] >= 0.05)
    res["C1 timing leak"] = {"leaky lift": leak["lift"], "leaky p": leak["p"], "forward lift": clean["lift"], "forward p": clean["p"],
                             "detector on leaky": detector(leak), "detector on clean": detector(clean),
                             "pass": bool(detector(leak) and not detector(clean))}

    # C2 week-start dates read as event days
    nw = pd.read_csv(OUT / "named_weeks_TSLA.csv", parse_dates=["date"])
    actual = nw[nw.biggest_in_move].date
    weekstart = [nw[nw.week_of == w].date.min() for w in nw[nw.biggest_in_move].week_of]
    share = lambda ds: pd.Series(pd.DatetimeIndex(ds).day_name()).value_counts(normalize=True).iloc[0]
    res["C2 date convention"] = {"actual max weekday share": float(share(actual)), "week-start max weekday share": float(share(weekstart)),
                                 "detector on week-start": bool(share(weekstart) >= 0.9), "detector on actual": bool(share(actual) >= 0.9),
                                 "pass": bool(share(weekstart) >= 0.9 and share(actual) < 0.9), "n dates": int(len(actual))}

    # gate on the real result
    a = next(k for k in mdl if k.startswith("a:"))
    thr = mdl[a]
    res["gate: real freed&below"] = {"lift pts": 100 * real["lift"], "p": real["p"], "80%-power lift pts": thr,
                                     "verdict": "robust" if (thr is not None and 100 * real["lift"] > thr and real["p"] < 0.05) else "unresolved"}
    (OUT / f"edge_lab{TAG}.json").write_text(json.dumps(res, indent=1, default=float))
    return res, pw


def figure(res, pw):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    C = {"a": "#2a78d6", "b": "#1baf7a", "c": "#eb6834"}
    INK, MUTED, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "legend.frameon": False})
    f, a = plt.subplots(figsize=(10.5, 6))
    for name, g in pw.groupby("profile", sort=False):
        k = name[0]
        g = g.sort_values("true lift (pts)")
        a.plot(g["true lift (pts)"], g["detected %"], marker="o", color=C[k], lw=2.2, label=name)
    a.axhline(80, color=MUTED, lw=1, ls="--")
    a.axhline(5, color=MUTED, lw=1, ls=":")
    a.annotate("80% detection", (0.5, 81.5), fontsize=8, color=MUTED)
    a.annotate("5% = luck's false alarms", (26, 6.5), fontsize=8, color=MUTED)
    g = res["gate: real freed&below"]
    a.axvline(g["lift pts"], color=C["a"], lw=1.4, ls=":")
    a.annotate(f"real freed & below flip:\n+{g['lift pts']:.1f} pts", (g["lift pts"], 40), xytext=(5, 0), textcoords="offset points",
               fontsize=8.5, color=C["a"])
    a.set_xlabel("true planted edge: extra probability of an up-burst after the signal (percentage points)")
    a.set_ylabel("% of planted tests the method flags (p < 0.05)")
    a.set_ylim(0, 102)
    a.legend(loc="lower right", fontsize=8.5)
    m = res["P4 lift detected 80% of the time (pts)"]
    fmt = lambda v: "not reached" if v is None else f"+{v:.0f} pts"
    a.set_title("How big must an edge be before a TSLA backtest can see it?  (planted-truth power curves, BootLoops protocol)\n"
                f"80% detection needs: signal like freed & below flip {fmt(m[next(k for k in m if k.startswith('a:'))])}, "
                f"like freed {fmt(m[next(k for k in m if k.startswith('b:'))])}, "
                f"7 hand-picked events {fmt(m[next(k for k in m if k.startswith('c:'))])}", loc="left", fontsize=10, color=INK)
    f.tight_layout()
    f.savefig(OUT / f"edge_lab{TAG}.png", dpi=150)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    res, pw = main()
    print(json.dumps({k: v for k, v in res.items()}, indent=1, default=float))
    print(pw.round(1).to_string(index=False))
    if not QUICK:
        figure(res, pw)
        print("saved", OUT / f"edge_lab{TAG}.png")
