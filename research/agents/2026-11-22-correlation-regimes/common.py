from pathlib import Path
import numpy as np, pandas as pd
H = Path(__file__).resolve().parent; D = H / "data"
def y(k): s = pd.read_csv(D / f"Y_{k}.csv", index_col=0, parse_dates=True).iloc[:, 0]; return s[~s.index.duplicated()].sort_index()
def f(k): s = pd.read_csv(D / f"F_{k}.csv", index_col=0, parse_dates=True).iloc[:, 0]; return s[~s.index.duplicated()].sort_index()
def gold_monthly():
    g = pd.read_csv(D / "gold_monthly.csv"); g.index = pd.to_datetime(g.Date) + pd.offsets.MonthEnd(0); return g.Price
def cape(): c = pd.read_csv(D / "cape_multpl.csv", index_col=0, parse_dates=True).iloc[:, 0]; return c[c.index.day == 1]
def bond_ret(yld_pct, periods_per_year):
    yd = yld_pct / 100; dur = (1 - (1 + yd / 2) ** -20) / yd
    return -dur.shift(1) * yd.diff() + yd.shift(1) / periods_per_year
def fisher_ci(r, n): z = np.arctanh(r); s = 1 / np.sqrt(n - 3); return np.tanh(z - 1.96 * s), np.tanh(z + 1.96 * s)
