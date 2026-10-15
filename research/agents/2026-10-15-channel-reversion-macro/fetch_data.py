"""Download everything this study uses into data/ (gitignored). Re-runnable; skips files already present
unless --refresh is given.

Sources (all free, no keys):
  Yahoo chart API      daily bars, full history, for the stock universe and market series
  BLS                  CPI-U (all items, not seasonally adjusted), 1980+
  Federal Reserve DDP  H.15 (rates), H.4.1 (balance sheet, TGA, reverse repo), H.6 (M2), whole releases
  US Treasury          daily real (TIPS) yield curve, 2003+
  FINRA                margin statistics (customer debit balances)
  SqueezeMetrics       S&P dealer gamma (GEX) and DIX, 2011+
  SEC XBRL             companyfacts (inventory, revenue, with filing dates)

Usage: python fetch_data.py [--refresh]
"""
import json
import subprocess
import sys
import time
from pathlib import Path

DATA = Path(__file__).parent / "data"
UA = "Mozilla/5.0"
# data.sec.gov serves this UA; www.sec.gov (the ticker->CIK file) refuses bots, so CIKs are listed by hand
# and each download is checked against its entityName in build_panel.py (wrong CIK -> name mismatch -> dropped).
SEC_UA = UA
CIK = {
    "NVDA": 1045810, "INTC": 50863, "AMD": 2488, "TXN": 97476, "ADI": 6281, "MU": 723125, "AMAT": 6951,
    "LRCX": 707549, "KLAC": 319201, "QCOM": 804328, "MCHP": 827054, "TER": 97210, "AVGO": 1730168,
    "NXPI": 1413447, "MRVL": 1835632, "ON": 1097864, "SWKS": 4127, "MSFT": 789019, "AAPL": 320193,
    "ORCL": 1341439, "CSCO": 858877, "IBM": 51143, "HPQ": 47217, "ADBE": 796343, "INTU": 896878,
    "ADSK": 769397, "SNPS": 883241, "CDNS": 813672, "AMZN": 1018724, "EBAY": 1065088, "GOOGL": 1652044,
    "NFLX": 1065280, "CRM": 1108524, "JNPR": 1043604, "NTAP": 1002047, "WDC": 106040, "STX": 1137789,
    "CTSH": 1058290, "AKAM": 1086222, "VRSN": 1014473, "META": 1326801,
}   # TSM, ASML, NOK, ERIC file 20-F under IFRS: no us-gaap facts, skipped

# Frozen before any outcome was looked at: large US-listed tech, semis and internet names with
# Yahoo history, plus indices. Survivors only (Yahoo drops delisted tickers): see README threats.
STOCKS = [
    # semiconductors
    "NVDA", "INTC", "AMD", "TXN", "ADI", "MU", "AMAT", "LRCX", "KLAC", "QCOM", "MCHP", "TSM",
    "ASML", "TER", "AVGO", "NXPI", "MRVL", "ON", "SWKS",
    # software, hardware, internet
    "MSFT", "AAPL", "ORCL", "CSCO", "IBM", "HPQ", "ADBE", "INTU", "ADSK", "SNPS", "CDNS",
    "AMZN", "EBAY", "GOOGL", "NFLX", "CRM", "JNPR", "NTAP", "WDC", "STX", "CTSH", "AKAM",
    "NOK", "ERIC", "VRSN", "META",
]
INDICES = ["^IXIC", "^NDX", "^SOX", "^GSPC"]
MARKET = ["^VIX", "DX-Y.NYB", "^TNX", "^IRX", "^TYX", "^FVX", "HYG", "LQD", "IEF", "BTC-USD"]

TREASURY_REAL = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
                 "daily-treasury-rates.csv/{y}/all?type=daily_treasury_real_yield_curve"
                 "&field_tdr_date_value={y}&page&_format=csv")


def curl(url, out, ua=UA, refresh=False, tries=4):
    out = Path(out)
    if out.exists() and out.stat().st_size > 0 and not refresh:
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".part")
    for attempt in range(tries):
        r = subprocess.run(["curl", "-sS", "-L", "-m", "120", "-A", ua, "-o", str(tmp),
                            "-w", "%{http_code}", url], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip() == "200" and tmp.stat().st_size > 0:
            tmp.rename(out)
            return True
        time.sleep(2 ** attempt)
    tmp.unlink(missing_ok=True)
    raise RuntimeError(f"fetch failed ({r.stdout.strip()} {r.stderr.strip()}): {url}")


def yahoo(sym, refresh):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=0"
           f"&period2={int(time.time())}&interval=1d&includePrePost=false&events=div%2Csplit")
    return curl(url, DATA / "yahoo" / f"{sym}.json", refresh=refresh)


def main(refresh=False):
    log = []
    for s in STOCKS + INDICES + MARKET:
        try:
            yahoo(s, refresh)
            log.append(("yahoo", s, "ok"))
        except RuntimeError as e:
            log.append(("yahoo", s, str(e)[:80]))
        time.sleep(0.3)
    for y0 in range(1980, 2030, 10):          # BLS v1 API: no key, 10 years per request, rate-limited
        out = DATA / "bls" / f"cpi_{y0}.json"
        if out.exists() and not refresh and y0 != 2020:
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(".part")
        body = json.dumps({"seriesid": ["CUUR0000SA0"], "startyear": str(y0), "endyear": str(y0 + 9)})
        for attempt in range(4):
            subprocess.run(["curl", "-sS", "-m", "60", "-A", UA, "-X", "POST", "-H", "Content-Type: application/json",
                            "-d", body, "-o", str(tmp), "https://api.bls.gov/publicAPI/v1/timeseries/data/"])
            try:
                ok = json.loads(tmp.read_text())["status"] == "REQUEST_SUCCEEDED"
            except (ValueError, OSError, KeyError):
                ok = False
            if ok:
                tmp.rename(out)
                break
            time.sleep(5 * 2 ** attempt)
        else:
            tmp.unlink(missing_ok=True)
            print("WARN BLS busy; keeping the existing", out.name if out.exists() else "(none)")
    for rel in ("H15", "H41", "H6"):
        curl(f"https://www.federalreserve.gov/datadownload/Output.aspx?rel={rel}&filetype=zip",
             DATA / "fed" / f"{rel}.zip", refresh=refresh)
    for y in range(2003, 2027):
        curl(TREASURY_REAL.format(y=y), DATA / "treasury_real" / f"{y}.csv",
             refresh=refresh or y == 2026)
    curl("https://squeezemetrics.com/monitor/static/DIX.csv", DATA / "DIX.csv", refresh=refresh)
    # FINRA keeps the live file at this 2021 path (linked from its margin-statistics page)
    curl("https://www.finra.org/sites/default/files/2021-03/margin-statistics.xlsx",
         DATA / "finra_margin.xlsx", refresh=refresh)
    for s, c in CIK.items():
        try:
            curl(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{c:010d}.json",
                 DATA / "sec" / f"{s}.json", ua=SEC_UA, refresh=refresh)
            log.append(("sec", s, "ok"))
        except RuntimeError as e:
            log.append(("sec", s, str(e)[:80]))
        time.sleep(0.15)
    for row in log:
        if row[2] != "ok":
            print("WARN", *row)
    print("done:", sum(r[2] == "ok" for r in log), "of", len(log), "per-symbol pulls ok")


if __name__ == "__main__":
    main(refresh="--refresh" in sys.argv)
