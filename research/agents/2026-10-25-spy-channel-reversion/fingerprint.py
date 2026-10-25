"""Which signals fired before all three reversions of the 2022-2026 S&P channel, and how often did they fire otherwise?
Design pre-registered at 1736cd2 (README.md, 'Redirect by the owner').
Usage: python fingerprint.py <folder with Yahoo chart JSONs and DIX.csv>  -> out/fingerprint.csv, out/fingerprint.json, out/fingerprint.png"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
START, END = pd.Timestamp("2022-10-13"), pd.Timestamp("2026-10-23")
TOPS = [("2023-07-31", "2023-10-27"), ("2025-02-19", "2025-04-08"), ("2026-01-27", "2026-03-30")]
MINOR = [("2024-03-28", "2024-04-19"), ("2024-07-16", "2024-08-05"), (None, "2025-11-20")]   # Nov 2025 top: the highest close in the 40 sessions before the low
WIN, MIN_DAYS, ALARM, NSHIFT = 30, 3, 0.80, 1000
RNG = np.random.default_rng(20261025)
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def series(folder, name, adj=True):
    d = json.loads((Path(folder) / f"{name}.json").read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    ind = d["indicators"]
    v = ind["adjclose"][0]["adjclose"] if adj and "adjclose" in ind else ind["quote"][0]["close"]
    s = pd.Series(v, index=idx, dtype=float).dropna()
    return s[~s.index.duplicated(keep="last")].sort_index()


def pct(s, n=252):
    return s.rolling(n, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)


def signals(folder):
    g = lambda n, adj=True: series(folder, n, adj)
    spx, spy = g("%5EGSPC", False), g("SPY")
    vix, vix3m, vix9d, vvix, skew = (g(n, False) for n in ("%5EVIX", "%5EVIX3M", "%5EVIX9D", "%5EVVIX", "%5ESKEW"))
    idx = spx.index
    al = lambda s: s.reindex(idx).ffill()
    r = np.log(spx).diff()
    dix = pd.read_csv(Path(folder) / "DIX.csv", parse_dates=["date"]).set_index("date")
    rel = lambda a, b: np.log(al(g(a))).diff(20) - np.log(al(g(b))).diff(20)
    ret20 = lambda a: np.log(al(g(a))).diff(20)
    S = pd.DataFrame(index=idx)
    gp = pct(al(dix.gex))
    S["M1 dealer gamma low"] = -gp
    S["M2 gamma percentile falling (10d)"] = -(gp - gp.shift(10))
    S["M3 DIX low"] = -pct(al(dix.dix))
    rv = r.rolling(20).std() * np.sqrt(252) * 100
    S["M4 realized vol low (vol-target max exposure)"] = -pct(rv)
    S["M5 VIX minus realized vol high"] = al(vix) - rv
    S["T1 trend broken (close vs 50-day)"] = -(np.log(spx) - np.log(spx.rolling(50).mean()))
    S["T2 20-day return low"] = -np.log(spx).diff(20)
    up, dn = r.clip(lower=0).rolling(14).mean(), (-r.clip(upper=0)).rolling(14).mean()
    S["T3 RSI overbought"] = 100 - 100 / (1 + up / dn)
    hi = spx.rolling(252).max()
    S["T4 sessions since 52-week high"] = (spx < hi).astype(int).groupby((spx >= hi).cumsum()).cumsum()
    S["V1 VIX/VIX3M high"] = al(vix) / al(vix3m)
    S["V2 VIX9D/VIX high"] = al(vix9d) / al(vix)
    S["V3 VVIX high"] = pct(al(vvix))
    S["V4 SKEW high"] = pct(al(skew))
    S["V5 VIX not falling on up days (10d corr)"] = r.rolling(10).corr(np.log(al(vix)).diff())
    S["V6 VIX rising (10d)"] = np.log(al(vix)).diff(10)
    S["X1 credit lagging (HYG vs IEF)"] = -rel("HYG", "IEF")
    S["X2 small caps lagging (IWM vs SPY)"] = -rel("IWM", "SPY")
    S["X3 breadth narrowing (RSP vs SPY)"] = -rel("RSP", "SPY")
    S["X4 semis lagging (SMH vs SPY)"] = -rel("SMH", "SPY")
    S["X5 discretionary lagging staples (XLY vs XLP)"] = -rel("XLY", "XLP")
    S["X6 regional banks lagging (KRE vs SPY)"] = -rel("KRE", "SPY")
    S["X7 bonds falling (TLT)"] = -ret20("TLT")
    S["X8 dollar rising (UUP)"] = ret20("UUP")
    S["X9 bitcoin falling"] = -ret20("BTC-USD")
    aapl = al(g("AAPL"))
    ra = np.log(aapl).diff()
    a_rel = np.log(aapl).diff(20) - np.log(al(spy)).diff(20)
    S["A1 AAPL lagging SPY (20d)"] = -a_rel
    S["A2 AAPL diverging either way (20d)"] = a_rel.abs()
    S["A3 AAPL below its 50-day while S&P above"] = ((aapl < aapl.rolling(50).mean()) & (spx > spx.rolling(50).mean())).astype(float)
    S["A4 AAPL decoupling (20d corr with SPY low)"] = -ra.rolling(20).corr(np.log(al(spy)).diff())
    P = pd.DataFrame({k: (S[k] if k.startswith("A3") else pct(S[k])) for k in S}, index=idx)
    return spx, S, P


def minor_tops(spx):
    out = []
    for t, l in MINOR:
        if t is None:
            li = spx.index.get_loc(pd.Timestamp(l))
            t = str(spx.iloc[li - 40:li + 1].idxmax().date())
        out.append((t, l))
    return out


def windows(idx):
    pre, inside, minor = np.zeros(len(idx), bool), np.zeros(len(idx), bool), np.zeros(len(idx), bool)
    for t, l in TOPS:
        ti, li = idx.get_loc(pd.Timestamp(t)), idx.get_loc(pd.Timestamp(l))
        pre[ti - WIN + 1:ti + 1] = True
        inside[ti + 1:li + 1] = True
    for t, l in MINOR:
        ti, li = idx.searchsorted(pd.Timestamp(t)), idx.get_loc(pd.Timestamp(l))
        minor[ti - WIN + 1:li + 1] = True
    return pre, inside, minor


def score(on, idx, pre, normal):
    hits, leads = [], []
    for t, _ in TOPS:
        ti = idx.get_loc(pd.Timestamp(t))
        w = on[ti - WIN + 1:ti + 1]
        hits.append(int(w.sum() >= MIN_DAYS))
        leads.append(int(WIN - 1 - np.argmax(w)) if w.any() else None)
    return hits, leads, float(on[normal].mean())


def main(folder):
    OUT.mkdir(exist_ok=True)
    spx, S, P = signals(folder)
    m = (P.index >= START) & (P.index <= END)
    P, spxc = P[m], spx[m]
    idx = P.index
    global MINOR
    MINOR = minor_tops(spxc)
    pre, inside, minor = windows(idx)
    normal = ~(pre | inside | minor)
    rows = []
    for k in P:
        on = (P[k] >= (0.5 if k.startswith("A3") else ALARM)).to_numpy() & P[k].notna().to_numpy()
        hits, leads, fa = score(on, idx, pre, normal)
        luck = 0
        n = len(on)
        for s in RNG.integers(60, n - 60, NSHIFT):
            o = np.roll(on, s)
            h, _, f = score(o, idx, pre, normal)
            luck += (sum(h) == 3 and f <= fa)
        minor_fired = []
        for t, _ in MINOR:
            ti = idx.searchsorted(pd.Timestamp(t))
            minor_fired.append(int(on[ti - WIN + 1:ti + 1].sum() >= MIN_DAYS))
        rows.append({"signal": k, "hits (2023, 2025, 2026)": "".join("✓" if h else "·" for h in hits), "hits": sum(hits),
                     "lead sessions (first alarm in window)": leads, "false-alarm rate": fa, "luck share": luck / NSHIFT,
                     "fired before minor pullbacks (Mar24, Jul24, Nov25)": minor_fired, "on today": bool(on[-1]),
                     "today percentile": float(P[k].iloc[-1]) if pd.notna(P[k].iloc[-1]) else None})
    R = pd.DataFrame(rows).sort_values(["hits", "false-alarm rate"], ascending=[False, True])
    R["candidate (3/3, FA <= 15%, luck <= 0.05)"] = (R.hits == 3) & (R["false-alarm rate"] <= 0.15) & (R["luck share"] <= 0.05)
    R.to_csv(OUT / "fingerprint.csv", index=False)
    res = {"minor pullbacks used": MINOR, "normal days": int(normal.sum()), "signals": int(len(R)), "hitting 3/3": int((R.hits == 3).sum()),
           "expected by luck to hit 3/3 at their false-alarm rate (sum of luck shares)": float(R["luck share"].sum()),
           "candidates": R[R["candidate (3/3, FA <= 15%, luck <= 0.05)"]].signal.tolist(),
           "today": {r.signal: r["on today"] for _, r in R.iterrows()}}
    (OUT / "fingerprint.json").write_text(json.dumps(res, indent=1, default=float))
    figure(spxc, P, R, pre, inside, minor)
    return R, res


def figure(spx, P, R, pre, inside, minor):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    show = R.head(14)
    f, (a, z) = plt.subplots(2, 1, figsize=(16, 9.5), sharex=True, gridspec_kw={"height_ratios": [1, 2.2], "hspace": 0.05})
    x = spx.index
    a.plot(x, spx, color=INK, lw=1.3)
    for ax in (a, z):
        for t, l in TOPS:
            ax.axvspan(pd.Timestamp(t) - pd.Timedelta(days=42), pd.Timestamp(t), color=ORANGE, alpha=0.12, lw=0)
            ax.axvspan(pd.Timestamp(t), pd.Timestamp(l), color=MUTED, alpha=0.10, lw=0)
    for t, l in TOPS:
        a.annotate(f"top {pd.Timestamp(t):%b %Y}", (pd.Timestamp(t), spx[t]), (pd.Timestamp(t) - pd.Timedelta(days=60), spx[t] * 1.04),
                   fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
    a.set_ylabel("S&P 500")
    a.set_title("Which warnings lit up before all three channel reversions (orange band: 30 sessions before each top; grey: the reversion)?\n"
                "each row: the signal's alarm days (top 20% of its own past year); ranked by hits, then by how often it fired at other times",
                loc="left", fontsize=10, color=INK)
    for i, (_, r) in enumerate(show.iterrows()):
        on = (P[r.signal] >= (0.5 if r.signal.startswith("A3") else ALARM)).to_numpy()
        y = len(show) - i
        col = GREEN if r["candidate (3/3, FA <= 15%, luck <= 0.05)"] else (BLUE if r.hits == 3 else MUTED)
        z.scatter(x[on], np.full(on.sum(), y), marker="|", s=40, color=col, lw=1.2)
        z.text(x[-1] + pd.Timedelta(days=12), y, f"{r['hits (2023, 2025, 2026)']}  FA {100 * r['false-alarm rate']:.0f}%  luck {r['luck share']:.2f}"
               f"{'  ON NOW' if r['on today'] else ''}", va="center", fontsize=8, color=INK)
    z.set_yticks(range(len(show), 0, -1), show.signal.tolist(), fontsize=8)
    z.set_ylim(0.3, len(show) + 0.7)
    z.set_xlim(x[0], x[-1] + pd.Timedelta(days=260))
    f.savefig(OUT / "fingerprint.png", dpi=140, bbox_inches="tight", facecolor=SURF)


if __name__ == "__main__":
    R, res = main(sys.argv[1])
    pd.set_option("display.width", 250, "display.max_colwidth", 60)
    print(R[["signal", "hits (2023, 2025, 2026)", "lead sessions (first alarm in window)", "false-alarm rate", "luck share",
             "fired before minor pullbacks (Mar24, Jul24, Nov25)", "on today", "candidate (3/3, FA <= 15%, luck <= 0.05)"]].round(3).to_string(index=False))
    print(json.dumps({k: v for k, v in res.items() if k != "today"}, indent=1))
