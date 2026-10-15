# Instructions for AI agents

**Verify, don't follow.** Rules and findings here are claims with evidence attached. Before you build on one, run its check:
* `engines/gamma/verify.py`
* `research/microstructure/rule_checks.py`
* the study's *Reproduce* commands

If a check fails, or you can show a rule or result is wrong, write it up as research (below). Rerun results win over written ones.

**Your own research goes in `research/agents/<YYYY-MM-DD>-<topic>/`.** Read [`research/agents/README.md`](research/agents/README.md) first.
* You have autonomy to replicate, critique, improve or extend anything here, or to ask new questions. Treat it as scientific research: pre-register, report denominators and nulls, and give a verdict against the prior work.
* **Never edit or overwrite the originals** (`research/microstructure/`, `engines/`, `docs/`, other agents' folders) unless the owner explicitly asks. Build on them by importing or copying them into your folder.
* If your work contradicts or refines an original, log it in `research/agents/INDEX.md`. The owner decides what gets corrected.

* **Layout:** `engines/` holds reusable tools, `research/<study>/` the owner's studies, `research/agents/` agents' own studies, and `docs/` the conventions and data sources.
* **Keys:** read from environment variables only. Never write a key into a file, a commit, a script, or command history saved to disk.
* **Licensed data** stays out of git: ThetaData chains, HistoricalData.net, Databento, Cboe samples. Each folder's `.gitignore` covers `data/`. Derived daily metrics may be committed.
* **Timing:** a state read at day t's close predicts t+1 onward only. Open interest dated t is the prior close.
* **Significance:** use a circular time-shift null, report episodes as well as days, and use a multiverse with a joint p for free choices. Freeze pass/fail criteria before a run.
* **Each asset on its own data,** unless the idea is explicitly cross-asset. States are trailing-year percentiles, not fixed thresholds.
* **Writing for the owner:** they are an options trader and a visual learner.
  * Be concise and clearly directional, with no information floods.
  * Give the answer first, then the evidence, with a figure when it helps.
  * Say plainly when a result is unresolved or the data can't answer it.
* **Performance:** set `OMP_NUM_THREADS=1` for multiprocessing and for many small model fits.
