# Stock-market testing

This repo tests trading ideas against market microstructure:
* dealer gamma and open interest
* the gamma flip
* dark-pool buying
* option expiries
* how a stock moves relative to the market

Every result can be re-run and re-checked from the code here. Nothing is meant to be taken on trust.

## Layout

```
engines/                 reusable tools; each has a README and a verify script
  gamma/                 option chains -> daily dealer gamma, flip, walls, near-price open interest; intraday live check
research/                one folder per study: scripts, REPORT.md with the findings, out/ figures and tables
  microstructure/        TSLA / MSFT / SPY / QQQ: own-stock gamma, the "freed" state, MSFT vs SPY release,
                         expiry weeks, dark pools (moved here from genovy research/log_channels, with its history)
  agents/                AI agents' own research: replications, critiques, better methods, new questions;
                         one dated folder each, never overwriting the originals (INDEX.md lists them)
docs/
  conventions.md         how studies are tested, each rule with its evidence and a command to re-test it
  data-sources.md        every data source and subscription: coverage, cost, limits
CLAUDE.md                instructions for AI agents working in this repo
```

## Verify before you trust

```bash
cd engines/gamma && python verify.py --study ../../research/microstructure     # engine: 8 checks with known answers
cd research/microstructure && OMP_NUM_THREADS=1 python rule_checks.py         # the testing rules: 5 checks
```

* Every number in a study's `REPORT.md` comes from a script listed in its *Reproduce* section. Rerunning it is the check.
* When a rerun disagrees, the rerun wins. The report gets a dated correction, never a silent edit.
* Agents can challenge or improve any of it in `research/agents/`. You decide what gets adopted.

## Start here

* **Gamma for a ticker:** [`engines/gamma/README.md`](engines/gamma/README.md)
* **Current findings:** [`research/microstructure/REPORT.md`](research/microstructure/REPORT.md). Read the corrections; several early results were retracted.
* **A new study:** see [`research/README.md`](research/README.md)
* **Data and keys:** [`docs/data-sources.md`](docs/data-sources.md). Keys go in environment variables only. Licensed raw data never goes in git.
