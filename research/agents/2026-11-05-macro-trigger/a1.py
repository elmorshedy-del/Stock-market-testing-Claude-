"""Amendment A1: surprise-conditioned gap / follow-through on jobs and CPI days (see README). Usage: python a1.py <DIX.csv>"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-11-05-liquidity-cycle"))
from common import yahoo, gex_pct
H = Path(__file__).resolve().parent; O = H / "out"; rng = np.random.default_rng(23)

spy = yahoo("SPY", "2009-01-01"); vix = yahoo("^VIX", "2009-01-01").close
d = spy[["open", "close"]].copy(); d["r"] = d.close.pct_change()
d["sig"] = d.r.rolling(20).std().shift(1)
d["gap"] = d.open / d.close.shift(1) - 1; d["ft"] = d.close / d.open - 1
d["gap_s"] = d.gap / d.sig; d["ft_s"] = d.ft / d.sig
d["dd10"] = d.close / d.close.rolling(10).max() - 1
g = gex_pct(sys.argv[1]); d["gp"] = g.gp.reindex(d.index)
d["LOW"] = 1 - d.gp.shift(1); d["DROP"] = -100 * d.dd10.shift(1); d["VIX"] = vix.reindex(d.index).shift(1) / 20

rd = pd.read_csv(O / "release_dates.csv", parse_dates=["date"]); rd["ym"] = rd.date.dt.to_period("M")
main = {"jobs": set(rd[rd.release == "jobs"].groupby("ym").date.min()), "cpi": set(rd[rd.release == "cpi"].groupby("ym").date.max())}
ev = []
for typ, f in (("jobs", "nfp"), ("cpi", "corecpi")):
    x = pd.read_csv(H / "data" / f"{f}.csv"); x["date"] = pd.to_datetime(x.datetime_utc.str[:10]); x = x.dropna(subset=["actual", "forecast"]).sort_values("date")
    x["surp"] = x.actual - x.forecast
    if typ == "jobs":
        sc = x.surp.abs().rolling(24, min_periods=12).median().shift(1); x["z"] = (x.surp / sc).clip(-4, 4)
    else:
        x["z"] = (x.surp / 0.1).round(6)
    x["type"] = typ; x["main"] = x.date.isin(main[typ]); ev.append(x)
E = pd.concat(ev); match = E.groupby("type").main.mean().round(3).to_dict()
E = E[E.main].merge(d, left_on="date", right_index=True, how="inner").sort_values("date")
# out-of-sample sign: corr(z, gap_s) over prior 24 releases of the same type
E["sgn"] = np.nan
for typ in ("jobs", "cpi"):
    m = E.type == typ; zz, gg = E.loc[m, "z"], E.loc[m, "gap_s"]
    E.loc[m, "sgn"] = np.sign(zz.rolling(24, min_periods=12).corr(gg).shift(1)).values
E["s"] = E.z * E.sgn; E["sp"] = E.s.clip(lower=0); E["sm"] = E.s.clip(upper=0)
E["az"] = E.z.abs(); E["agap"] = E.gap_s.abs(); E["isjobs"] = (E.type == "jobs").astype(float)
E["az_LOW"] = E.az * E.LOW; E["sp_D"] = E.sp * E.DROP; E["sm_D"] = E.sm * E.DROP; E["g_LOW"] = E.gap_s * E.LOW
S = E[(E.date >= "2012-05-01") & (E.date < "2026-11-01")].dropna(subset=["gap_s", "ft_s", "LOW", "DROP", "VIX", "z", "s"]).copy()
S["year"] = S.date.dt.year

SPEC = {"A": ("agap", ["isjobs", "az", "LOW", "az_LOW", "VIX"], "az_LOW"),
        "B": ("gap_s", ["isjobs", "sp", "sm", "sp_D", "sm_D", "DROP", "VIX"], ("sp_D", "sm_D")),
        "C": ("ft_s", ["isjobs", "gap_s", "g_LOW", "LOW", "DROP", "VIX"], "g_LOW")}
def stat(X, y, xs, key):
    xs = [c for c in xs if X[c].std() > 0]
    m = sm.OLS(X[y], sm.add_constant(X[xs])).fit(cov_type="HC3")
    if isinstance(key, tuple):
        L = np.zeros(len(m.params)); L[list(m.params.index).index(key[0])] = 1; L[list(m.params.index).index(key[1])] = -1
        t = m.t_test(L); return float(np.squeeze(t.effect)), float(np.squeeze(t.tvalue)), m
    return float(m.params[key]), float(m.tvalues[key]), m
def fit(X, h):
    y, xs, key = SPEC[h]; est, tv, m = stat(X, y, xs, key)
    from scipy.stats import norm
    p_hc3 = float(1 - norm.cdf(tv))
    yrs = X.year.unique(); bs = []
    for _ in range(2000):
        pick = rng.choice(yrs, len(yrs)); Xb = pd.concat([X[X.year == yy] for yy in pick])
        try: bs.append(stat(Xb, y, xs, key)[0])
        except Exception: pass
    bs = np.array(bs); p_bs = float((bs <= 0).mean())
    out = {"n": int(len(X)), "estimate": round(est, 4), "t (HC3)": round(tv, 2), "p HC3": round(p_hc3, 4), "p year-bootstrap": round(p_bs, 4),
           "p used (larger)": round(max(p_hc3, p_bs), 4), "boot 90% CI": [round(float(np.percentile(bs, 5)), 4), round(float(np.percentile(bs, 95)), 4)],
           "coefs": {k: [round(float(v), 4), round(float(m.tvalues[k]), 2)] for k, v in m.params.items()}}
    return out
R = {"match rate FF->FRED main dates": match, "sample": [str(S.date.min().date()), str(S.date.max().date())], "n by type": S.type.value_counts().to_dict()}
for h in "ABC": R[h] = fit(S, h)
ps = {h: R[h]["p used (larger)"] for h in "ABC"}; order = sorted(ps, key=ps.get); run = 0; R["Holm"] = {}
for i, k in enumerate(order): run = max(run, min(1, (3 - i) * ps[k])); R["Holm"][k] = {"adj": round(run, 4), "PASS": bool(run < 0.05)}
# secondary: B relief intercept b5 (DROP)
R["B secondary b5 DROP (gap_s per 1% drawdown)"] = R["B"]["coefs"].get("DROP")
# robustness
rob = {}
subsets = {"jobs only": S[S.type == "jobs"], "cpi only": S[S.type == "cpi"], "2012-19": S[S.year <= 2019], "2020-26": S[S.year >= 2020],
           "ex Mar-Apr 2020 & Apr 2025": S[~(((S.date >= "2020-03-01") & (S.date < "2020-05-01")) | ((S.date >= "2025-04-01") & (S.date < "2025-05-01")))]}
for nm, X in subsets.items():
    rob[nm] = {h: (lambda o: {"n": o["n"], "est": o["estimate"], "t": o["t (HC3)"], "p": o["p used (larger)"]})(fit(X, h)) for h in "ABC"}
Sb = S.copy(); Sb["LOW"] = (Sb.LOW >= 0.70).astype(float); Sb["DROP"] = (Sb.DROP >= 3).astype(float)
Sb["az_LOW"] = Sb.az * Sb.LOW; Sb["sp_D"] = Sb.sp * Sb.DROP; Sb["sm_D"] = Sb.sm * Sb.DROP; Sb["g_LOW"] = Sb.gap_s * Sb.LOW
rob["binary (GEX<=30th, drop>=3%)"] = {h: (lambda o: {"n": o["n"], "est": o["estimate"], "t": o["t (HC3)"], "p": o["p used (larger)"]})(fit(Sb, h)) for h in "ABC"}
R["robustness"] = rob
# control: C on non-release days
rel_dates = set(E.date)
N = d[(d.index >= "2012-05-01") & (d.index < "2026-11-01") & ~d.index.isin(rel_dates)].dropna(subset=["gap_s", "ft_s", "LOW", "DROP", "VIX"]).copy()
N["isjobs"] = 0.0; N["g_LOW"] = N.gap_s * N.LOW; N["year"] = N.index.year
mN = sm.OLS(N.ft_s, sm.add_constant(N[["gap_s", "g_LOW", "LOW", "DROP", "VIX"]])).fit(cov_type="HC3")
R["C control non-release days"] = {"n": int(len(N)), "g_LOW": [round(float(mN.params.g_LOW), 4), round(float(mN.tvalues.g_LOW), 2)], "gap_s": [round(float(mN.params.gap_s), 4), round(float(mN.tvalues.gap_s), 2)]}
# Friday descriptive
J = E[E.type == "jobs"].tail(24)
R["FRIDAY: last 24 payrolls"] = {"corr(z, gap_s)": round(float(J.z.corr(J.gap_s)), 3), "sign used for Nov 6": float(np.sign(J.z.corr(J.gap_s))),
    "last 6": {str(r.date.date()): {"z": round(float(r.z), 2), "gap %": round(100 * r.gap, 2), "open->close %": round(100 * r.ft, 2)} for r in J.tail(6).itertuples()}}
cpiR = E[E.type == "cpi"].tail(24); R["CPI last 24 corr(z, gap_s)"] = round(float(cpiR.z.corr(cpiR.gap_s)), 3)
R["state now (Nov 5 close, live)"] = {"DROP %": round(float(-100 * d.dd10.iloc[-1]), 2), "LOW (Nov 4 GEX)": round(float(1 - g.gp.iloc[-1]), 3), "sigma20 %": round(100 * float(d.r.tail(20).std()), 2)}
json.dump(R, open(O / "a1.json", "w"), indent=1, default=float); print(json.dumps(R, indent=1, default=float))
