"""Stage 5-6 screen: Spearman of every feature with every target on 1990-2019 (targets ending before the lockbox),
p-values from 500 circular shifts of the target, Benjamini-Hochberg at q = 0.10, and sign stability by decade."""
from pathlib import Path
import numpy as np, pandas as pd

H = Path(__file__).resolve().parent; LOCK = pd.Timestamp("2020-01-01")
rng = np.random.default_rng(20261122)
TARGETS = {"vol4": "end4", "mdd13": "end13", "crash13": "end13", "ret4": "end4", "ret13": "end13"}

def rank(a): return pd.Series(a).rank().values

if __name__ == "__main__":
    X = pd.read_parquet(H / "data" / "features.parquet"); T = pd.read_parquet(H / "data" / "targets.parquet")
    rows = []
    for tg, endc in TARGETS.items():
        t = T.loc["1990-01-01":, [tg, endc]].dropna(); t = t[pd.to_datetime(t[endc]) < LOCK]
        yv = t[tg].values; n = len(yv); yr = rank(yv); idx = t.index
        Xd = X.reindex(idx)
        shifts = rng.integers(52, n - 52, size=500)
        Ynull = np.stack([np.roll(yr, k) for k in shifts])                     # 500 x n
        for c in Xd.columns:
            xv = Xd[c].values; m = ~np.isnan(xv)
            if m.sum() < 300: continue
            xr = rank(xv[m]); xr = (xr - xr.mean()) / xr.std()
            ya = yr[m]; ya = (ya - ya.mean()) / ya.std(); rho = float(np.mean(xr * ya))
            yn = Ynull[:, m]; yn = (yn - yn.mean(1, keepdims=True)) / yn.std(1, keepdims=True)
            rn = (yn @ xr) / m.sum()
            p = (1 + np.sum(np.abs(rn) >= abs(rho))) / (1 + len(rn))
            eras = {}
            for a, b in (("1990", "1999"), ("2000", "2009"), ("2010", "2019")):
                s = pd.DataFrame({"x": Xd[c], "y": t[tg]}).loc[a:b].dropna()
                eras[a] = s.x.rank().corr(s.y.rank()) if len(s) > 60 else np.nan
            ev = [v for v in eras.values() if pd.notna(v)]
            stable = len(ev) == 3 and all(np.sign(v) == np.sign(rho) for v in ev)
            rows.append({"target": tg, "feature": c, "rho": rho, "p": p, "n": int(m.sum()), "null95": float(np.quantile(np.abs(rn), 0.95)),
                         "rho_1990s": eras["1990"], "rho_2000s": eras["2000"], "rho_2010s": eras["2010"], "stable_sign": stable})
    R = pd.DataFrame(rows)
    # Benjamini-Hochberg across ALL feature x target pairs
    R = R.sort_values("p").reset_index(drop=True); m = len(R)
    R["bh_crit"] = 0.10 * (np.arange(1, m + 1) / m); passed = R.p <= R.bh_crit
    kmax = passed[passed].index.max() if passed.any() else -1
    R["fdr_pass"] = R.index <= kmax
    R["survivor"] = R.fdr_pass & R.stable_sign
    R.to_csv(H / "out" / "screen.csv", index=False)
    print(f"pairs tested: {m} ({R.feature.nunique()} features x {R.target.nunique()} targets); smallest attainable p = {1/501:.4f}")
    print("pass FDR:", int(R.fdr_pass.sum()), " | pass FDR and same sign in all three decades:", int(R.survivor.sum()))
    print(R.groupby("target")[["fdr_pass", "survivor"]].sum().astype(int).to_string())
    pd.set_option("display.width", 220)
    for tg in TARGETS:
        s = R[(R.target == tg) & R.survivor].copy(); s["abs"] = s.rho.abs()
        print(f"\n== {tg}: {len(s)} survivors; strongest 12:")
        if len(s): print(s.sort_values("abs", ascending=False).head(12)[["feature", "rho", "null95", "rho_1990s", "rho_2000s", "rho_2010s"]].round(3).to_string(index=False))
