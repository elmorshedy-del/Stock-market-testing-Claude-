"""Multi-week up-legs ("thrusts") and what the stock's own options did before, during and at
the top of each one.

Leg definition (replaces single-day bursts): at least +25% (log) within MAX_LEN = 20
sessions. Candidate days are those whose best forward run reaches the threshold; each
cluster becomes one leg. Start = the last close within 3% of the cluster's low before the
take-off (first +5% day or +10% from the low), so a base/consolidation is not cut off.
Top = the running high until the first 10% give-back from it. Legs never overlap.

Phases of a leg
  pre      the 10 sessions before the start
  trigger  the first +5% day (or the leg's biggest day if none) within the first 10 sessions
  top      the high close; 'top trigger' = first session after the top that closes
           down >= 4% or breaks the 5-day low
Structure (weekly closes inside the leg): 'step-up' (the biggest week comes after an
up lead-in week), 'big-first' (the biggest week is the first), 'red-gap' (a down week
>= 4% between two strong weeks); 'bounce' flags legs starting after a drawdown >= 25%
from the 60-session high.
Usage: python legs.py TSLA
"""
import sys

import numpy as np
import pandas as pd

from burst_gamma import state
from common import OUT, load_bars
from forecast import build as spx_frame
from q4_forensics import calendar
from tsla_eras import REACTIONS_2020

MIN_GAIN, MAX_LEN, START = np.log(1.25), 20, "2021-01-01"
NAMED = {"2021-10-11": "Oct 2021 (Hertz)", "2023-01-09": "Jan 2023 (off the bottom)", "2023-05-15": "May 2023",
         "2024-06-24": "Jun-Jul 2024", "2024-10-21": "Oct-Nov 2024 (report + election)",
         "2025-04-21": "Apr-May 2025 (bounce)", "2025-09-08": "Sep 2025"}
ELECTIONS = ["2020-11-03", "2022-11-08", "2024-11-05", "2026-11-03"]


def find_legs(c, near_low=np.log(1.03), give_back=np.log(0.90)):
    lc = np.log(c.to_numpy())
    n = len(lc)
    r = np.r_[0, np.diff(lc)]
    best = np.full(n, -np.inf)
    for h in range(5, MAX_LEN + 1):
        best = np.maximum(best, np.r_[lc[h:] - lc[:-h], np.full(h, -np.inf)])
    cand = best >= MIN_GAIN
    legs, i = [], 0
    while i < n:
        if not cand[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and (cand[j + 1] or (j + 2 < n and cand[j + 2])):
            j += 1
        lo = i + int(np.argmin(lc[i:j + 1]))
        # take-off = first +5% day or +10% from the low; start = last close within 3% of the low before it
        k = lo + 1
        while k < n - 1 and r[k] < 0.05 and lc[k] - lc[lo] < np.log(1.10):
            k += 1
        s = max(t for t in range(lo, k) if lc[t] <= lc[lo] + near_low)
        # top = running high until the first 10% give-back (at least the best high within MAX_LEN)
        e, t = s, s
        while t + 1 < n:
            t += 1
            if lc[t] > lc[e]:
                e = t
            elif lc[t] - lc[e] <= give_back:
                break
        e = max(e, s + int(np.argmax(lc[s:min(s + MAX_LEN, n - 1) + 1])), key=lambda q: lc[q])
        if legs and s <= legs[-1][1]:
            ps, pe = legs[-1]
            legs[-1] = (ps, e if lc[e] > lc[pe] else pe)
        else:
            legs.append((s, e))
        i = max(j + 1, e + 1)
    return [(c.index[s], c.index[e]) for s, e in legs]


def weekly_shape(c, s, e):
    w = c[s:e].resample("W-FRI").last()
    w0 = c[:s].iloc[-1:]
    wk = 100 * np.log(pd.concat([w0, w]).pipe(lambda x: x / x.shift())).dropna()
    big = int(np.argmax(wk.to_numpy()))
    red_gap = any((wk.iloc[k] <= -4) and wk.iloc[:k].max() >= 8 and wk.iloc[k + 1:].max() >= 8 for k in range(1, len(wk) - 1))
    shape = "red-gap" if red_gap else ("big-first" if big == 0 else "step-up")
    return shape, wk


def leg_table(sym="TSLA"):
    b = load_bars(sym)
    c = b.close
    r = np.log(c).diff()
    st = state(sym)
    m = pd.read_csv(OUT / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date")
    st["pc_oi"] = m.put_oi / m.call_oi
    st["call_oi_5d"] = 100 * np.log(m.call_oi / m.call_oi.shift(5))
    spx = spx_frame()
    cal = calendar(c.index)
    rx = {c.index[c.index.searchsorted(pd.Timestamp(d))] for d in REACTIONS_2020} if sym == "TSLA" else set()
    rows = []
    for s, e in find_legs(c):
        if s < pd.Timestamp(START) or s not in st.index:
            continue
        i_s, i_e = c.index.get_loc(s), c.index.get_loc(e)
        seg = r.iloc[i_s + 1:i_s + 11]
        big5 = seg[seg >= 0.05]
        trig = big5.index[0] if len(big5) else seg.idxmax()
        post = c.iloc[i_e + 1:i_e + 30]
        low5 = c.rolling(5).min().shift(1)
        tt = next((t for t in post.index if r[t] <= -0.04 or c[t] < low5[t]), post.index[0] if len(post) else e)
        shape, wk = weekly_shape(c, s, e)
        dd = c.iloc[i_s] / c.iloc[max(0, i_s - 60):i_s + 1].max() - 1
        pre = st.loc[c.index[max(0, i_s - 10)]:s]
        top_w = st.loc[c.index[max(i_s, i_e - 2)]:e]
        mid = st.loc[s:e]
        near = lambda d, lst: min((abs((c.index.searchsorted(pd.Timestamp(x)) - c.index.get_loc(d))) for x in lst), default=99)
        name = next((v for k, v in NAMED.items() if abs((pd.Timestamp(k) - s).days) <= 21), "")
        rows.append({
            "start": s.date(), "trigger": trig.date(), "top": e.date(), "top_trigger": tt.date(), "named": name,
            "sessions": i_e - i_s, "gain_pct": 100 * (c[e] / c[s] - 1), "shape": shape, "bounce": dd <= -0.25,
            "weeks": " ".join(f"{v:+.0f}" for v in wk.to_numpy()),
            "drawdown_before_pct": 100 * dd,
            "trigger_report": trig in rx, "trigger_election": near(trig, ELECTIONS) <= 2,
            "pre_near_min": pre.near_pct.min(), "pre_near_last": pre.near_pct.iloc[-1], "pre_g": pre.g_pct.iloc[-1],
            "pre_flip_pct": pre.to_flip_pct.iloc[-1], "pre_iv": pre.iv_pct.iloc[-1], "pre_pc_oi": pre.pc_oi.iloc[-1],
            "pre_spx_gex": spx.gex_pct.asof(s), "pre_dix": spx.dix_pct.asof(s),
            "start_to_wall_pct": st.to_call_wall_pct.get(s), "wall_at_start": st.call_wall.get(s),
            # walls are raw strikes: compare with the option-implied (unadjusted) spot, not split-adjusted closes
            "wall_at_top": st.call_wall.get(e), "top_vs_start_wall_pct": 100 * (st.spot.get(e) / st.call_wall.get(s) - 1),
            "top_vs_top_wall_pct": 100 * (st.spot.get(e) / st.call_wall.get(e) - 1),
            "mid_call_oi_growth_pct": 100 * np.log(m.call_oi.get(e) / m.call_oi.get(s)),
            "top_near": top_w.near_pct.mean(), "top_g": top_w.g_pct.mean(), "top_iv": top_w.iv_pct.mean(),
            "top_flip_pct": st.to_flip_pct.get(e) if np.isfinite(st.to_flip_pct.get(e, np.nan)) else 20.0,  # no flip within +-20% "top_pc_oi": st.pc_oi.get(e), "top_spx_gex": spx.gex_pct.asof(e),
            "top_tdays_to_opex": cal.tdays_to_opex.get(e), "top_tdays_since_opex": cal.tdays_since_opex.get(e),
            "iv_rise_in_leg": st.iv_pct.get(e) - st.iv_pct.get(s),
            "after_top_20d_pct": 100 * (c.iloc[min(i_e + 20, len(c) - 1)] / c[e] - 1)})
    return pd.DataFrame(rows), st, c


if __name__ == "__main__":
    pd.set_option("display.width", 260)
    pd.set_option("display.max_columns", 60)
    sym = (sys.argv[1:] or ["TSLA"])[0]
    L, st, c = leg_table(sym)
    L.to_csv(OUT / f"legs_{sym}.csv", index=False)
    print(L[["start", "trigger", "top", "top_trigger", "named", "sessions", "gain_pct", "shape", "bounce", "weeks"]].round(1).to_string(index=False))
