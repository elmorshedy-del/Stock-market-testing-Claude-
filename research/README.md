# Research

Each study answers one line of questions and lives in its own folder.

| Study | Question | Status |
|---|---|---|
| [`agents/`](agents/) | AI agents' own research, run as scientific research: replications, critiques, method improvements, extensions. See [`agents/INDEX.md`](agents/INDEX.md). | Open |
| [`microstructure/`](microstructure/) | Does a stock's own options positioning (gamma, flip, near-price OI), the market's positioning and dark-pool buying predict bursts and direction for TSLA, MSFT, SPY and QQQ? | Active. Live status is in REPORT §4ae. |

## Starting a new study

1. Create `research/<topic>/` with:
   * a `README.md` stating the question and how to reproduce the results
   * a `.gitignore` for `data/`
2. If the study has pass/fail criteria, commit them in a file **before** the first run (see `microstructure/edge_lab_controls.md`).
3. Use engines from `engines/`. If the study must stay exactly reproducible, copy the engine in and note which version you copied.
4. Put findings in `REPORT.md` with their p-values, day counts and episode counts.
   * List every script in a *Reproduce* section.
   * Corrections are dated and stay visible.
5. Check the method against [`docs/conventions.md`](../docs/conventions.md) and run its checks. If your study shows a rule is wrong, log it in [`agents/INDEX.md`](agents/INDEX.md) or tell the owner. The rule changes once the owner adopts it.

Agents: start in [`agents/README.md`](agents/README.md). Your work goes in a dated folder there, and you don't edit the studies above.
