"""Checks with known answers. Exit code 1 if any fail.

M1  no look-ahead in features: building with every input truncated at a cutoff reproduces every feature (raw and
    model input) on or before the cutoff
M2  purge: in every walk-forward year, every training week's outcome window ended before the test year began
M3  labels by hand: S&P fell 10%+ within 13 weeks of Fri 2020-02-21 and 20%+ within 52 weeks of Fri 2021-12-31;
    not 10% within 13 weeks of Fri 2017-06-30
M4  shift-null calibration for the stacked-rule test: persistent no-effect signals give p < 0.05 about 5% of the time
"""
import sys

import numpy as np
import pandas as pd

import explore_mv as E
import features_mv as F
import model_mv as M

fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  {detail}" if detail else ""))
    if not ok:
        fails.append(name)


full = pd.read_pickle(F.DATA / "features_raw.pkl")
Xfull = pd.read_pickle(F.DATA / "features_X.pkl")
feat = [c for c in full.columns if c[:2] in ("V_", "M_", "O_", "R_", "S_") or c.startswith("ERA_")]
bad = 0
for cut in ("2008-09-26", "2018-09-28", "2021-12-31"):
    f = F.build(cut)
    X = F.transform(f)
    rows = f.index[f.index <= pd.Timestamp(cut)]
    a, b = full.loc[rows, feat].to_numpy(float), f.loc[rows, feat].to_numpy(float)
    same = np.isclose(a, b, rtol=1e-9, atol=1e-12, equal_nan=True)
    xa, xb = Xfull.loc[rows].to_numpy(float), X.loc[rows].to_numpy(float)
    same_x = np.isclose(xa, xb, rtol=1e-9, atol=1e-12, equal_nan=True)
    bad += int((~same).sum() + (~same_x).sum())
    if (~same).any():
        cols = np.array(feat)[(~same).any(axis=0)]
        print("   differing raw columns at", cut, list(cols))
check("M1 features on or before a cutoff do not change when later data are removed", bad == 0, f"{bad} mismatches")

raw = full
worst = pd.Timedelta(days=-10**5)   # latest (label end - test start) over all years; must stay negative
for outcome, H in M.H_WEEKS.items():
    y = raw[outcome]
    for Y in M.YEARS:
        cut = pd.Timestamp(f"{Y}-01-01")
        train = (raw.index >= M.START) & y.notna().to_numpy() & ((raw.last_day + pd.Timedelta(weeks=H)) < cut).to_numpy()
        if train.any():
            end = (raw.last_day[train] + pd.Timedelta(weeks=H)).max()
            worst = max(worst, end - cut)
check("M2 every training label window ends before its test year", worst < pd.Timedelta(0), f"closest label end: {-worst.days} days before its test year")

ok = (full.loc["2020-02-21", "Y_CORR"] == 1 and full.loc["2021-12-31", "Y_BEAR"] == 1
      and full.loc["2017-06-30", "Y_CORR"] == 0)
check("M3 labels match known history", bool(ok))

y = raw.Y_CORR[raw.index >= "1992-01-01"]
pv = []
for rep in range(200):
    g = np.random.default_rng(3000 + rep)
    x = np.zeros(len(y))
    for k in range(1, len(x)):
        x[k] = 0.98 * x[k - 1] + g.normal()
    s = pd.Series((x > np.quantile(x, 2 / 3)).astype(float), index=y.index)
    pv.append(E.shift_test(s, y, ndraw=200, seed=rep)["p_shift"])
fp = float(np.mean(np.array(pv) < 0.05))
check("M4 stacked-rule shift null: false positives near 5%", 0.01 <= fp <= 0.10, f"{fp:.1%} of 200 no-effect signals")

print("\n" + ("ALL PASS" if not fails else f"{len(fails)} FAILED: {fails}"))
sys.exit(1 if fails else 0)
