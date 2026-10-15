"""Does a market bounce cap TSLA's drawdown? (REPORT 4ae, market-cap block)
Thesis: if SPY/QQQ are set up to rally (low S&P dealer gamma, dark-pool buying), TSLA's downside is capped,
because TSLA rarely falls hard while the market goes up.
  1. hindsight  TSLA over the next 10 sessions, split by what the S&P actually did over the same 10 sessions
  2. ex ante    S&P over the next 10 sessions, split by today's market readings (S&P gamma, DIX, SPY's own DPI)
  3. the live case  TSLA's full setup (freed and below its own flip) split by the market's readings at the start
All outcomes are strictly forward (t+1..t+10) from the day-t close. ^GSPC is used for the S&P (no dividend drops).
Usage: python market_cap.py      -> out/market_cap.csv, out/market_cap.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from burst_gamma import state
from common import OUT, load_bars
from finra_dpi import load as load_dpi
from forecast import build
from stock_gamma import START, frame
from stock_now import burst_days

H, END, DIP = 10, "2026-10-15", np.log(0.92)
C1, C2, C3, INK, MUTED, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#fcfcfb"


def data():
    t, s = load_bars("TSLA").close, load_bars("^GSPC").close
    idx = t.index.intersection(s.index)
    idx = idx[idx < END]
    t, s = t.reindex(idx), s.reindex(idx)
    lt, ls = np.log(t), np.log(s)
    path = lambda l: pd.concat([l.shift(-k) - l for k in range(1, H + 1)], axis=1)
    D = pd.DataFrame({"spx10": ls.shift(-H) - ls, "tsla10": lt.shift(-H) - lt, "tsla_dd": path(lt).min(axis=1), "spx_dd": path(ls).min(axis=1)})
    nx = lambda m: m.shift(-1)[::-1].rolling(H, min_periods=H).max()[::-1]
    D["tsla_dn"] = nx(pd.Series(burst_days(t, -1), index=idx))
    D["tsla_up"] = nx(pd.Series(burst_days(t, 1), index=idx))
    f = build()
    D["gex"], D["dix"] = f.gex_pct.reindex(idx), f.dix_pct.reindex(idx)
    dpi, _ = load_dpi()
    D["spy_dpi"] = dpi["SPY"].rolling(5).mean().rolling(252, min_periods=120).rank(pct=True).reindex(idx)
    x = frame("TSLA").join(state("TSLA")[["near_pct"]])
    x = x[(x.index >= START) & (x.index < END)]
    D["full"] = ((x.near_pct <= 1 / 3) & x.below.astype(bool)).reindex(idx).fillna(False).astype(bool)
    return D.loc["2015":].dropna(subset=["spx10", "tsla10"])


def summ(z):
    return {"days": len(z), "TSLA up-burst %": 100 * z.tsla_up.mean(), "TSLA down-burst %": 100 * z.tsla_dn.mean(),
            "TSLA worst dip %": 100 * z.tsla_dd.mean(), "TSLA dip worse than -8% %": 100 * (z.tsla_dd < DIP).mean(),
            "TSLA 10d %": 100 * z.tsla10.mean(), "S&P 10d %": 100 * z.spx10.mean(), "S&P up %": 100 * (z.spx10 > 0).mean()}


def tables(D):
    rally = D.spx10.quantile(2 / 3)
    q = pd.qcut(D.spx10, 3, labels=["S&P fell (bottom third)", "S&P flat (middle)", "S&P rallied (top third)"])
    t1 = pd.DataFrame({lab: summ(D[q == lab]) for lab in q.cat.categories}).T
    top = D[q == "S&P rallied (top third)"]
    t1b = pd.DataFrame({"rally, S&P gamma low at start": summ(top[top.gex <= 1 / 3]),
                        "rally, S&P gamma not low": summ(top[top.gex > 1 / 3])}).T
    E = D.dropna(subset=["gex", "dix"])
    low = E.gex <= 1 / 3
    states = {"all days": E.gex == E.gex, "S&P gamma low": low, "+ DIX top third": low & (E.dix >= 2 / 3),
              "+ DIX middle (now)": low & E.dix.between(1 / 3, 2 / 3), "+ DIX bottom third": low & (E.dix < 1 / 3),
              "+ SPY own DPI top third (now)": low & (E.spy_dpi >= 2 / 3)}
    t2 = pd.DataFrame({lab: {**summ(E[m]), "S&P rally %": 100 * (E[m].spx10 >= rally).mean(), "S&P worst dip %": 100 * E[m].spx_dd.mean()}
                       for lab, m in states.items()}).T
    F, A = D.loc["2021":], D.loc["2021":]
    full = F.full
    states = {"TSLA all days": A.full == A.full, "TSLA full setup, any market": full, "full setup + S&P gamma low": full & (F.gex <= 1 / 3),
              "full setup + S&P gamma not low": full & (F.gex > 1 / 3),
              "full setup + gamma low + SPY DPI high": full & (F.gex <= 1 / 3) & (F.spy_dpi >= 2 / 3)}
    t3 = pd.DataFrame({lab: {**summ(F[m]), "episodes": int((m & ~m.shift(1, fill_value=False)).sum())} for lab, m in states.items()}).T
    return t1, t1b, t2, t3


def figure(t1, t2, t3):
    f, axs = plt.subplots(1, 3, figsize=(15, 5.2), gridspec_kw={"wspace": 0.55})
    a, b, c = axs
    k = "TSLA dip worse than -8% %"
    a.barh(range(3), t1[k], color=[C2, MUTED, C3])
    a.set_yticks(range(3), [s.replace(" (", "\n(") for s in t1.index])
    a.set_title("1. Hindsight: if the S&P DOES rally,\nTSLA's deep dips are rarer", loc="left", color=INK, fontsize=10)
    b.barh(range(len(t2)), t2["S&P rally %"], color=[MUTED] + [C1] * (len(t2) - 1))
    b.axvline(t2["S&P rally %"].iloc[0], color=MUTED, ls=":", lw=1)
    b.set_yticks(range(len(t2)), t2.index)
    b.set_title("2. Ex ante: today's readings only\nmodestly raise the odds of a rally", loc="left", color=INK, fontsize=10)
    b.set_xlabel("chance the S&P's next 10 sessions are a top-third rally (%)")
    c.barh(range(len(t3)), t3[k], color=[MUTED] + [C2] * (len(t3) - 1))
    c.axvline(t3[k].iloc[0], color=MUTED, ls=":", lw=1)
    c.set_yticks(range(len(t3)), [s.replace(" + ", "\n+ ") for s in t3.index])
    c.set_title("3. In TSLA's full setup, today-like market\nreadings did NOT cap the drawdown", loc="left", color=INK, fontsize=10)
    for ax in (a, c):
        ax.set_xlabel("chance TSLA dips more than 8% within 10 sessions (%)")
    for ax, t, col in ((a, t1, k), (b, t2, "S&P rally %"), (c, t3, k)):
        ax.invert_yaxis()
        for i, v in enumerate(t[col]):
            ax.text(v + 0.8, i, f"{v:.0f}%  (n={int(t.days.iloc[i])})", va="center", fontsize=8, color=INK)
        ax.set_xlim(0, max(t[col]) * 1.45)
        ax.tick_params(labelsize=8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    f.patch.set_facecolor(SURF)
    f.suptitle("Does a market bounce cap TSLA's downside?  Only if the bounce actually happens: use SPY/QQQ reclaiming their flips "
               "as live confirmation, not today's readings", x=0.01, ha="left", fontsize=10.5, color=INK, weight="bold")
    f.savefig(OUT / "market_cap.png", dpi=150, bbox_inches="tight", facecolor=SURF)


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    t1, t1b, t2, t3 = tables(data())
    names = ("1. TSLA next 10 sessions by what the S&P did (hindsight, 2015+)", "1b. within S&P rallies, by S&P gamma at the start",
             "2. S&P next 10 sessions by today's market readings (ex ante, 2015+)", "3. TSLA full setup by market readings at the start (2021+)")
    for n, t in zip(names, (t1, t1b, t2, t3)):
        print(f"\n{n}\n{t.round(1).to_string()}")
    pd.concat({n.split(".")[0]: t for n, t in zip(names, (t1, t1b, t2, t3))}).round(2).to_csv(OUT / "market_cap.csv")
    figure(t1, t2, t3)
    print("saved", OUT / "market_cap.png")
