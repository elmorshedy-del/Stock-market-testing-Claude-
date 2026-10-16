"""Follow-up C (pre-registered in README.md at 437b6dc, amended before any run at d9e41d9): TSLA indicators split
by the higher-timeframe regime. Regime = 52-week efficiency ratio vs its own expanding median (range = at or below);
alternates: weekly ADX vs its expanding median, flat SMA(40) slope vs its expanding median. No rule-of-thumb thresholds.
Usage: OMP_NUM_THREADS=1 python followup_regimes.py [--regimes]
       -> out/followup_regimes.csv, out/followup_regimes.json, out/followup_regimes.png
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

import followup_false_lows as FB
import followup_rsi_lows as FA
import indicators as I

sys.path.insert(0, str(I.MICRO))
from own_multiverse import within                  # noqa: E402
from stock_now import burst_days                   # noqa: E402

SYM, ALPHA = "TSLA", 0.05 / 6
OSC, TREND = ("RSI", "%B", "Stochastic"), ("Momentum", "Trend distance", "MACD", "ADX")
BLUE, ORANGE, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
CMAP = LinearSegmentedColormap.from_list("div", [BLUE, "#bcd3f0", "#efeeea", "#f6c7b0", ORANGE])
RNG = np.random.default_rng(20261018)


def regimes():
    b = I.bars(I.load(SYM), "W-FRI")
    lc = np.log(b.close)
    er = (lc - lc.shift(52)).abs() / lc.diff().abs().rolling(52).sum()
    raw = I.indicators(b, 40)
    sma = b.close.rolling(40).mean()
    slope = (sma - sma.shift(13)).abs() / (raw["ATR%"] * b.close)
    xp = lambda s: s.expanding(min_periods=156).rank(pct=True)
    R = pd.DataFrame({"close": b.close, "ER pct": xp(er), "primary": xp(er) <= 0.5, "alt ADX": xp(raw.ADX) <= 0.5,
                      "alt SMA slope": xp(slope) <= 0.5})
    return R[R["ER pct"].notna()]


def to_daily(R, idx):
    return {k: R[k].astype(float).reindex(R.index.union(idx)).ffill().reindex(idx).shift(1) for k in ("primary", "alt ADX", "alt SMA slope")}


def regime_tests():
    R = regimes()
    rows, fam = [], {}
    for tf in ("daily", "weekly"):
        p = I.TFS[tf]
        b, raw, pct, Rt = I.frame(SYM, tf)
        G = to_daily(R, Rt.index) if tf == "daily" else {k: R[k].astype(float).reindex(Rt.index) for k in ("primary", "alt ADX", "alt SMA slope")}
        ok = pct.notna().all(axis=1) & Rt.notna() & G["primary"].notna()
        P, r = pct[ok].to_numpy().T, Rt[ok].to_numpy()
        up, dn = (r >= np.quantile(r, 0.8)).astype(float), (r <= np.quantile(r, 0.2)).astype(float)
        hi, lo = (P >= 2 / 3).astype(float), (P <= 1 / 3).astype(float)
        g = {k: v[ok].to_numpy().astype(bool) for k, v in G.items()}

        def block(h, l, rg):
            a = I.stats(h[:, rg], l[:, rg], r[rg], up[rg], dn[rg])
            bb = I.stats(h[:, ~rg], l[:, ~rg], r[~rg], up[~rg], dn[~rg])
            return {"range": a, "trend": bb, "interaction": a - bb}

        real = block(hi, lo, g["primary"])
        alts = {k: block(hi, lo, g[k]) for k in ("alt ADX", "alt SMA slope")}
        offs = I.offsets(len(r), p)
        nulls = [block(np.roll(hi, o, 1), np.roll(lo, o, 1), g["primary"]) for o in offs]
        for fname in ("range", "trend", "interaction"):
            obs = real[fname]
            null = np.stack([n_[fname] for n_ in nulls])
            mu, sd = null.mean(0), null.std(0)
            z, zn = (obs - mu) / sd, (null - mu) / sd
            fz, fzn = np.abs(z).ravel(), np.abs(zn).reshape(len(offs), -1)
            raw_p = ((fzn >= fz).sum(0) + 1) / (len(offs) + 1)
            order, adj, run = np.argsort(-fz), np.empty_like(fz), 0.0
            for i, k in enumerate(order):
                run = max(run, (np.sum(fzn[:, order[i:]].max(1) >= fz[k]) + 1) / (len(offs) + 1))
                adj[k] = run
            fam[f"{tf} {fname}"] = float((np.sum(fzn.max(1) >= fz.max()) + 1) / (len(offs) + 1))
            for i, ind in enumerate(I.IND):
                for j, st in enumerate(I.STATS):
                    k = i * 3 + j
                    same = all(np.sign(alts[a][fname][i, j]) == np.sign(obs[i, j]) for a in alts)
                    rows.append({"timeframe": tf, "family": fname, "indicator": ind, "statistic": st, "value": obs[i, j], "z": z[i, j],
                                 "p raw": raw_p[k], "p family (step-down)": adj[k], "alt ADX": alts["alt ADX"][fname][i, j],
                                 "alt SMA slope": alts["alt SMA slope"][fname][i, j], "same sign both alternates": bool(same),
                                 "n range": int(g["primary"].sum()), "n trend": int((~g["primary"]).sum()), "null draws": len(offs)})
    T = pd.DataFrame(rows)
    T["survivor"] = T["p family (step-down)"] < ALPHA
    T["robust"] = T.survivor & T["same sign both alternates"]
    T["hypothesis"] = T.apply(hyp, axis=1)
    return T, fam, R


def hyp(r):
    if r.family == "range" and r.indicator in OSC:
        if r.statistic.startswith("S2"):
            return "matches H-range" if r.value < 0 else "contradicts H-range"
        if r.statistic.startswith("S3"):
            return "matches H-range" if r.value > 0 else "contradicts H-range"
    if r.family == "trend" and r.indicator in TREND and r.statistic.startswith("S2"):
        return "matches H-trend" if r.value > 0 else "contradicts H-trend"
    return ""


def secondary(R):
    D = FA.data()
    D = D[D.index >= "2010-08-01"]
    D["range"] = to_daily(R, D.index)["primary"]
    out = {}
    ok = D.burst10.notna() & D.range.notna() & D.rsi_pct.notna()
    low = D.rsi_pct <= 0.10
    for lab, rg in (("range", D.range == 1), ("trend", D.range == 0)):
        m = ok & rg
        s, y = low[m].to_numpy(), D.burst10[m].to_numpy()
        obs = y[s].mean() - y.mean()
        full_low, idx = low.to_numpy(), np.where(m.to_numpy())[0]
        null = [D.burst10.to_numpy()[idx][np.roll(full_low, o)[idx]].mean() - y.mean() for o in RNG.choice(np.arange(60, len(D) - 59), 1000)]
        out[f"RSI bottom tenth -> up-burst within 10, {lab}"] = {"days": int(s.sum()), "P | RSI low": float(y[s].mean()), "P | regime": float(y.mean()),
                                                                  "difference": float(obs), "p": float((np.sum(np.abs(null) >= abs(obs)) + 1) / 1001)}
    S = I.setups()["TSLA"]
    x = D.join(S[["setup"]], how="inner")
    x = x[x.index >= "2021-01-01"]
    x["up3"] = within(x.burst.to_numpy(), 3)
    for lab, rg in (("range", x.range == 1), ("trend", x.range == 0)):
        m = rg & x.up3.notna()
        z = x[m]
        out[f"options full setup -> up-burst within 3 (2021+), {lab}"] = {
            "setup days": int(z.setup.sum()), "episodes": FA.I.episodes(z.setup.to_numpy()) if len(z) else 0,
            "P | setup": float(z.up3[z.setup].mean()), "P | no setup": float(z.up3[~z.setup].mean())}
    Fd = FB.frame()
    A, _ = FB.candidates(Fd)
    A = A.dropna(subset=["true low"])
    rg = D.range.reindex(Fd.date.iloc[A.day].to_numpy()).to_numpy()
    for lab, v in (("range", 1.0), ("trend", 0.0)):
        m = rg == v
        out[f"new 20-session closing low held 10 sessions, {lab}"] = {"candidates": int(m.sum()), "held": float(A["true low"].to_numpy()[m].mean())}
    return out


def figure(T, R, sec, fam):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f = plt.figure(figsize=(16, 10.5))
    gs = f.add_gridspec(2, 3, height_ratios=[0.8, 1.2], hspace=0.42, wspace=0.32)
    a = f.add_subplot(gs[0, :])
    a.semilogy(R.index, R.close, color=INK, lw=1.4)
    rg = R.primary.astype(bool)
    for d, on in rg.items():
        if on:
            a.axvspan(d - pd.Timedelta(days=3.5), d + pd.Timedelta(days=3.5), color=BLUE, alpha=0.13, lw=0)
    a.plot([], [], color=BLUE, alpha=0.3, lw=8, label="range regime (52-week efficiency at or below its own median, known in real time)")
    a.legend(loc="upper left", frameon=False, fontsize=8.5)
    a.set_ylabel("TSLA weekly close (log)")
    a.set_title("1. The regime as it was known at the time: ranges in 2015-16, 2018-19, 2022-24 and now; trends in 2017, 2020-21 and 2025",
                loc="left", fontsize=10, color=INK)
    for k, (tf, st, title) in enumerate((("daily", "S2", "2. Entry, daily bars: big up moves,\nindicator high minus low"),
                                          ("weekly", "S2", "3. Entry, weekly bars"), ("daily", "S3", "4. Exit, daily bars: big down moves"))):
        ax = f.add_subplot(gs[1, k])
        cols = ["range", "trend", "interaction"]
        M = np.full((len(I.IND), 3), np.nan)
        for j, fname in enumerate(cols):
            for i, ind in enumerate(I.IND):
                r = T[(T.timeframe == tf) & (T.family == fname) & (T.indicator == ind) & T.statistic.str.startswith(st)].iloc[0]
                M[i, j] = r.z
                ax.text(j, i, f"{r.z:+.1f}", ha="center", va="center", fontsize=8, color=SURF if abs(r.z) >= 3 else INK)
                if r.robust:
                    ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, ec=INK, lw=2.4))
        im = ax.imshow(np.clip(M, -4, 4), cmap=CMAP, vmin=-4, vmax=4, aspect="auto")
        ax.set_xticks(range(3), [f"{c}\nfamily p {fam[f'{tf} {c}']:.3f}" for c in cols], fontsize=8)
        ax.set_yticks(range(len(I.IND)), I.IND, fontsize=8.5)
        ax.tick_params(length=0)
        for s_ in ax.spines.values():
            s_.set_visible(False)
        ax.set_title(title, loc="left", fontsize=9.5, color=INK)
    cb = f.colorbar(im, cax=ax.inset_axes([1.05, 0, 0.05, 1]))
    cb.set_label("z vs the shift null; box = survives, same sign under both alternate regime gauges", fontsize=8)
    f.suptitle(R.attrs.get("headline", ""), x=0.01, ha="left", fontsize=11, color=INK, weight="bold", y=0.995)
    f.savefig(I.OUT / "followup_regimes.png", dpi=150, bbox_inches="tight", facecolor=SURF)


def main():
    if "--regimes" in sys.argv:
        R = regimes()
        R["year"] = R.index.year
        print(R.groupby("year")[["primary", "alt ADX", "alt SMA slope"]].mean().round(2).to_string())
        return None
    T, fam, R = regime_tests()
    sec = secondary(R)
    rob = T[T.robust]
    R.attrs["headline"] = (f"TSLA indicators by regime: {len(rob)} robust survivor(s) of {len(T)} statistics"
                           + (": " + "; ".join(f"{r.timeframe} {r.indicator} {r.statistic.split(' ')[0]} in {r.family} ({r.hypothesis or 'no hypothesis'})"
                                               for _, r in rob.iterrows()) if len(rob) else "; splitting by regime does not uncover a reliable signal"))
    T.to_csv(I.OUT / "followup_regimes.csv", index=False)
    res = {"family p (single-step)": fam, "survivors": int(T.survivor.sum()), "robust": rob.drop(columns=["n range", "n trend"]).to_dict("records"),
           "secondary": sec, "headline": R.attrs["headline"],
           "regime now (week of " + str(R.index[-1].date()) + ")": "range" if R.primary.iloc[-1] else "trend"}
    (I.OUT / "followup_regimes.json").write_text(json.dumps(res, indent=1, default=float))
    figure(T, R, sec, fam)
    return T, res


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    out = main()
    if out:
        T, res = out
        cols = ["timeframe", "family", "indicator", "statistic", "value", "z", "p raw", "p family (step-down)", "alt ADX", "alt SMA slope", "survivor", "robust", "hypothesis"]
        print(T.reindex(T.z.abs().sort_values(ascending=False).index)[cols].head(20).round(4).to_string(index=False))
        print(json.dumps({k: v for k, v in res.items() if k != "robust"}, indent=1, default=lambda v: round(float(v), 4)))
