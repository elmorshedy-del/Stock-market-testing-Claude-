"""Amendment A3: B6 rotation/coupling zones; B5 fix (Day-2 corr from 5-day pull). Usage: python a3.py <dl_dir> <label>"""
import sys, json, time, random, importlib.util, requests, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
dl, label = sys.argv[1], sys.argv[2]; H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
out = {"label": label}
px = pd.DataFrame({s: lc.yahoo(s, "2003-06-01").close for s in ("RSP", "SMH")}).dropna(); r = px.pct_change().dropna()
bins = [-1, -0.06, -0.04, -0.02, 0, 0.02, 1]; labels = ["<=-6", "-6..-4", "-4..-2", "-2..0", "0..+2", ">+2"]
for tag, start in (("recent 2023-2026", "2023-01-01"), ("full 2004-2026", "2004-01-01")):
    w = r[(r.index >= start) & (r.index <= "2026-10-30")].copy(); w["bin"] = pd.cut(w.SMH, bins, labels=labels)
    g = w.groupby("bin", observed=True).agg(n=("RSP", "size"), SMH_mean=("SMH", "mean"), RSP_mean=("RSP", "mean"), RSP_neg=("RSP", lambda x: (x < 0).mean()))
    g["coupling"] = g.RSP_mean / g.SMH_mean
    out[f"B6 {tag}"] = {b: {"n": int(x.n), "SMH mean %": round(100 * x.SMH_mean, 2), "RSP mean %": round(100 * x.RSP_mean, 2), "share RSP<0": round(float(x.RSP_neg), 3), "coupling": round(float(x.coupling), 3)} for b, x in g.iterrows()}
    tail = w[w.SMH <= -0.04]; mid = w[(w.SMH > -0.04) & (w.SMH <= -0.02)]
    out[f"B6 {tag}"]["test"] = {"coupling tail (<=-4)": round(float(tail.RSP.mean() / tail.SMH.mean()), 3), "coupling -4..-2": round(float(mid.RSP.mean() / mid.SMH.mean()), 3),
                                "ratio": round(float((tail.RSP.mean() / tail.SMH.mean()) / (mid.RSP.mean() / mid.SMH.mean())), 2), "mid-bin RSP mean %": round(100 * float(mid.RSP.mean()), 2)}
# B5 fix: same 150 names, baseline from 60-day pull, Day 2 from the 5-day pull
X = pd.read_csv(O / f"cross_section_{label}.csv", index_col=0); rest = sorted(X.index[X.b_AI < X.b_AI.quantile(0.70)]); random.seed(7); samp = random.sample(rest, 150)
M5 = pd.read_parquet(f"{dl}/m5.parquet").reset_index(); M5 = M5[M5.sym.isin(samp)]
def avgcorr(C):
    lr = np.log(C).diff().iloc[1:]; lr = lr.dropna(axis=1, thresh=int(0.8 * len(lr))).dropna(axis=0, how="any"); cm = np.corrcoef(lr.values.T); n = cm.shape[0]; return (cm.sum() - n) / (n * (n - 1)), lr.shape
res = {}
for d in ("2026-10-30", "2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05"):
    x = M5[M5.ts.dt.date == pd.Timestamp(d).date()]; x = x[(x.ts.dt.time >= pd.Timestamp("09:30").time()) & (x.ts.dt.time < pd.Timestamp("16:00").time())]
    x = x.assign(ts=x.ts.dt.floor("5min")); C = x.pivot_table(index="ts", columns="sym", values="close", aggfunc="last"); v, shp = avgcorr(C); res[d] = {"corr": round(float(v), 3), "bars x names": list(shp)}
a2 = json.load(open(O / f"a2_{label}.json"))["B5 avg pairwise 5-min corr, 150 non-AI names"]
out["B5 fix (5-day pull)"] = {"by day": res, "baseline median (60-day pull)": a2["baseline median"], "baseline 95th pct": a2["baseline 95th pct"],
                              "Day 2 vs baseline 95th": "above" if res["2026-11-05"]["corr"] > a2["baseline 95th pct"] else "not above"}
json.dump(out, open(O / f"a3_{label}.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
