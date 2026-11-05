"""P4 deep-change checklist (descriptive). Today vs the eve of the 2000, 2007, 2020 and 2022 bear markets (pre-registered), plus a
control group added before computing: the eve of every >=10% decline from a record close since 1999 that stopped short of 20%.
Eve = the month of the record close (monthly series) or the 21 sessions ending on it (daily series). Usage: python p4.py
Inputs (data/, gitignored; re-fetch from FRED): data/fred_monthly_1999_2026.csv (FRED monthly averages: DFF DGS10 UNRATE CORECPI_YY WTI DGS2 BAA10Y), data/fred_dfii10_monthly_2003_2026.csv
(FRED DFII10 monthly averages), latest daily FRED prints below (fetched 2026-11-05 through the Firecrawl/Alexandria FRED provider),
Shiller CAPE from multpl.com (fetched live), ^VIX, ^VIX3M, CL=F and ^GSPC from Yahoo (fetched live)."""
import json, re, html as htmllib, urllib.request, importlib.util, numpy as np, pandas as pd
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
M = pd.read_csv(H / "data" / "fred_monthly_1999_2026.csv", index_col=0, parse_dates=True)
M["DFII10"] = pd.read_csv(H / "data" / "fred_dfii10_monthly_2003_2026.csv", index_col=0, parse_dates=True)["DFII10"]
LATEST = {"BAA10Y": ("2026-11-03", 1.54), "DGS2": ("2026-11-04", 4.58), "DFF": ("2026-11-04", 3.88), "DGS10": ("2026-11-04", 4.90), "DFII10": ("2026-11-04", 2.64),
          "HY OAS (ICE BofA; FRED keeps only 2023-11 on, so no eve values)": ("2026-11-04", 3.32)}
BEARS = {"2000": "2000-03-24", "2007": "2007-10-09", "2020": "2020-02-19", "2022": "2022-01-03"}
CONTROLS = {"1999": "1999-07-16", "2015": "2015-05-21", "2018a": "2018-01-26", "2018b": "2018-09-20", "2025": "2025-02-19"}  # >=10% from a record, <20%, macro data exist
spx = lc.yahoo("^GSPC", "1998-01-01").close; rec_date = spx[spx == spx.cummax()].index[-1]; NOW = str(rec_date.date())
# ---- monthly indicators
M["Baa - 10y (pp)"] = M.BAA10Y
M["2y - fed funds (pp)"] = M.DGS2 - M.DFF
M["10y real yield, TIPS (%)"] = M.DFII10
M["10y - core CPI y/y (pp)"] = M.DGS10 - M.CORECPI_YY
M["Unemployment - 12-month low (pp)"] = M.UNRATE - M.UNRATE.rolling(12, min_periods=6).min()
M["Core CPI y/y (%)"] = M.CORECPI_YY
M["WTI oil y/y (%)"] = 100 * (M.WTI / M.WTI.shift(12) - 1)
html = urllib.request.urlopen(urllib.request.Request("https://www.multpl.com/shiller-pe/table/by-month", headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", "replace")
rows = re.findall(r"<td>\s*([A-Z][a-z]{2} \d{1,2}, \d{4})\s*</td>\s*<td>([^<]*)</td>", html)
cape = pd.Series({pd.Timestamp(d): float(re.search(r"-?\d+(?:\.\d+)?", htmllib.unescape(v).replace("\u2002", " ")).group()) for d, v in rows}).sort_index()
assert len(cape) > 1500 and cape.between(4, 50).all(), (len(cape), cape.max())
cape_m = cape[cape.index.day == 1]; cape_latest = (str(cape.index[-1].date()), float(cape.iloc[-1]))
M["Shiller CAPE"] = cape_m.reindex(M.index)
vix, v3 = lc.yahoo("^VIX", "1998-01-01").close, lc.yahoo("^VIX3M", "2006-01-01").close
ratio = (vix / v3).dropna(); M["VIX / VIX3M"] = ratio.groupby(ratio.index.to_period("M")).mean().to_timestamp().reindex(M.index)
oil = lc.yahoo("CL=F", "2024-06-01").close
IND = ["Baa - 10y (pp)", "2y - fed funds (pp)", "10y real yield, TIPS (%)", "10y - core CPI y/y (pp)", "Unemployment - 12-month low (pp)", "Core CPI y/y (%)", "WTI oil y/y (%)", "VIX / VIX3M", "Shiller CAPE"]
def at(ind, date):
    """Eve value: daily VIX/VIX3M = mean of the 21 sessions ending on the record date; monthly = the record month (falls back to the latest month for 'now')."""
    d = pd.Timestamp(date)
    if ind == "VIX / VIX3M":
        w = ratio[ratio.index <= d].iloc[-21:]
        return (round(float(w.mean()), 3), None) if len(w) == 21 and w.index[0] > d - pd.Timedelta(days=45) else (None, None)
    m = pd.Timestamp(d.year, d.month, 1); s = M[ind].dropna()
    if m in s.index: return round(float(s[m]), 2), None
    if date == NOW and len(s): return round(float(s.iloc[-1]), 2), str(s.index[-1].date())[:7]
    return None, None
dist = {}
for ind in IND:
    s = M[ind].dropna(); s = s[s.index <= "2026-10-01"]; dist[ind] = {"from": str(s.index[0].date())[:7], "n months": int(len(s)), "p10/p33/p50/p67/p90": [round(float(s.quantile(q)), 2) for q in (0.1, 1 / 3, 0.5, 2 / 3, 0.9)]}
def terc(ind, v):
    q = dist[ind]["p10/p33/p50/p67/p90"]; return None if v is None else (0 if v < q[1] else 1 if v < q[3] else 2)
latest = {"Baa - 10y (pp)": LATEST["BAA10Y"][1], "2y - fed funds (pp)": round(LATEST["DGS2"][1] - LATEST["DFF"][1], 2), "10y real yield, TIPS (%)": LATEST["DFII10"][1],
          "10y - core CPI y/y (pp)": round(LATEST["DGS10"][1] - float(M.CORECPI_YY.dropna().iloc[-1]), 2), "Unemployment - 12-month low (pp)": None, "Core CPI y/y (%)": None,
          "WTI oil y/y (%)": round(100 * (float(oil.iloc[-1]) / float(oil[oil.index <= oil.index[-1] - pd.Timedelta(days=365)].iloc[-1]) - 1), 1),
          "VIX / VIX3M": round(float(ratio.iloc[-1]), 3), "Shiller CAPE": cape_latest[1]}
res = {}
for ind in IND:
    now, fb = at(ind, NOW); r = {"now (month of the 2026 record)": now, "now fallback month": fb, "latest": latest[ind]}
    r["bear eves"] = {k: at(ind, d)[0] for k, d in BEARS.items()}; r["control eves (10-20% declines)"] = {k: at(ind, d)[0] for k, d in CONTROLS.items()}
    b = [v for v in r["bear eves"].values() if v is not None]; c = [v for v in r["control eves (10-20% declines)"].values() if v is not None]
    r["AUC bear eves above controls (0.5 = no separation)"] = round(float(np.mean([(x > y) + 0.5 * (x == y) for x in b for y in c])), 2) if b and c else None
    r["n bear / control"] = [len(b), len(c)]
    r["read vs each bear eve (same tercile of the 1999-2026 months = rhymes)"] = {k: (None if v is None or now is None else ("rhymes" if terc(ind, v) == terc(ind, now) else "differs")) for k, v in r["bear eves"].items()}
    r["read vs each control eve"] = {k: (None if v is None or now is None else ("rhymes" if terc(ind, v) == terc(ind, now) else "differs")) for k, v in r["control eves (10-20% declines)"].items()}
    r["now tercile (0 low, 1 mid, 2 high)"] = terc(ind, now); r["distribution"] = dist[ind]; res[ind] = r
out = {"record date used as today's eve": NOW, "S&P close / record": [round(float(spx.iloc[-1]), 2), round(float(spx[rec_date]), 2), str(spx.index[-1].date())],
       "bear eves": BEARS, "control eves": CONTROLS, "latest prints": {**{k: v for k, v in LATEST.items()}, "CAPE (multpl)": cape_latest, "VIX/VIX3M": [str(ratio.index[-1].date()), latest["VIX / VIX3M"]],
       "WTI front month": [str(oil.index[-1].date()), round(float(oil.iloc[-1]), 2)]}, "indicators": res}
json.dump(out, open(O / "p4.json", "w"), indent=1, default=float)
for ind, r in res.items():
    print(f"{ind:34s} now {r['now (month of the 2026 record)']} ({r['now fallback month'] or 'record month'}) latest {r['latest']} | bears {r['bear eves']} | controls {r['control eves (10-20% declines)']} | AUC {r['AUC bear eves above controls (0.5 = no separation)']} | {r['read vs each bear eve (same tercile of the 1999-2026 months = rhymes)']} | ctrl {r['read vs each control eve']} | terciles {r['distribution']['p10/p33/p50/p67/p90']}")
print(out["record date used as today's eve"], out["S&P close / record"], out["latest prints"])
