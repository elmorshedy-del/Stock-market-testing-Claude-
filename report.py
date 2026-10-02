"""Build figures + numbers for REPORT.md (run backtest.py first)."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import options_flow as of
from channels import detect, ou_halflife, touches
from common import OUT, load_bars
from flow_intraday import anchored_vwap, ma_lag_check, summary as flow_summary

C1, C2, C3, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
                     "legend.frameon": False})


def channel_fig(daily, ch, nums):
    t = np.arange(len(daily) + 60, dtype=float)
    fut = pd.bdate_range(daily.index[-1], periods=61)[1:]
    idx = daily.index.append(fut)
    lo, mid, up = ch.lines(t)
    s = ch.start - 40
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.set_yscale("log")
    ax.vlines(daily.index[s:], daily.low[s:], daily.high[s:], color=MUTED, lw=0.6)
    ax.plot(daily.index[s:], daily.close[s:], color=INK, lw=1, label="MU close")
    for y, lab in ((up, "upper"), (mid, "mid"), (lo, "lower")):
        ax.plot(idx[ch.start:], y[ch.start:], color=C1, lw=2, alpha=0.85)
        ax.annotate(f"{lab} {y[len(daily)-1]:,.0f}", (idx[-1], y[-1]), color=C1, fontsize=8, va="center")
    sma50 = daily.close.rolling(50).mean()
    ax.plot(daily.index[s:], sma50[s:], color=C2, lw=1.5, label="50-day SMA")
    av = anchored_vwap(daily, daily.index[ch.start])
    ax.plot(av.index, av, color=C3, lw=1.5, label="VWAP anchored at channel low")
    up_t, dn_t = touches(ch, daily, tol=0.0)
    ax.scatter(daily.index[up_t], daily.high.iloc[up_t], s=10, color=C1, zorder=3)
    ax.scatter(daily.index[dn_t], daily.low.iloc[dn_t], s=10, color=C1, zorder=3, label="bars piercing a line")
    ax.set_title(f"MU auto-detected log channel  (anchor {daily.index[ch.start].date()}, "
                 f"{100*ch.annual_growth():.0f}%/yr, width {100*(np.exp(ch.hi-ch.lo)-1):.0f}%, R² {ch.r2:.3f})",
                 loc="left", color=INK)
    ax.legend(loc="upper left")
    ax.set_ylabel("price (log scale)")
    fig.tight_layout()
    fig.savefig(OUT / "fig_channel.png", dpi=150)


def gex_fig(res, df, S, ch_today):
    near = df[df["T"] * 365 <= 45]
    e = of.exposures(near, S, "classic")
    by = e.groupby("K").gex.sum() / 1e6
    by = by[(by.index > 0.8 * S) & (by.index < 1.3 * S)]
    fig, (a, b) = plt.subplots(2, 1, figsize=(9, 6.4))
    a.bar(by.index, by.values, width=4, color=np.where(by.values >= 0, C1, C2))
    a.set_title("Dealer GEX by strike, expiries ≤45d, classic convention ($M per 1% move)", loc="left", color=INK)
    for v, lab in zip(ch_today, ("lower", "mid", "upper")):
        a.axvline(v, color=MUTED, ls="--", lw=1); a.text(v, a.get_ylim()[1] * 0.9, f" {lab}", color=MUTED, fontsize=8)
    a.axvline(S, color=INK, lw=1); a.text(S, a.get_ylim()[1] * 0.75, " spot", color=INK, fontsize=8)
    for conv, col in (("classic", C1), ("short", C2)):
        g, tot = res[conv]["profile"]
        b.plot(g, np.array(tot) / 1e9, color=col, lw=2,
               label="dealers long calls / short puts" if conv == "classic" else "dealers short calls and puts")
    b.axhline(0, color=MUTED, lw=0.8)
    b.axvline(S, color=INK, lw=1)
    for f in res["classic"]["gamma_flips"]:
        b.axvline(f, color=C1, ls=":", lw=1.2); b.text(f, b.get_ylim()[0] * 0.8, f" flip {f:,.0f}", color=C1, fontsize=8)
    for v in ch_today:
        b.axvline(v, color=MUTED, ls="--", lw=1)
    b.set_title("Total dealer GEX if spot moved there (all expiries, sticky strike, $B per 1%)", loc="left", color=INK)
    b.set_xlabel("MU price")
    b.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "fig_gex.png", dpi=150)


def flow_fig(m5, prof, levels):
    centers, vol = prof
    poc, val, vah = levels
    fig = plt.figure(figsize=(9, 6))
    gs = fig.add_gridspec(2, 2, width_ratios=[4, 1], height_ratios=[3, 2], hspace=0.25, wspace=0.05)
    a, p, c = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0])
    x = np.arange(len(m5))
    a.plot(x, m5.close, color=INK, lw=0.8)
    a.set_title("MU 5-minute closes, last 60 sessions, with 60-session volume profile", loc="left", color=INK)
    p.barh(centers, vol / 1e6, height=np.gradient(centers) * 0.9, color=C1)
    for v, lab in ((poc, "POC"), (val, "VAL"), (vah, "VAH")):
        a.axhline(v, color=C2 if lab == "POC" else MUTED, ls="--", lw=1)
        a.text(0, v, f" {lab} {v:,.0f}", color=C2 if lab == "POC" else MUTED, fontsize=8, va="bottom")
    lim = (m5.low.min() * 0.98, m5.high.max() * 1.02)
    a.set_ylim(lim); p.set_ylim(lim); p.set_yticklabels([]); p.set_xlabel("volume (M sh)")
    c.plot(x, m5.cvd / 1e6, color=C2, lw=1.2)
    c.set_title("Cumulative volume delta, bulk-volume classified (M shares)", loc="left", color=INK)
    days = m5.index.normalize()
    ticks = np.r_[0, np.where(days[1:] != days[:-1])[0] + 1][::10]
    for ax in (a, c):
        ax.set_xticks(ticks); ax.set_xticklabels([d.strftime("%b %d") for d in m5.index[ticks]])
    fig.savefig(OUT / "fig_flow.png", dpi=150, bbox_inches="tight")


def backtest_fig(bt):
    fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.6))
    real = {r["side"]: r["reject"] for r in bt["real"]}
    null = {r["side"]: r["reject"] for r in bt["null"]}
    labs = ["lower-line touch", "upper-line touch"]
    xs = np.arange(2)
    a.bar(xs - 0.2, [null[-1], null[1]], 0.38, color=MUTED, label="random null (block bootstrap)")
    a.bar(xs + 0.2, [real[-1], real[1]], 0.38, color=C1, label="real")
    ci = bt["reject_ci"]
    for k, s in enumerate(("-1", "1")):
        m, l, h = ci[s]
        a.errorbar(k + 0.2, m, yerr=[[m - l], [h - m]], color=INK, capsize=3, lw=1)
    a.set_xticks(xs, labs); a.set_ylabel("share rejected"); a.set_ylim(0, 0.6)
    a.set_title("Rejection rate at channel lines, 40 stocks", loc="left", color=INK); a.legend(loc="upper left", fontsize=7)
    qd = pd.DataFrame(bt["model_no_zclose"]["quintiles"])
    b.plot(qd.p, qd.break_rate, "o-", color=C1, lw=2, ms=6, label="out-of-sample 2021+")
    b.plot([0.2, 0.9], [0.2, 0.9], color=MUTED, lw=0.8, ls="--", label="perfect calibration")
    b.set_xlabel("predicted P(break)"); b.set_ylabel("realised break rate")
    b.set_title(f"Breakout model, AUC {bt['model_no_zclose']['auc_test']:.2f}", loc="left", color=INK)
    b.legend(loc="upper left", fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "fig_backtest.png", dpi=150)


if __name__ == "__main__":
    daily = load_bars("MU")
    ch = detect(daily, q=0.15)
    n = len(daily) - 1
    lo, mid, up = (float(v[0]) for v in ch.lines([n]))
    t = np.arange(ch.start, n + 1, dtype=float)
    resid = np.log(daily.close.to_numpy()[ch.start:]) - ch.mid(t)
    hl, phi = ou_halflife(resid)
    S = daily.close.iloc[-1]
    # days until the rising lower line passes today's price / key levels
    days_to = {lvl: float(np.log(lvl / lo) / ch.b) for lvl in (S, 1100, 1150, 1200)}
    res, chain = of.summary()
    fs, m5, prof, blk = flow_summary()
    bt = json.loads((OUT / "backtest.json").read_text())
    channel_fig(daily, ch, None)
    gex_fig(res, chain, res["spot"], (lo, mid, up))
    flow_fig(m5, prof, (fs["poc"], *fs["value_area"]))
    backtest_fig(bt)
    for conv in ("classic", "short"):
        res[conv].pop("profile")
    adv = float((daily.close * daily.volume).iloc[-20:].mean())
    nums = {
        "channel": {"anchor": str(daily.index[ch.start].date()), "growth_pct_yr": 100 * ch.annual_growth(),
                    "log_slope_per_day": ch.b, "width_pct": 100 * (np.exp(ch.hi - ch.lo) - 1), "r2": ch.r2,
                    "today_lower_mid_upper": (lo, mid, up), "z_close": float(ch.z(n, np.log(S))),
                    "resid_ar1_phi": phi, "resid_halflife_days": hl,
                    "trading_days_until_lower_line_reaches": days_to},
        "ma_lag": ma_lag_check(daily, ch),
        "options": res, "flow": fs,
        "adv_dollar_20d": adv, "gex_classic_as_pct_adv": 100 * res["classic"]["net_gex_per_1pct"] / adv,
    }
    (OUT / "report_numbers.json").write_text(json.dumps(nums, indent=1, default=str))
    print(json.dumps(nums["channel"], indent=1, default=str), nums["gex_classic_as_pct_adv"])
