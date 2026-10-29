"""Part A, index calendar mechanics (pre-registered @ 89dcdd6). Daily log returns; year-block bootstrap (10,000); Holm across A1-A8.
Usage: python partA.py <scratchpad> -> out/partA.json, out/profiles.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; CX = S / "ctx"
rng = np.random.default_rng(0); B = 10000


def yahoo(p):
    r = json.load(open(p))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    c = pd.Series(q["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
    c = c[~c.index.duplicated(keep="last")]; c = c[c > 0]
    return np.log(c).diff().dropna()


def nth_friday(y, m, n):
    return pd.date_range(f"{y}-{m:02d}-01", periods=31, freq="D").to_series().loc[lambda s: (s.dt.month == m) & (s.dt.dayofweek == 4)].iloc[n - 1]


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); adj = np.empty_like(ps); run = 0
    for i, k in enumerate(o):
        run = max(run, (len(ps) - i) * ps[k]); adj[k] = min(1, run)
    return adj


def pboot(bs):
    bs = bs[~np.isnan(bs)]; return float(min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1 / len(bs)))


def yboot(df, stat):
    """df has a 'yr' column; resample years with replacement."""
    yrs = df.yr.unique(); groups = {y: df[df.yr == y] for y in yrs}; out = np.empty(B)
    for i in range(B):
        out[i] = stat(pd.concat([groups[y] for y in rng.choice(yrs, len(yrs))], ignore_index=True))
    return out


def tag(lr):
    d = pd.DataFrame({"r": lr}); d["yr"] = d.index.year; d["m"] = d.index.month
    tf = {(y, m): nth_friday(y, m, 3) for y in range(d.yr.min(), d.yr.max() + 1) for m in range(1, 13)}
    d["tf"] = [tf[(y, m)] for y, m in zip(d.yr, d.m)]
    d["late_sep"] = (d.m == 9) & (d.index > d.tf)
    return d


spx = tag(yahoo(S / "long" / "GSPC.json"))
diff_ls = lambda x: x[x.late_sep].r.mean() - x[~x.late_sep].r.mean()
R = {}
# A1
a1 = spx[(spx.yr >= 1928) & (spx.yr <= 1949)]
R["A1 pre-1950 S&P: late-Sep minus other days (bp/day)"] = {"est": 1e4 * diff_ls(a1), "boot": 1e4 * yboot(a1, diff_ls), "n_late": int(a1.late_sep.sum())}
# A2 pooled other markets
parts = []
for f, lo in (("%5EGDAXI.json", 1988), ("%5EFTSE.json", 1984), ("%5EN225.json", 1970)):
    x = tag(yahoo(CX / "intl" / f)); x = x[(x.yr >= lo) & (x.yr <= 2025)]; x["idx"] = f.split("5E")[1].split(".")[0]; parts.append(x)
intl = pd.concat(parts)
R["A2 DAX+FTSE+Nikkei: late-Sep minus other days (bp/day)"] = {"est": 1e4 * diff_ls(intl), "boot": 1e4 * yboot(intl, diff_ls),
    "by_index": {k: 1e4 * diff_ls(g) for k, g in intl.groupby("idx")}}
# A3 era
e1, e2 = spx[(spx.yr >= 1950) & (spx.yr <= 1982)], spx[(spx.yr >= 1983) & (spx.yr <= 2025)]
b1, b2 = yboot(e1, diff_ls), yboot(e2, diff_ls)
R["A3 late-Sep contrast, 1983-2025 minus 1950-1982 (bp/day)"] = {"est": 1e4 * (diff_ls(e2) - diff_ls(e1)), "boot": 1e4 * (b2 - b1),
    "1950-1982": 1e4 * diff_ls(e1), "1983-2025": 1e4 * diff_ls(e2)}
# A4 quarterly vs monthly post-expiry week x era
def post5(x):
    rows = []
    for (y, m), g in x.groupby(["yr", "m"]):
        nxt = x[x.index > g.tf.iloc[0]].iloc[:5]
        rows.append({"yr": y, "q": m in (3, 6, 9, 12), "r": nxt.r.mean()})
    return pd.DataFrame(rows)
p1, p2 = post5(e1), post5(e2)
qm = lambda d: d[d.q].r.mean() - d[~d.q].r.mean()
R["A4 (quarterly - monthly) post-expiry week, 1983+ minus 1950-82 (bp/day)"] = {"est": 1e4 * (qm(p2) - qm(p1)), "boot": 1e4 * (yboot(p2, qm) - yboot(p1, qm)),
    "1950-1982": 1e4 * qm(p1), "1983-2025": 1e4 * qm(p2)}
# A5 clock race
q = e2[e2.m.isin([3, 6, 9, 12])].copy()
q["between"] = (q.index.day >= 16) & (q.index <= q.tf); q["after"] = q.index > q.tf
a5 = lambda x: x[x.between].r.mean() - x[x.after].r.mean()
R["A5 clock race: (16th..3rd Fri) minus (after 3rd Fri), quarterly months 1983+ (bp/day)"] = {"est": 1e4 * a5(q), "boot": 1e4 * yboot(q, a5),
    "between": 1e4 * q[q.between].r.mean(), "after": 1e4 * q[q.after].r.mean(), "ordinary days 1983+": 1e4 * e2[~e2.m.isin([3, 6, 9, 12])].r.mean(),
    "n_between": int(q.between.sum()), "n_after": int(q.after.sum())}
# A6 Japan's clock
nk = tag(yahoo(CX / "intl" / "%5EN225.json")); nk = nk[(nk.yr >= 1989) & (nk.yr <= 2025)]
rows = []
for (y, m), g in nk[nk.m.isin([3, 6, 9, 12])].groupby(["yr", "m"]):
    sq, us = nth_friday(y, m, 2), nth_friday(y, m, 3)
    rows.append({"yr": y, "after_us": nk[nk.index > us].r.iloc[:5].mean(), "after_sq": nk[nk.index > sq].r.iloc[:5].mean()})
a6d = pd.DataFrame(rows); a6 = lambda d: d.after_us.mean() - d.after_sq.mean()
R["A6 Nikkei: 5 sessions after US 3rd Fri minus after own SQ (bp/day)"] = {"est": 1e4 * a6(a6d), "boot": 1e4 * yboot(a6d, a6),
    "after_us": 1e4 * a6d.after_us.mean(), "after_sq": 1e4 * a6d.after_sq.mean(), "nikkei all days": 1e4 * nk.r.mean()}
# A7 dose: GEX roll-off vs S&P sessions 2-6 after expiry (session 1 holds the 'after' GEX reading, so it is excluded to avoid spot contamination)
dix = pd.read_csv(S / "late28" / "DIX.csv", parse_dates=["date"]).set_index("date")
sp = spx.r; rows = []
for y in range(2011, 2026):
    for m in range(1, 13):
        tf = nth_friday(y, m, 3); bef = dix.index[dix.index < tf]; aft = dix.index[dix.index > tf]
        if not len(bef) or not len(aft) or bef[-1] < pd.Timestamp("2011-06-01"): continue
        nxt = sp[sp.index > aft[0]].iloc[:5]
        if len(nxt) < 5: continue
        rows.append({"yr": y, "dgex": dix.gex[aft[0]] - dix.gex[bef[-1]], "ret": nxt.sum()})
a7d = pd.DataFrame(rows); sp_ = lambda d: stats.spearmanr(d.dgex, d.ret)[0]
R["A7 dose: Spearman(GEX roll-off, S&P sessions 2-6 after expiry)"] = {"est": sp_(a7d), "boot": yboot(a7d, sp_), "n": len(a7d)}
# A8 liquidity drain: weekly TGA change vs same-week S&P
rows = []
for f in ("tga1.json", "tga2.json"): rows += json.load(open(CX / f))["data"]
T = pd.DataFrame(rows); T["date"] = pd.to_datetime(T.record_date)
cl = T[T.account_type.isin(["Federal Reserve Account", "Treasury General Account (TGA)"])].assign(v=lambda d: pd.to_numeric(d.close_today_bal, errors="coerce"))
cl2 = T[T.account_type == "Treasury General Account (TGA) Closing Balance"].assign(v=lambda d: pd.to_numeric(d.open_today_bal, errors="coerce"))
tga = pd.concat([cl, cl2]).groupby("date").v.last().sort_index(); tga = tga[tga.index >= "2009-01-01"]
spc = np.exp(spx.r.cumsum()); wk = pd.DataFrame({"tga": tga.resample("W-WED").last(), "spx": spc.resample("W-WED").last()}).dropna()
wk = wk[wk.index <= "2025-12-31"]; wk["dtga"] = wk.tga.diff(); wk["ret"] = np.log(wk.spx).diff(); wk = wk.dropna(); wk["yr"] = wk.index.year
R["A8 Spearman(weekly TGA change, same-week S&P return), 2009-2025"] = {"est": stats.spearmanr(wk.dtga, wk.ret)[0], "boot": yboot(wk, lambda d: stats.spearmanr(d.dtga, d.ret)[0]), "n": len(wk)}
pred = {"A1": 0, "A2": -1, "A3": -1, "A4": -1, "A5": 1, "A6": 0, "A7": 1, "A8": -1}
out = {}
for (k, v), h in zip(R.items(), holm([pboot(v["boot"]) for v in R.values()])):
    bs = v.pop("boot"); v["ci95"] = [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]; v["p"] = pboot(bs); v["p_holm"] = float(h)
    v["pass"] = bool(h < 0.05); p = pred[k[:2]]; v["predicted_sign"] = p; v["sign_as_predicted"] = (None if p == 0 else bool(np.sign(v["est"]) == p)); out[k] = v
json.dump(out, open(HERE / "out" / "partA.json", "w"), indent=1, default=float)
# profiles for the figure: mean cumulative return by session relative to the 3rd Friday, quarterly vs monthly, two eras; and September day-by-day
prof = {}
for nm, era in (("1950-1982", e1), ("1983-2025", e2)):
    for qq in (True, False):
        acc = {}
        for (y, m), g in era[era.m.isin([3, 6, 9, 12]) == qq].groupby(["yr", "m"]):
            tfi = era.index.searchsorted(g.tf.iloc[0], side="right")
            for k in range(-10, 11):
                j = tfi + k
                if 0 <= j < len(era): acc.setdefault(k, []).append(era.r.iloc[j])
        prof[f"{nm} {'quarterly' if qq else 'monthly'}"] = {k: 1e4 * float(np.mean(v)) for k, v in acc.items()}
prof["S&P 1928-1949 late-Sep bp/day"] = 1e4 * a1[a1.late_sep].r.mean(); prof["S&P 1928-1949 other bp/day"] = 1e4 * a1[~a1.late_sep].r.mean()
json.dump(prof, open(HERE / "out" / "profiles.json", "w"), indent=1)
pd.set_option("display.width", 250)
print(pd.DataFrame(out).T.drop(columns=[c for c in ("by_index",) if c in pd.DataFrame(out).T]).to_string())
print("A2 by index:", {k: round(v, 2) for k, v in out["A2 DAX+FTSE+Nikkei: late-Sep minus other days (bp/day)"]["by_index"].items()})
