"""D1 (pre-registered @ 7f12ecb): on S&P down days <= -1%, does TSLA's own long dealer gamma cushion it (D1a), and does
low S&P gamma override that cushion (D1b)? Usage: python d1_override.py <TSLA daily json> <DIX.csv> -> out/d1.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MICRO = HERE.parents[1] / "microstructure"
r = json.load(open(sys.argv[1]))["chart"]["result"][0]
adj = r["indicators"].get("adjclose", [{}])[0].get("adjclose") or r["indicators"]["quote"][0]["close"]
ts = pd.Series(adj, index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").normalize().tz_localize(None)).dropna()
ts = ts[~ts.index.duplicated(keep="last")]
sq = pd.read_csv(sys.argv[2], parse_dates=["date"]).set_index("date")
sq["gex_pct"] = sq.gex.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
h = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
gn = h.gex_classic / (h.spot * (h.call_oi + h.put_oi) * 100)
own_pct = gn.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)

df = pd.DataFrame({"t": ts.pct_change(), "s": sq.price.pct_change()}).dropna()
df["beta"] = (df.t.rolling(60).cov(df.s) / df.s.rolling(60).var()).shift(1)
df["own"] = own_pct.reindex(df.index).shift(1); df["spg"] = sq.gex_pct.reindex(df.index).shift(1)
df["ex"] = df.t - df.beta * df.s; df["ex_next"] = df.ex.shift(-1)
ev = df[(df.s <= -0.01) & (df.index >= "2020-01-02") & (df.index <= "2026-10-14")].dropna(subset=["beta", "own", "spg"]).copy()
ev["own_state"] = np.where(ev.own >= 2 / 3, "high", np.where(ev.own <= 1 / 3, "low", "mid"))
ev["sp_state"] = np.where(ev.spg <= 0.30, "S&P gamma low", "S&P gamma not low")
ev["month"] = ev.index.to_period("M")
rng = np.random.default_rng(0)


def diff_stat(x, col):
    def d(z):
        a = z[(z.own_state == "high") & (z.sp_state == "S&P gamma not low")][col].mean() - z[(z.own_state == "low") & (z.sp_state == "S&P gamma not low")][col].mean()
        b = z[(z.own_state == "high") & (z.sp_state == "S&P gamma low")][col].mean() - z[(z.own_state == "low") & (z.sp_state == "S&P gamma low")][col].mean()
        return a, b, a - b
    obs = d(x); months = x.month.unique(); g = {m: x[x.month == m] for m in months}; bs = []
    for _ in range(5000):
        z = pd.concat([g[m] for m in rng.choice(months, len(months))]); bs.append(d(z))
    bs = np.array(bs); out = {}
    for i, k in enumerate(("D1a cushion (high-low own, S&P gamma not low)", "same, S&P gamma low", "D1b interaction")):
        v = bs[:, i][~np.isnan(bs[:, i])]
        out[k] = {"pts": round(obs[i] * 100, 2), "90% CI": [round(np.quantile(v, .05) * 100, 2), round(np.quantile(v, .95) * 100, 2)], "p (one-sided, >0)": round(float((v <= 0).mean()), 3)}
    return out


res = {"n events": len(ev)}
cells = ev.groupby(["sp_state", "own_state"]).agg(n=("ex", "size"), sp=("s", "mean"), tsla=("t", "mean"), beta=("beta", "mean"), excess=("ex", "mean"), excess_next=("ex_next", "mean"))
cells[["sp", "tsla", "excess", "excess_next"]] *= 100
res["cells (% means)"] = {f"{a} | own {b}": {k: round(float(v), 2) for k, v in row.items()} for (a, b), row in cells.iterrows()}
res["primary"] = diff_stat(ev, "ex")
ps = sorted([(res["primary"]["D1a cushion (high-low own, S&P gamma not low)"]["p (one-sided, >0)"], "D1a"), (res["primary"]["D1b interaction"]["p (one-sided, >0)"], "D1b")])
res["Holm"] = {ps[0][1]: min(1, ps[0][0] * 2), ps[1][1]: min(1, max(ps[0][0] * 2, ps[1][0]))}
res["secondary next-day"] = diff_stat(ev.dropna(subset=["ex_next"]), "ex_next")
for lab, lo, hi in (("2020-21", "2020", "2021-12-31"), ("2022-26", "2022", "2026-12-31")):
    x = ev.loc[lo:hi]
    res[f"regime {lab}"] = {"n": len(x), "cells n": x.groupby(["sp_state", "own_state"]).size().to_dict().__repr__(), "diffs": diff_stat(x, "ex")}
# correlation check (REPORT 4k replica on this window): TSLA-S&P correlation on all days by S&P gamma state
allx = df.loc["2020":"2026-10-14"].dropna(subset=["spg"])
res["all-day corr by S&P gamma"] = {k: round(float(g.t.corr(g.s)), 2) for k, g in allx.groupby(np.where(allx.spg <= 0.3, "low", "not low"))}
res["down-day TSLA/S&P move ratio by S&P gamma"] = {k: round(float(g.t.mean() / g.s.mean()), 2) for k, g in ev.groupby("sp_state")}
json.dump(res, open(HERE / "out" / "d1.json", "w"), indent=1, default=str)
ev[["s", "t", "beta", "ex", "ex_next", "own_state", "sp_state"]].to_csv(HERE / "out" / "d1_events.csv")
print(json.dumps(res, indent=1, default=str))
