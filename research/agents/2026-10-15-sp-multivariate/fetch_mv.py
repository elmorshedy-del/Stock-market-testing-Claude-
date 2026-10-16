"""Extra data for the S&P multivariate study (no keys). Re-runnable; skips files already present.

  Yahoo            ^SKEW (1990+), ^VVIX (2007+), ^VIX9D (2011+)
  Cboe             put/call archive CSVs (total, equity, index; Nov 2006 - Oct 4 2019) and the daily market-statistics
                   JSON from Oct 7 2019 on (put/call ratios, volume and open interest by product incl. SPX + SPXW)
  Chicago Fed      NFCI and its risk / credit / leverage parts, weekly since 1971 (current vintage: revised history)

Usage: python fetch_mv.py
"""
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
PREV = HERE.parent / "2026-10-15-channel-reversion-macro"
sys.path.insert(0, str(PREV))
import fetch_data as FD   # noqa: E402

DATA = HERE / "data"
UA = "Mozilla/5.0"


def get(url, out, refresh=False):
    out = Path(out)
    if out.exists() and out.stat().st_size > 0 and not refresh:
        return "cached"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".part")
    for attempt in range(3):
        r = subprocess.run(["curl", "-sS", "-L", "-m", "60", "-A", UA, "-o", str(tmp), "-w", "%{http_code}", url],
                           capture_output=True, text=True)
        code = r.stdout.strip()
        if code == "200" and tmp.stat().st_size > 0:
            tmp.rename(out)
            return "ok"
        if code in ("403", "404"):
            tmp.unlink(missing_ok=True)
            return code
        time.sleep(2 ** attempt)
    tmp.unlink(missing_ok=True)
    return "fail"


def main():
    for sym, name in (("%5ESKEW", "SKEW"), ("%5EVVIX", "VVIX"), ("%5EVIX9D", "VIX9D")):
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=0&period2={int(time.time())}"
               f"&interval=1d&includePrePost=false")
        FD.curl(url, DATA / "yahoo" / f"{name}.json", refresh=True)
    for f in ("totalpc", "equitypc", "indexpc"):
        get(f"https://cdn.cboe.com/resources/options/volume_and_call_put_ratios/{f}.csv", DATA / "cboe" / f"{f}.csv")
    days = pd.bdate_range("2019-10-07", pd.Timestamp.today().normalize())
    urls = [(f"https://cdn.cboe.com/data/us/options/market_statistics/daily/{d:%Y-%m-%d}_daily_options",
             DATA / "cboe" / "daily" / f"{d:%Y-%m-%d}.json") for d in days]
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda a: get(*a), urls))
    print("cboe daily:", {k: res.count(k) for k in set(res)})
    get("https://www.chicagofed.org/-/media/publications/nfci/nfci-data-series-csv.csv", DATA / "nfci.csv", refresh=True)
    print("done")


if __name__ == "__main__":
    main()
