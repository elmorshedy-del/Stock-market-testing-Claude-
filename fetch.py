"""Download daily/intraday bars and full option chains from Yahoo Finance.

Usage: python fetch.py MU [NVDA ...]      (options + intraday for the first symbol)
       python fetch.py --universe          (daily bars for the backtest universe)
"""
import json
import subprocess
import sys
import time
from pathlib import Path

DATA = Path(__file__).parent / "data"
UA = "Mozilla/5.0"
UNIVERSE = [
    "MU", "NVDA", "AMD", "AVGO", "TSM", "AAPL", "MSFT", "AMZN", "META", "GOOGL",
    "TSLA", "NFLX", "LRCX", "AMAT", "KLAC", "ASML", "SMCI", "PLTR", "COST", "LLY",
    "JPM", "XOM", "CAT", "GE", "WMT", "ORCL", "CRM", "ADBE", "INTC", "QCOM",
    "SPY", "QQQ", "NVO", "UNH", "BA", "DIS", "SHOP", "UBER", "ANET", "VRT",
]


def curl(url, out=None, cookies=None):
    cmd = ["curl", "-sS", "-m", "40", "-A", UA]
    if cookies:
        cmd += ["-b", str(cookies), "-c", str(cookies)]
    cmd.append(url)
    for attempt in range(4):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and r.stdout:
            if out:
                Path(out).write_text(r.stdout)
            return r.stdout
        time.sleep(2 ** attempt)
    raise RuntimeError(f"fetch failed: {url}: {r.stderr}")


def chart(sym, rng="10y", interval="1d"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval={interval}&includePrePost=false"
    curl(url, DATA / f"{sym}_{interval}.json")


def options(sym):
    jar = DATA / ".cookies"
    curl("https://fc.yahoo.com", cookies=jar)
    crumb = curl("https://query1.finance.yahoo.com/v1/test/getcrumb", cookies=jar).strip()
    base = f"https://query1.finance.yahoo.com/v7/finance/options/{sym}?crumb={crumb}"
    first = json.loads(curl(base, cookies=jar))["optionChain"]["result"][0]
    chains = []
    for exp in first["expirationDates"]:
        res = json.loads(curl(f"{base}&date={exp}", cookies=jar))["optionChain"]["result"][0]
        chains.append(res["options"][0])
    snap = {"quote": first["quote"], "fetched": int(time.time()), "chains": chains}
    (DATA / f"{sym}_options.json").write_text(json.dumps(snap))
    jar.unlink(missing_ok=True)


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    if sys.argv[1:] == ["--universe"]:
        for s in UNIVERSE:
            chart(s)
            print("daily", s)
    else:
        for s in sys.argv[1:]:
            chart(s, "10y", "1d")
        main = sys.argv[1]
        chart(main, "60d", "5m")
        chart(main, "7d", "1m")
        options(main)
        print("ok", main)
