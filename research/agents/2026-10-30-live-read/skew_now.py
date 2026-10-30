"""TSLA 30-day 25-delta risk reversal and ATM IV, Oct 15-28 (extends permanence/out/skew.csv, which ends Oct 14), same function
(2026-10-30-permanence/skew.py:one_month, imported unchanged) on the recent closing chains. Usage: python skew_now.py <chain files...> -> out/tsla_skew_recent.csv"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-10-30-permanence"))
from skew import one_month       # noqa: E402

rows = [r for f in sys.argv[1:] for r in one_month(("TSLA", f))]
R = pd.DataFrame(rows).drop_duplicates("date", keep="last").sort_values("date")
old = pd.read_csv(HERE.parent / "2026-10-30-permanence" / "out" / "skew.csv", parse_dates=["date"]).query("sym == 'TSLA'")
R = pd.concat([old.tail(15), R]).drop_duplicates("date", keep="last")
R.to_csv(HERE / "out" / "tsla_skew_recent.csv", index=False)
full = pd.concat([old, R]).drop_duplicates("date", keep="last").set_index("date").sort_index()
last = full.iloc[-1]; yr = full.loc[full.index >= full.index[-1] - pd.Timedelta(days=365)]
print(R[["date", "spot", "rr25", "atm_iv"]].round(4).to_string(index=False))
print("rr25 pct (1y):", round(float((yr.rr25 < last.rr25).mean()), 3), " atm pct (1y):", round(float((yr.atm_iv < last.atm_iv).mean()), 3))
