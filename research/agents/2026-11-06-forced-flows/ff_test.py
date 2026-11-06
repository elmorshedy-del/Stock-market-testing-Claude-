"""Forced-flows test (pre-registered @ 0273b35). LETF close-rebalancing identity F = sum L(L-1) A R, square-root impact x = sigma*sign(F)*sqrt(|F|/V),
outcome r = 15:30 -> official close. Usage: python ff_test.py -> out/ff.json"""
import json, numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import spearmanr
H = Path(__file__).resolve().parent; D = H / "data"; O = H / "out"; TD = Path("/tmp/claude-0/-home-user-genovy/4a459aba-63bd-54e9-abd7-2cbbef04a1e9/scratchpad/thesis/dl")
U = json.load(open(D / "universe.json")); LEV, REF = U["LEV"], U["REF"]; Q = {q["symbol"]: q for q in json.load(open(D / "letf_quote.json"))["quoteResponse"]["result"]}
DL = pd.read_parquet(D / "daily.parquet"); M5 = pd.read_parquet(D / "m5.parquet"); rng = np.random.default_rng(611)
spv, spc = pd.read_parquet(TD / "daily_vol.parquet"), pd.read_parquet(TD / "daily_close.parquet"); spv.index = pd.to_datetime(spv.index); spc.index = pd.to_datetime(spc.index)
sp500 = [s.replace(".", "-") for s in pd.read_csv(TD / "sp500.csv").iloc[:, 0]]
def dollar_vol(syms):
    parts = []
    for s in syms:
        if s in spv.columns: parts.append((spv[s] * spc[s]).rename(s))
        elif (s, "close") in DL.columns: parts.append((DL[(s, "close")] * DL[(s, "volume")]).rename(s))
    return pd.concat(parts, axis=1).sum(axis=1, min_count=1)
def ref_of(u): return REF.get(u, u)
def clean_close(ref):
    """Daily closes with the 5-minute window overwritten by each day's last 5-minute close (equal to the official close where both exist;
    fixes a Yahoo daily glitch: SOXX closes on 2026-11-02..04 came back about 3x too high)."""
    m = M5[ref].dropna()["close"]; last = m.groupby(m.index.normalize().tz_localize(None)).last(); return last.combine_first(DL[(ref, "close")].dropna()).sort_index()
days = sorted(set(M5.index.normalize().tz_localize(None))); res = {}
def build(const_aum=False):
    rows = []
    for u, funds in LEV.items():
        ref = ref_of(u); c = clean_close(ref); lr = np.log(c).diff(); sig = lr.rolling(20, min_periods=15).std().shift(1)
        V = (dollar_vol(sp500) if u == "SPX" else dollar_vol(U["NDX"]) if u == "NDX" else dollar_vol(U["SEMIS"]) if u == "SEMIS" else DL[(u, "close")] * DL[(u, "volume")]).rolling(20, min_periods=15).mean().shift(1)
        G = 0
        for f, L in funds.items():
            q = Q.get(f); fc = DL[(f, "close")].dropna() if (f, "close") in DL.columns else None
            if q is None or q.get("netAssets") is None or fc is None: continue
            A = pd.Series(float(q["netAssets"]), index=fc.index) if const_aum else float(q["netAssets"]) * fc / float(q["regularMarketPrice"])
            G = G + L * (L - 1) * A.shift(1)
        m = M5[ref].dropna(); m = m[m.index.time == pd.Timestamp("15:25").time()]["close"]; m.index = m.index.normalize().tz_localize(None)
        for d in days:
            if d not in m.index or d not in c.index: continue
            i = c.index.get_loc(d)
            if i == 0: continue
            pc, cl, p1530 = c.iloc[i - 1], c.iloc[i], m.loc[d]; R, r, Dd = p1530 / pc - 1, cl / p1530 - 1, cl / pc - 1
            g, v, s = float(G.loc[d]) if d in G.index else np.nan, float(V.loc[d]) if d in V.index else np.nan, float(sig.loc[d])
            F = g * R; x = s * np.sign(F) * np.sqrt(abs(F) / v)
            rows.append({"u": u, "date": d, "R": R, "r": r, "D": Dd, "G": g, "V": v, "sigma": s, "x": x, "psi": g / v})
    return pd.DataFrame(rows).dropna()
def tests(df):
    dts = sorted(df.date.unique()); ins_d, oos_d = set(dts[:30]), set(dts[30:]); I, O_ = df[df.date.isin(ins_d)], df[df.date.isin(oos_d)]
    Y = (I.x * I.r).sum() / (I.x ** 2).sum(); B = (I.R * I.r).sum() / (I.R ** 2).sum()
    r2 = lambda d, pred: 1 - ((d.r - pred) ** 2).sum() / (d.r ** 2).sum()
    obs_c = np.corrcoef(O_.x, O_.r)[0, 1]; obs_d = r2(O_, Y * O_.x) - r2(O_, B * O_.R); od = sorted(oos_d); bc, bd = [], []
    g = {d: O_[O_.date == d] for d in od}
    for _ in range(4000):
        smp = pd.concat([g[od[k]] for k in rng.integers(0, len(od), len(od))]); bc.append(np.corrcoef(smp.x, smp.r)[0, 1]); bd.append(r2(smp, Y * smp.x) - r2(smp, B * smp.R))
    return {"n in/oos": [len(I), len(O_)], "Y (in-sample impact constant)": round(float(Y), 3), "beta momentum (in-sample)": round(float(B), 4),
            "H-FF1 oos corr(x, r)": round(float(obs_c), 3), "H-FF1 one-sided p": round(float(np.mean(np.array(bc) <= 0)), 4), "H-FF1 90% CI": [round(float(np.percentile(bc, 5)), 3), round(float(np.percentile(bc, 95)), 3)],
            "oos R2 flow": round(float(r2(O_, Y * O_.x)), 4), "oos R2 momentum": round(float(r2(O_, B * O_.R)), 4), "H-FF2 dR2 (flow - momentum)": round(float(obs_d), 4), "H-FF2 one-sided p": round(float(np.mean(np.array(bd) <= 0)), 4)}
df = build(); res["main"] = tests(df); res["sensitivity: constant AUM"] = tests(build(const_aum=True))
per = []
for u, d in df.groupby("u"):
    b = (d.R * d.r).sum() / (d.R ** 2).sum(); per.append({"u": u, "end-of-day momentum slope b": round(float(b), 4), "psi = sum L(L-1)A / V": round(float(d.psi.mean()), 4), "n": len(d),
                                                      "corr(R, r)": round(float(np.corrcoef(d.R, d.r)[0, 1]), 3)})
P = pd.DataFrame(per); rho = spearmanr(P["end-of-day momentum slope b"], P["psi = sum L(L-1)A / V"]).correlation
perm = [spearmanr(rng.permutation(P["end-of-day momentum slope b"].values), P["psi = sum L(L-1)A / V"]).correlation for _ in range(10000)]
res["H-FF3 per underlying"] = P.sort_values("psi = sum L(L-1)A / V", ascending=False).to_dict("records"); res["H-FF3 Spearman rho"] = round(float(rho), 3); res["H-FF3 one-sided permutation p"] = round(float(np.mean(np.array(perm) >= rho)), 4)
# ---- descriptive: Nov 5 decomposition, and next-morning reversal (exploratory)
Yall = float((df.x * df.r).sum() / (df.x ** 2).sum()); res["Y (all 60 sessions)"] = round(Yall, 3); n5 = df[df.date == pd.Timestamp("2026-11-05")]; dec = []
for _, z in n5.iterrows():
    Ff = z.G * z.D; dec.append({"u": z.u, "full-day move %": round(100 * z.D, 2), "forced close rebalancing $bn": round(Ff / 1e9, 2), "as % of daily $ volume": round(100 * abs(Ff) / z.V, 2),
                                "predicted 15:30->close %": round(100 * Yall * z.x, 2), "actual 15:30->close %": round(100 * z.r, 2)})
res["Nov 5 decomposition"] = sorted(dec, key=lambda k: k["forced close rebalancing $bn"])
rev = []
for u, d in df.groupby("u"):
    ref = ref_of(u); m = M5[ref].dropna()["close"]; first = m.groupby(m.index.normalize().tz_localize(None)).first()
    for _, z in d.iterrows():
        nx = first.index[first.index > z.date]
        if len(nx): rev.append((z.x, first.loc[nx[0]] / clean_close(ref).loc[z.date] - 1))
rv = np.array(rev); res["exploratory: corr(x, next-morning first-5-min vs close)"] = round(float(np.corrcoef(rv[:, 0], rv[:, 1])[0, 1]), 3)
last = df.sort_values("date").groupby("u").tail(1); rule = {}
for _, z in last.iterrows():
    rule[z.u] = {f"{int(100*R):+d}% by 15:30": round(float(100 * Yall * z.sigma * np.sign(R) * np.sqrt(z.psi * abs(R))), 2) for R in (-0.05, -0.03, -0.02, -0.01, 0.01, 0.02, 0.03)}
    rule[z.u]["psi"] = round(float(z.psi), 3); rule[z.u]["sigma %"] = round(float(100 * z.sigma), 2)
res["today's 15:30 rule: predicted 15:30->close % given the move so far"] = rule
json.dump(res, open(O / "ff.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items() if k not in ("today's 15:30 rule: predicted 15:30->close % given the move so far",)}, indent=1, default=str)[:6000])
