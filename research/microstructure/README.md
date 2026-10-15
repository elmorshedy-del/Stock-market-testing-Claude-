# Options microstructure study

**Question:** does positioning predict bursts and their direction? The pieces tested are:
* a stock's own options positioning: dealer gamma, the gamma flip, near-price open interest
* the market's positioning: S&P dealer gamma
* dark-pool buying

Main subjects are TSLA, MSFT, SPY and QQQ. The study began as a MU log-channel case study (§1–§5 of the report), which explains the report's title.

Moved here from `genovy/research/log_channels` with its full git history.

## Read in this order

1. **`REPORT.md` §4ae:** the latest status (TSLA setup, MSFT release, expiry week, dark pools, market bounce vs TSLA drawdown).
2. **§4z:** the timing correction. Two earlier "findings" were artifacts of counting day t's own move, and later sections are built on the corrected method.
3. **§4ad:** how large an edge must be before this method can see it. Use it to judge any result here.
4. The rest by topic; the section headings name their scripts.

## Verify

```bash
OMP_NUM_THREADS=1 python rule_checks.py                    # the testing rules in docs/conventions.md, re-tested on this data
cd ../../engines/gamma && python verify.py --study ../../research/microstructure   # the gamma engine
```

* Every number in `REPORT.md` comes from a script in its *Reproduce* section. Rerun it to check.
* If a rerun disagrees, the rerun wins. Add a dated correction to the report.

## Setup and data

```bash
pip install -r requirements.txt                 # numpy pandas scipy matplotlib
python fetch.py --index                         # S&P/VIX history + SqueezeMetrics GEX/DIX  -> data/
python fetch.py --universe                      # daily bars for the stock universe          -> data/*_1d.json
python finra_dpi.py fetch                       # FINRA daily short-volume files             -> data/finra/
# ThetaData (needs THETADATA_API_KEY, Value tier, Python 3.12 + the thetadata package):
python td_pull.py 2020-01 2026-10 TSLA MSFT SPY QQQ NVDA MU   # -> data/thetadata/
OMP_NUM_THREADS=1 python td_gamma.py TSLA MSFT SPY QQQ NVDA MU # -> out/td_gamma_{SYM}.csv
```

* `data/` is gitignored, apart from the MU, TSLA and MSFT snapshot files that cannot be re-downloaded.
* Derived tables and figures in `out/` are committed.
* `td_gamma.py`, `hd_gamma.py`, `options_flow.py`, `common.py` and `td_pull.py` are this study's frozen copy of the engine. The maintained version is `engines/gamma/`; it gives identical output (`verify.py` B1).

## Daily routine (during a live setup)

```bash
python fetch.py --index && python finra_dpi.py fetch && python fetch.py --universe   # after the close
python td_pull.py 2026-10 2026-10 TSLA MSFT SPY QQQ && OMP_NUM_THREADS=1 python td_gamma.py TSLA MSFT SPY QQQ
python tsla_live.py 2026-10-16 <price> TSLA <next monthly expiry>     # intraday, from today's OI
python status_fig.py 2026-10-16 <price> <next monthly expiry>         # TSLA and MSFT setup figure -> out/status.png
```
