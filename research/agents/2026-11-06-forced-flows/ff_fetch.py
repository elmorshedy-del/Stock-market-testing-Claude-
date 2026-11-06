"""Forced-flows data: LETF universe (leverage from fund names, net assets from Yahoo quote), daily closes/volumes, 60-day 5-minute bars.
Writes data/ (gitignored). Usage: python ff_fetch.py"""
import json, time, urllib.request, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
H = Path(__file__).resolve().parent; D = H / "data"; TD = Path("/tmp/claude-0/-home-user-genovy/4a459aba-63bd-54e9-abd7-2cbbef04a1e9/scratchpad/thesis/dl")
# leverage checked against each fund's name (data/letf_quote.json longName); grouped by the underlying whose shares absorb the hedge
LEV = {"SPX": {"UPRO": 3, "SPXL": 3, "SSO": 2, "SPUU": 2, "SPXU": -3, "SPXS": -3, "SDS": -2, "SH": -1},
       "NDX": {"TQQQ": 3, "QLD": 2, "SQQQ": -3, "QID": -2, "PSQ": -1},
       "SEMIS": {"SOXL": 3, "USD": 2, "SOXS": -3, "SSG": -2},
       "NVDA": {"NVDL": 2, "NVDU": 2, "NVDX": 2, "NVDD": -1, "NVDQ": -2, "NVD": -2}, "TSLA": {"TSLL": 2, "TSLR": 2, "TSLT": 2, "TSLQ": -2, "TSLZ": -2, "TSLS": -1},
       "AMD": {"AMDL": 2, "AMUU": 2}, "AVGO": {"AVL": 2, "AVGX": 2, "AVGU": 2}, "MU": {"MUU": 2, "MULL": 2}, "PLTR": {"PLTU": 2, "PTIR": 2, "PLTD": -1},
       "MSTR": {"MSTU": 2, "MSTX": 2, "MSTZ": -2, "SMST": -2}, "COIN": {"CONL": 2, "CONI": -2}}
REF = {"SPX": "SPY", "NDX": "QQQ", "SEMIS": "SOXX"}  # price reference for each complex; single stocks reference themselves
NDX = "AAPL NVDA MSFT AMZN GOOGL SPCX GOOG META AVGO TSLA WMT MU AMD ASML COST PLTR CSCO INTC PANW NFLX AMAT TXN LRCX AMGN LIN CRWD GILD PEP SHOP ARM ADI KLAC ISRG TMUS QCOM VRTX SNDK MRVL BKNG SBUX PDD ADP STX WDC APP MAR ABNB MRNA REGN ADBE CSX MNST INTU FTNT CTAS CMCSA CDNS SNPS MDLZ CEG DASH MELI ROST ORLY HON AEP DDOG NXPI FAST MPWR MSTR ADSK PCAR IDXX LITE XEL FANG TRI CCEP BKR KDP PYPL HONA ROP WDAY EXC PAYX FER MCHP TTWO GEHC ODFL TER NBIS ALAB AXON DXCM RKLB CPRT CRWV ALNY".split()  # slickcharts, fetched 2026-11-06 (cache 2026-11-05)
SEMIS = "NVDA AVGO AMD MU QCOM TXN INTC AMAT LRCX KLAC ADI MRVL NXPI MCHP ON MPWR TER ENTG SWKS QRVO TSM ASML ARM ALAB COHR LSCC GFS SNDK".split()  # approximation of SOXX's index
def get(url, tries=5):
    for k in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))
        except Exception as e:
            time.sleep(1.5 * (k + 1))
    return None
def daily(sym, p1=int(pd.Timestamp("2026-03-01").timestamp())):
    d = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1={p1}&period2={int(time.time())}&interval=1d&events=split")
    try:
        r = d["chart"]["result"][0]; q = r["indicators"]["quote"][0]; ix = pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").normalize().tz_localize(None)
        return sym, pd.DataFrame({"close": q["close"], "volume": q["volume"]}, index=ix).dropna()
    except Exception: return sym, None
def m5(sym):
    d = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=60d&interval=5m")
    try:
        r = d["chart"]["result"][0]; q = r["indicators"]["quote"][0]; ix = pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York")
        return sym, pd.DataFrame({"close": q["close"], "volume": q["volume"]}, index=ix).dropna()
    except Exception: return sym, None
letfs = [t for g in LEV.values() for t in g]; unders = list(REF.values()) + [u for u in LEV if u not in REF]
sp = set(pd.read_parquet(TD / "daily_vol.parquet").columns); extra = sorted((set(NDX) | set(SEMIS)) - sp)
with ThreadPoolExecutor(8) as ex: dd = dict(ex.map(daily, sorted(set(letfs + unders + extra))))
with ThreadPoolExecutor(6) as ex: mm = dict(ex.map(m5, unders))
miss = [k for k, v in dd.items() if v is None] + [f"m5:{k}" for k, v in mm.items() if v is None]; print("missing:", miss)
pd.concat({k: v for k, v in dd.items() if v is not None}, axis=1).to_parquet(D / "daily.parquet"); pd.concat({k: v for k, v in mm.items() if v is not None}, axis=1).to_parquet(D / "m5.parquet")
json.dump({"LEV": LEV, "REF": REF, "NDX": NDX, "SEMIS": SEMIS, "extra fetched": extra}, open(D / "universe.json", "w"), indent=1); print("ok", len(dd), len(mm))
