"""The slow state before every S&P fall of 15% or more since 1963, against a control group of months that were also near a 12-month high
but were NOT followed by a big fall. State is read at the end of the month before the peak month (macro data lagged one more month)."""
import json
from math import comb
import numpy as np, pandas as pd
from common import H, y, f, gold_monthly, cape, bond_ret

THR = 0.15
def drawdown_events(px, thr=THR, start="1963-01-01"):
    ev, peak, pdate, in_dd, trough, tdate = [], px.iloc[0], px.index[0], False, None, None
    for d, v in px.items():
        if not in_dd:
            if v >= peak: peak, pdate = v, d
            elif v <= peak * (1 - thr): in_dd, trough, tdate = True, v, d
        else:
            if v < trough: trough, tdate = v, d
            if v >= peak:
                ev.append((pdate, tdate, trough / peak - 1, d)); in_dd = False; peak, pdate = v, d
    if in_dd: ev.append((pdate, tdate, trough / peak - 1, None))
    return [e for e in ev if e[0] >= pd.Timestamp(start)]

def monthly_state():
    me = lambda s: s.resample("ME").last(); ma = lambda s: s.resample("ME").mean()
    spx_d = y("SPX"); spx = me(spx_d)
    core = f("CPILFESL"); core.index = core.index + pd.offsets.MonthEnd(0); core_yy = (100 * core.pct_change(12)).shift(1)   # released next month
    capeM = cape(); capeM.index = capeM.index + pd.offsets.MonthEnd(0); capeM = capeM.shift(1)
    tb3 = f("TB3MS"); tb3.index = tb3.index + pd.offsets.MonthEnd(0)
    baa = f("BAA"); baa.index = baa.index + pd.offsets.MonthEnd(0)
    t10 = ma(f("DGS10")); real = t10 - core_yy
    S = pd.DataFrame(index=spx.index)
    S["CAPE"] = capeM
    S["Excess earnings yield (1/CAPE − real 10y)"] = 100 / capeM - real
    S["10y yield, 12m change (bp)"] = 100 * t10.diff(12)
    S["Real 10y, 12m change (bp)"] = 100 * real.diff(12)
    S["Yield curve 10y − 3m"] = t10 - tb3
    S["Baa − 10y spread"] = baa - t10
    S["Baa − 10y spread, 12m change (bp)"] = 100 * (baa - t10).diff(12)
    S["Financial conditions (NFCI)"] = me(f("NFCI"))
    S["Leverage (NFCI leverage sub-index)"] = me(f("NFCILEVERAGE"))
    wk = lambda s: s.resample("W-FRI").last()
    sb = pd.concat([np.log(wk(spx_d)).diff(), bond_ret(wk(f("DGS10")), 52)], axis=1, keys=["s", "b"]).dropna()
    S["Stock–bond correlation, 3y"] = me(sb.s.rolling(156).corr(sb.b))
    S["S&P realized volatility, 3m (%)"] = me(np.log(spx_d).diff().rolling(63).std() * np.sqrt(252) * 100)
    S["S&P return, 12m (%)"] = 100 * spx.pct_change(12)
    S["Gold return, 12m (%)"] = 100 * gold_monthly().reindex(S.index).pct_change(12)
    S["Dollar, 12m change (%)"] = 100 * me(y("DXY")).pct_change(12)
    return S, spx, spx_d

def binom_two_sided(k, n):
    p = sum(comb(n, i) for i in range(n + 1) if comb(n, i) <= comb(n, k)) / 2 ** n; return min(1.0, p)

if __name__ == "__main__":
    S, spx, spx_d = monthly_state()
    ev = drawdown_events(spx_d)
    print(f"{len(ev)} falls of ≥{THR:.0%} since 1963:")
    for p, t, dd, rec in ev: print(f"  peak {p.date()}  trough {t.date()}  {dd:+.1%}  recovered {rec.date() if rec is not None else 'not yet'}")
    peak_months = [p + pd.offsets.MonthEnd(0) for p, *_ in ev]
    state_month = [m - pd.offsets.MonthEnd(1) for m in peak_months]   # month before the peak month
    # control: month-ends within 3% of the trailing 12-month high, with no fall of 10% or more in the next 12 months,
    # and not within the 12 months before an event peak
    hi = spx_d.rolling(252, min_periods=200).max().resample("ME").last(); px = spx
    fwd_min = spx_d[::-1].rolling(252, min_periods=150).min()[::-1].resample("ME").last()
    near = px >= 0.97 * hi; safe = (fwd_min / px - 1) > -0.10
    excl = pd.Series(False, index=px.index)
    for m in peak_months: excl |= (px.index > m - pd.DateOffset(months=13)) & (px.index <= m)
    ctrl = px.index[near & safe & ~excl & (px.index >= "1963-01-01") & (px.index <= "2025-10-31")]
    print(f"\ncontrol months: {len(ctrl)} (near a 12-month high, no fall of 10%+ in the next 12 months)")
    rows, table = [], {}
    for v in S.columns:
        c = S.loc[ctrl, v].dropna(); e = S.loc[state_month, v]
        e = e[e.notna()]; pct = [(c < x).mean() for x in e]
        k = int(sum(p > 0.5 for p in pct)); n = len(pct)
        now = S.loc["2026-09-30", v] if "2026-09-30" in S.index else np.nan
        rows.append({"variable": v, "n_events": n, "event_median": round(float(e.median()), 2), "control_median": round(float(c.median()), 2),
                     "event_median_percentile": round(float(np.median(pct)) * 100) if n else None, "events_above_control_median": f"{k}/{n}",
                     "p_sign": round(binom_two_sided(k, n), 3) if n else None, "now (Sep 2026)": round(float(now), 2) if pd.notna(now) else None,
                     "now_percentile_in_control": round(float((c < now).mean()) * 100) if pd.notna(now) else None})
        table[v] = {str(m.date())[:7]: (round(float(S.loc[m, v]), 2) if pd.notna(S.loc[m, v]) else None) for m in state_month}
    R = pd.DataFrame(rows)
    # Holm across variables
    order = R.p_sign.rank(method="first").astype(int); m = len(R)
    adj = R.p_sign.sort_values().reset_index(drop=False)
    holm = {}; prev = 0
    for i, (idx, p) in enumerate(zip(adj["index"], adj.p_sign)):
        val = min(1.0, max(prev, (m - i) * p)); holm[idx] = round(val, 3); prev = val
    R["p_Holm"] = R.index.map(holm)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20)
    print("\n" + R.to_string(index=False))
    E = pd.DataFrame(table).T; E.columns = [c for c in E.columns]
    print("\nEvent-by-event state (month before each peak):"); print(E.to_string())
    json.dump({"events": [{"peak": str(p.date()), "trough": str(t.date()), "depth": dd, "recovered": str(r.date()) if r is not None else None} for p, t, dd, r in ev],
               "n_control": len(ctrl), "summary": R.to_dict("records"), "event_states": table}, open(H / "out" / "state.json", "w"), indent=1, default=float)
    S.to_csv(H / "out" / "monthly_state.csv"); pd.Series(ctrl).to_csv(H / "out" / "control_months.csv", index=False)
