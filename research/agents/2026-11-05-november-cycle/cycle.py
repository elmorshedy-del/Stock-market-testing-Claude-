"""November rescue + monthly cycle by regime (pre-registered, see README). Usage: python cycle.py <DIX.csv>"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-11-05-liquidity-cycle"))
from common import yahoo, gex_pct

OUT = Path(__file__).resolve().parent / "out"; OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(7)
spx = yahoo("^GSPC", "1950-01-01").close
ndx = yahoo("^NDX", "1985-10-01").close
d = pd.DataFrame({"spx": spx})
d["r"] = d.spx.pct_change(); d["ma200"] = d.spx.rolling(200).mean(); d["hi252"] = d.spx.rolling(252).max()
d["absr"] = d.r.abs(); d["mv60"] = d.absr.rolling(60).mean()
d["ratio"] = (ndx / d.spx).reindex(d.index)
d["ym"] = d.index.to_period("M"); d["k"] = d.groupby("ym").cumcount() + 1
g = gex_pct(sys.argv[1]) if len(sys.argv) > 1 else None
if g is not None: d["gp"] = g.gp.reindex(d.index)

rows = []; months = list(d.ym.unique())
for i, ym in enumerate(months[1:], 1):
    m = d[d.ym == ym]; p = d[d.ym == months[i - 1]]
    if len(m) < 4: continue
    pc, pr = p.spx.iloc[-1], p.ratio.iloc[-1]
    tf = pd.date_range(ym.to_timestamp(), ym.to_timestamp(how="end"), freq="W-FRI")[2]
    opex = m.index[m.index <= tf].max(); mon = tf - pd.Timedelta(days=4)
    seg = np.where(m.k <= 4, "S1", np.where(m.index < mon, "S2", np.where(m.index <= opex, "S3", "S4")))
    base = p.mv60.iloc[-1]
    complete = ym < pd.Period("2026-11", "M")
    rw = dict(ym=str(ym), year=ym.year, month=ym.month, complete=complete,
              start=m.spx.iloc[3] / pc - 1, rest=(m.spx.iloc[-1] / m.spx.iloc[3] - 1) if complete else np.nan,
              full=(m.spx.iloc[-1] / pc - 1) if complete else np.nan,
              bull=(pc >= p.ma200.iloc[-1]) if not np.isnan(p.ma200.iloc[-1]) else np.nan,
              dd=pc / p.hi252.iloc[-1] - 1,
              rstart=m.ratio.iloc[3] / pr - 1 if pd.notna(pr) else np.nan,
              rrest=(m.ratio.iloc[-1] / m.ratio.iloc[3] - 1) if (complete and pd.notna(pr)) else np.nan,
              ndx_rest=np.nan)
    for s in ("S1", "S2", "S3", "S4"):
        x = m[seg == s]
        rw[f"r_{s}"] = x.r.mean() if len(x) else np.nan
        rw[f"mv_{s}"] = x.absr.mean() / base if len(x) and base > 0 else np.nan
        if g is not None: rw[f"gp_{s}"] = x.gp.mean() if len(x) else np.nan
    rw["r_rest"] = m[m.k >= 5].r.mean() if complete else np.nan
    rows.append(rw)
M = pd.DataFrame(rows)
nd = ndx.reindex(d.index)
for j, rw in M.iterrows():
    if rw.complete and rw.year >= 1986:
        m = nd[d.ym == pd.Period(rw.ym, "M")]
        if len(m) > 4 and m.notna().all(): M.loc[j, "ndx_rest"] = m.iloc[-1] / m.iloc[3] - 1
M.to_csv(OUT / "months.csv", index=False)

C = M[M.complete]
q_start = C.start.quantile(0.2); q_rstart = C.rstart.dropna().quantile(0.2)
C = C.assign(weak=C.start <= q_start, trot=C.rstart <= q_rstart)
pct = lambda x: round(100 * float(x), 2)
R = {"as of": "2026-11-05 intraday (Nov 2026 start is LIVE, provisional)", "months complete": int(len(C)),
     "weak start threshold (bottom 20%)": pct(q_start), "tech-rotation threshold (bottom 20%, 1985-)": pct(q_rstart)}

# N1 Novembers
N = C[C.month == 11]
bearN = N[N.bull == False]
R["N1"] = {"Novembers": int(len(N)), "share >= -1%": round(float((N.full >= -0.01).mean()), 3),
           "share up": round(float((N.full > 0).mean()), 3), "median %": pct(N.full.median()),
           "bear Novembers": int(len(bearN)), "bear share >= -1%": round(float((bearN.full >= -0.01).mean()), 3) if len(bearN) else None,
           "losers (< -1%)": {int(r.year): {"Nov %": pct(r.full), "bull": bool(r.bull) if pd.notna(r.bull) else None, "dd %": pct(r.dd)} for r in N[N.full < -0.01].itertuples()},
           "all months share >= -1%": round(float((C.full >= -0.01).mean()), 3)}

# P1 November rescue after weak start
W = C[C.weak]
isnov = (W.month == 11).values; rest = W.rest.values
obs = rest[isnov].mean() - rest[~isnov].mean()
perm = np.array([(lambda s: rest[s].mean() - rest[~s].mean())(rng.permutation(isnov)) for _ in range(10000)])
p1 = float((perm >= obs).mean())
R["P1"] = {"weak-start Novembers": int(isnov.sum()), "weak-start other months": int((~isnov).sum()),
           "Nov rest mean %": pct(rest[isnov].mean()), "Nov rest share up": round(float((rest[isnov] > 0).mean()), 3),
           "other rest mean %": pct(rest[~isnov].mean()), "other rest share up": round(float((rest[~isnov] > 0).mean()), 3),
           "all months rest mean %": pct(C.rest.mean()), "diff %": pct(obs), "p (one-sided, permutation)": p1,
           "eligible (>=8 Novembers)": bool(isnov.sum() >= 8),
           "weak-start Novembers": {int(r.year): {"start %": pct(r.start), "rest %": pct(r.rest), "full %": pct(r.full), "bull": bool(r.bull) if pd.notna(r.bull) else None} for r in W[W.month == 11].itertuples()}}

# N3 tech-rotation Novembers
T = C[(C.month == 11) & C.trot]
R["N3"] = {int(r.year): {"SPX start %": pct(r.start), "NDX/SPX start %": pct(r.rstart), "SPX rest %": pct(r.rest), "NDX rest %": pct(r.ndx_rest),
                         "NDX/SPX rest %": pct(r.rrest), "SPX Nov %": pct(r.full), "bull": bool(r.bull)} for r in T.itertuples()}
R["N3 all months with tech-rotation start"] = {"n": int(C.trot.sum()), "ratio rest mean %": pct(C[C.trot].rrest.mean()), "ratio rest share up": round(float((C[C.trot].rrest > 0).mean()), 3),
                                               "all months ratio rest mean %": pct(C.rrest.mean())}

# P2-P4 monthly cycle (one obs per month)
def test(x, alt, unit):
    x = np.asarray(x.dropna(), float); t = stats.ttest_1samp(x, 0, alternative=alt).pvalue
    b = np.array([rng.choice(x, len(x)).mean() for _ in range(10000)])
    pb = float((b <= 0).mean()) if alt == "greater" else float((b >= 0).mean())
    return {"n": int(len(x)), f"mean diff ({unit})": round(float(x.mean()) * (1e4 if unit == "bp/day" else 1), 3),
            "p t": float(t), "p boot": pb, "p used (larger)": max(float(t), pb)}
CB = C[C.bull == True]; CR = C[C.bull == False]
spec = {"P2 bull: S1 > rest (daily ret)": (lambda X: X.r_S1 - X.r_rest, "bull", "greater", "bp/day"),
        "P3 bull: movement S1 > S3": (lambda X: X.mv_S1 - X.mv_S3, "bull", "greater", "x normal"),
        "P4 bear: S1 < rest (daily ret)": (lambda X: X.r_S1 - X.r_rest, "bear", "less", "bp/day")}
for name, (f, reg, alt, unit) in spec.items():
    X = CB if reg == "bull" else CR
    R[name] = test(f(X), alt, unit)
    R[name]["1950-1999"] = test(f(X[X.year < 2000]), alt, unit); R[name]["2000-2026"] = test(f(X[X.year >= 2000]), alt, unit)
ps = {"P1": p1, **{k[:2]: R[k]["p used (larger)"] for k in spec}}
order = sorted(ps, key=ps.get); m_ = len(ps); adj, run = {}, 0
for i, k in enumerate(order): run = max(run, min(1, (m_ - i) * ps[k])); adj[k] = round(run, 4)
R["Holm"] = {k: {"p": round(ps[k], 4), "adj": adj[k], "PASS": bool(adj[k] < 0.05 and (k != "P1" or R["P1"]["eligible (>=8 Novembers)"]))} for k in ps}

# Segment profile (descriptive)
prof = {}
for reg, X in (("bull", CB), ("bear", CR)):
    prof[reg] = {s: {"ret bp/day": round(1e4 * X[f"r_{s}"].mean(), 2), "movement x": round(X[f"mv_{s}"].mean(), 3),
                     **({"GEX pct (2011-)": round(X[X.year >= 2012][f"gp_{s}"].mean(), 3)} if g is not None else {})} for s in ("S1", "S2", "S3", "S4")}
    prof[reg]["n months"] = int(len(X))
R["segment profile"] = prof

# Q3 weak start -> rest by regime
R["Q3"] = {reg: {"n": int(len(X[X.weak])), "rest mean %": pct(X[X.weak].rest.mean()), "rest share up": round(float((X[X.weak].rest > 0).mean()), 3),
                 "all-months rest mean %": pct(X.rest.mean()), "all-months share up": round(float((X.rest > 0).mean()), 3)} for reg, X in (("bull", CB), ("bear", CR))}

t = M[M.ym == "2026-11"].iloc[0]
R["TODAY Nov 2026 (live)"] = {"SPX start %": pct(t.start), "start pct rank": round(float((C.start < t.start).mean()), 3), "weak": bool(t.start <= q_start),
                             "NDX/SPX start %": pct(t.rstart), "ratio start pct rank": round(float((C.rstart.dropna() < t.rstart).mean()), 3), "tech-rotation": bool(t.rstart <= q_rstart),
                             "bull (Oct close vs 200d)": bool(t.bull), "dd from 252d high %": pct(t.dd), "last SPX": round(float(d.spx.iloc[-1]), 2), "last date": str(d.index[-1].date())}
json.dump(R, open(OUT / "cycle.json", "w"), indent=1, default=float)
print(json.dumps(R, indent=1, default=float))
