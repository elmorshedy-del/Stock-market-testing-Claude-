"""S2 (exploratory, announced with A1 @ 77b4866; not a test): re-run the channels-deep P2 event rule (trailing 3y z <= -1.75, 15y z > -1,
>=120 sessions apart) on sign-randomized S&P surrogates (M0: same daily |moves|, no direction memory). Is "channel broken -> 10%+ fall
within a year" more than volatility clustering produces? Usage: python s2_surrogate_p2.py -> out/s2.json"""
import json, importlib.util, numpy as np
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
src = open(H / "physics.py").read(); exec(src[src.index("def rolling_z_log"):src.index("def betas")])
s = lc.yahoo("^GSPC", "1927-12-01").close; s = s[s.index >= "1950-01-01"]; y = np.log(s.values); r = np.diff(y); mu = r.mean(); rng = np.random.default_rng(11); NS = 500
def stats(yy):
    P = np.exp(yy); N = len(P); zs, zl = rolling_z_log(yy, 756), rolling_z_log(yy, 3780); cond = (zs <= -1.75) & (zl > -1.0); ev = []
    for i in np.where(cond)[0]:
        if not cond[max(0, i - 120):i].any(): ev.append(i)
    done = [i for i in ev if i + 252 < N]; m = []
    for i in done:
        pk = P[max(0, i - 251):i + 1].max(); seg = P[i + 1:i + 253]; rm = np.maximum.accumulate(np.concatenate([[pk], seg]))[1:]; m.append(float((seg / rm - 1).min()))
    m = np.array(m); return len(done), (m <= -0.10).mean() if len(m) else np.nan, (m <= -0.20).mean() if len(m) else np.nan
obs = stats(y); sur = np.array([stats(np.concatenate([[y[0]], y[0] + np.cumsum(mu + rng.choice([-1.0, 1.0], size=len(r)) * (r - mu))])) for _ in range(NS)])
ok = ~np.isnan(sur[:, 1])
out = {"observed": {"finished events": obs[0], "share fell 10%+ within a year": round(float(obs[1]), 3), "share became 20%+ bears": round(float(obs[2]), 3)},
       "surrogates (M0)": {"paths": NS, "paths with events": int(ok.sum()), "median events per path": float(np.median(sur[:, 0])),
           "share 10%+: median / 5-95%": [round(float(np.median(sur[ok, 1])), 3), round(float(np.percentile(sur[ok, 1], 5)), 3), round(float(np.percentile(sur[ok, 1], 95)), 3)],
           "share 20%+: median / 5-95%": [round(float(np.median(sur[ok, 2])), 3), round(float(np.percentile(sur[ok, 2], 5)), 3), round(float(np.percentile(sur[ok, 2], 95)), 3)],
           "share of paths with 10%+ share >= observed": round(float((sur[ok, 1] >= obs[1]).mean()), 3), "share of paths with 20%+ share >= observed": round(float((sur[ok, 2] >= obs[2]).mean()), 3)}}
json.dump(out, open(O / "s2.json", "w"), indent=1); print(json.dumps(out, indent=1))
