# Gamma engine

Daily dealer-gamma history for a single stock or ETF, built from end-of-day option chains and open interest (OI).
For each trading day it gives:
* dealer gamma (GEX)
* the gamma flip
* call and put walls
* vanna and charm
* how much OI sits near the price
* 30-day ATM IV

A live tool redraws the map intraday from today's OI.

The source is `research/log_channels` in the `genovy` repo, where every result built on it is written up.

## Files

| File | What it does |
|---|---|
| `td_pull.py` | Downloads ThetaData end-of-day option quotes and OI, one request per symbol per month, resumable. |
| `td_gamma.py` | **The engine.** Turns the downloaded chains into one row per day → `out/td_gamma_{SYM}.csv`. |
| `hd_gamma.py` | `day_metrics()`: the per-day metrics (GEX, flip, walls, shares). Also holds an older builder for HistoricalData.net CSV samples. |
| `options_flow.py` | Black-Scholes greeks, `exposures()` (the GEX formula and sign convention) and `gex_profile()`. Its Yahoo functions (`load_chain`, `summary`) need `fetch.py` from the source repo. |
| `common.py` | Paths (`data/`, `out/`) and a Yahoo daily-bar loader. |
| `live_check.py` | Intraday: today's OI at a live price, the flip now vs after the next expiry, and OI changes by strike. Called `tsla_live.py` in the source repo. |

## Setup

```bash
python3.12 -m venv .venv && source .venv/bin/activate   # the thetadata package needs Python >= 3.12
pip install -r requirements.txt
export THETADATA_API_KEY=...        # Value tier or higher; keep it in the environment, never in a file
```

* `td_gamma.py` itself only needs numpy, pandas and scipy, so it runs on any Python ≥ 3.10 once the data is downloaded.
* `data/` and `out/` are gitignored. Raw ThetaData chains are licensed data and must not be committed.

## Use

```bash
# 1. Download chains + OI (resumable; past months are cached, the current month is always refreshed)
python td_pull.py 2020-01 2026-10 TSLA MSFT SPY QQQ

# 2. Build the daily gamma history (4 worker processes)
OMP_NUM_THREADS=1 python td_gamma.py TSLA MSFT SPY QQQ

# 3. During the session: today's OI at a live price, and the map after Friday's expiry
python live_check.py 2026-10-15 362.53 TSLA 2026-10-16      # day, live price, symbol, next monthly expiry
```

* `TD_MAX_DTE` overrides the 120-day expiry cap in step 1. Contracts beyond 120 days add less than 1% to the gamma.
* Set `OMP_NUM_THREADS=1` in step 2. Otherwise each worker spawns its own math threads and the run can slow down badly.

## Output: `out/td_gamma_{SYM}.csv` (one row per trading day)

| Column | Meaning |
|---|---|
| `date` | Session date. OI on this row is the **prior close's** positions, i.e. positioning going into this session. |
| `spot` | Close implied by put-call parity (split-unadjusted, like the strikes). |
| `call_oi`, `put_oi`, `contracts` | Totals over expiries ≤ 120 days. |
| `gex_classic` | Dealer gamma, $ of delta change per 1% move, **classic convention** (see Method). Positive = dealers dampen moves, negative = they amplify them. |
| `gex_short` | The same with dealers short every option (an alternative convention, kept for comparison). |
| `vanna_*`, `charm_*` | $ delta change per +1 vol point / per calendar day. |
| `flip_classic` | Price where total classic GEX crosses zero (the gamma flip). Above it dealers are long gamma, below it short gamma. |
| `call_wall`, `put_wall` | Strikes with the most call / put OI, expiries ≤ 45 days, within ±25% of spot. |
| `gamma_share_1d`, `gamma_share_5d` | Share of absolute gamma expiring within 1 / 5 trading days. |
| `near_oi_share` | Share of all OI at strikes within ±5% of spot, expiries ≤ 45 days. It is IV-free. A low value means the stock is "freed" (little OI pinning it). |
| `atm_iv_30d` | ATM IV, expiries 20–45 days out. |

## Method

* **Spot:** put-call parity at the strikes where call mid − put mid is smallest, on the nearest expiry at least 2 days out.
* **IV:** ThetaData end-of-day rows have no IV. It is solved by Black-Scholes bisection from **out-of-the-money** mids (r = 4%), smoothed across strikes per expiry, and applied to both calls and puts at each strike.
* **GEX per contract:** gamma × OI × 100 × S² × 0.01.
* **Sign (classic):** dealers long calls (+) and short puts (−). This is the SqueezeMetrics convention.
* **Flip:** total GEX evaluated on an 81-point price grid from 0.8× to 1.2× spot; the zero crossing nearest spot, linearly interpolated.
* **States used in the research:**
  * "Below flip": spot < `flip_classic`.
  * "Freed": `near_oi_share` in the bottom third of its trailing 252-day range.

```python
import pandas as pd
m = pd.read_csv("out/td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
m["below_flip"] = m.spot < m.flip_classic
m["near_pct"] = m.near_oi_share.rolling(252, min_periods=120).rank(pct=True)
m["freed"] = m.near_pct <= 1/3
print(m[["spot", "flip_classic", "below_flip", "near_pct", "freed"]].tail())
```

## What is verified, and what is not

* **Verified:**
  * The exposure code reproduces SqueezeMetrics' published S&P GEX at a correlation of 0.96 (0.90 on daily changes), using a 2022 SPX end-of-day sample. The all-short convention gets −0.34.
  * SPY gamma from this engine tracks SqueezeMetrics at 0.67 in levels and 0.83 as percentiles (2021–2026).
  * This folder reproduces the source repo's TSLA output exactly (Sep–Oct 2026 test).
* **Assumed, not tested:**
  * The dealer sign. There are no signed (buy/sell) option trades, so who is long or short is assumed.
  * 0DTE positions are invisible, because OI is end-of-day.
  * Where an expiry has fewer than 3 usable IVs, it falls back to the expiry's (or the day's) median IV.
* **Use outcomes strictly forward.** Positioning on row t is known at t's close, so outcomes must start at t+1. Counting day t's own move produced fake effects in the research (since corrected).

## Data notes

* **ThetaData Value tier ($40/month):**
  * End-of-day quotes and OI from January 2020.
  * 2 concurrent requests per session, which is what the scripts use.
  * Same-day OI must be requested one expiration at a time; `live_check.py` does this.
  * The free tier has about one year of quotes and no OI, so it cannot run this.
* **Downloaded files:** `data/thetadata/{SYM}_{YYYY-MM}_{eod|oi}.csv.gz`, plus `{SYM}_live_oi_{YYYYMMDD}.csv.gz` from the live tool. 2020-01 to 2026-10 for six tickers was about 860 MB.
