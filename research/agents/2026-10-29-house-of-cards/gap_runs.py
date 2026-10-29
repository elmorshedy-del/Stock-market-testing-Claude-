"""H4-H6 (pre-registered @ bab7db6): gap-ups >= 0.5 sigma in TSLA, NVDA, QQQ, MSFT, MU (2020-02 to 2026-10-14) after a forced run
(price up and 30-day ATM IV up over the 10 sessions to the prior close) vs not; and options-led runs. Plus the 7-day ATM call translation.
Usage: python gap_runs.py <scratchpad> -> out/gap_runs.json, out/gap_events.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm as N

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; CX = S / "ctx"
rng = np.random.default_rng(0); B = 10000
SYMS = ["TSLA", "NVDA", "QQQ", "MSFT", "MU"]
SPLITS = {"TSLA": ["2020-08-31", "2022-08-25"], "NVDA": ["2021-07-20", "2024-06-10"]}
ev = pd.read_csv(HERE.parent / "2026-10-29-calendar-mechanics" / "out" / "events13.csv", parse_dates=["date"])
ev = ev[ev.sym.isin(SYMS) & (ev.date >= "2020-02-01") & (ev.date <= "2026-10-14")]
iv = pd.read_csv(HERE / "out" / "ivseries.csv", parse_dates=["date"])


def daily(sym):
    r = json.load(open(CX / "daily" / f"{sym}.json"))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ("open", "close", "volume")}, index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return d[~d.index.duplicated(keep="last")].dropna()


def bs_call(S0, K, T, v):
    d1 = (np.log(S0 / K) + 0.5 * v * v * T) / (v * np.sqrt(T)); return S0 * N.cdf(d1) - K * N.cdf(d1 - v * np.sqrt(T))


rows = []
for s in SYMS:
    dd = daily(s); ivs = iv[iv.sym == s].set_index("date")
    for r in ev[ev.sym == s].itertuples():
        pr = dd[dd.index < r.date]
        if len(pr) < 71 or r.date not in dd.index: continue
        d1, d11 = pr.index[-1], pr.index[-11]
        if d1 not in ivs.index or d11 not in ivs.index: continue
        ret10 = pr.close.iloc[-1] / pr.close.iloc[-11] - 1; ivchg = ivs.atm_iv30[d1] - ivs.atm_iv30[d11]
        o = {"sym": s, "date": r.date, "cls": r.cls, "Y1": r.Y1, "sig": r.sig, "ret10": ret10, "iv_chg": ivchg, "iv_prev": ivs.atm_iv30[d1],
             "forced": int(ret10 > 0 and ivchg > 0), "oc_sig": (dd.close[r.date] / dd.open[r.date] - 1) / r.sig, "oc_pct": 100 * (dd.close[r.date] / dd.open[r.date] - 1)}
        # options-led: call contracts x100 / shares, last 10 sessions vs the 60 before them; skip windows spanning a split
        win = pr.index[-70:]
        if not any(win[0] < pd.Timestamp(x) <= r.date for x in SPLITS.get(s, [])):
            cv = ivs.call_vol.reindex(win); sv = pr.volume.reindex(win)
            ratio = 100 * cv / sv
            o["opt_led"] = float(ratio.iloc[-10:].mean() / ratio.iloc[:60].mean()) if ratio.notna().sum() >= 60 else np.nan
        # 7-day ATM call bought at the open, marked at the close, prior-close IV held constant
        v = ivs.atm_iv30[d1]; S0, S1 = dd.open[r.date], dd.close[r.date]
        if np.isfinite(v) and v > 0:
            V0 = bs_call(S0, S0, 7 / 365, v); V1 = bs_call(S1, S0, (7 - 6.5 / 24) / 365, v); o["call7_open_to_close_pct"] = 100 * (V1 / V0 - 1)
        rows.append(o)
G = pd.DataFrame(rows)
G["opt_led_top"] = (G.groupby("sym").opt_led.rank(pct=True) > 2 / 3).astype(float).where(G.opt_led.notna())


def contrast(df, flag, y):
    df = df[flag.notna() & df[y].notna()].copy(); df["g"] = flag[df.index].astype(int); df["yd"] = df[y] - df.groupby("sym")[y].transform("mean")
    est = df[df.g == 1].yd.mean() - df[df.g == 0].yd.mean(); dates = df.date.unique(); idx = {d: np.flatnonzero(df.date.to_numpy() == d) for d in dates}
    yd, g = df.yd.to_numpy(), df.g.to_numpy(); bs = np.empty(B)
    for i in range(B):
        k = np.concatenate([idx[d] for d in rng.choice(dates, len(dates))]); bs[i] = yd[k][g[k] == 1].mean() - yd[k][g[k] == 0].mean() if (g[k] == 1).any() and (g[k] == 0).any() else np.nan
    bs = bs[~np.isnan(bs)]
    return {"n_context": int(df.g.sum()), "n_rest": int((df.g == 0).sum()), "est": float(est), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
            "p": float(min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1 / len(bs))),
            "vf_context": float((df[df.g == 1].cls == "VF").mean()), "vf_rest": float((df[df.g == 0].cls == "VF").mean()),
            "sc_context": float((df[df.g == 1].cls == "SC").mean()), "sc_rest": float((df[df.g == 0].cls == "SC").mean())}


T = {"H4 gap-up after a forced run: Y1 (open -> 10:30, sigma)": contrast(G, G.forced.astype(float), "Y1"),
     "H5 gap-up after a forced run: open -> close (sigma)": contrast(G, G.forced.astype(float), "oc_sig"),
     "H6 gap-up after an options-led run: open -> close (sigma)": contrast(G, G.opt_led_top, "oc_sig")}
call = {k: {"forced" if f else "not forced": {"n": int(len(x)), "mean_pct": float(x.call7_open_to_close_pct.mean()), "median_pct": float(x.call7_open_to_close_pct.median()),
                                              "share_losing_25pct_or_more": float((x.call7_open_to_close_pct <= -25).mean())} for f, x in G.dropna(subset=["call7_open_to_close_pct"]).groupby(col)}
        for k, col in (("by forced run", "forced"),)}
json.dump({"tests": T, "call7_translation": call, "counts": G.groupby(["sym", "forced"]).size().unstack(fill_value=0).to_dict()}, open(HERE / "out" / "gap_runs.json", "w"), indent=1, default=float)
G.to_csv(HERE / "out" / "gap_events.csv", index=False)
pd.set_option("display.width", 250); print(pd.DataFrame(T).T.to_string()); print(json.dumps(call, indent=1, default=lambda x: round(float(x), 2)))
print(G.groupby(["sym", "forced"]).size().unstack(fill_value=0))
print(G[G.date == "2020-09-02"].round(3).to_string())
