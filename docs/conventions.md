# Conventions

**Don't take these on trust.** Every rule below has the evidence it rests on and a command that re-tests it.
* Rules marked **choice** are design decisions, not findings. Each says how to test the alternative.
* If a check fails, or you find a flaw in it, the rule is what changes, not the evidence.
  * Agents write the challenge up in `research/agents/` and log it in `research/agents/INDEX.md`.
  * The owner adopts a change by editing this file and logging it under *Rule changes* at the bottom.
* These rules are a floor, not a ceiling. Better methods are welcome; propose them the same way.

Run all checks:

```bash
cd engines/gamma && python verify.py --study ../../research/microstructure          # engine: 8 checks
cd research/microstructure && OMP_NUM_THREADS=1 python rule_checks.py              # testing rules: 5 checks
```

## Timing

**1. A state read at day t's close may only predict day t+1 onward.**
* Evidence: counting day t's own move gave a fake +40-point edge. Measured from t+1, the same trigger shows −9 points.
* This bug produced two false findings that were later retracted (REPORT §4z).
* Check: `rule_checks.py` R1.

**2. Open interest dated t is the prior close's positions.**
* Evidence: ThetaData stamps OI at about 06:30 ET. The change in OI from t to t+1 tracks day t's volume (rank correlation 0.93) more than day t+1's (0.77).
* Check: `verify.py` B2.

**3. Confirm what hand-picked dates mark before testing day-of-week effects.**
* Evidence: dates given as "the week of" a move all fall on Mondays (100%). The moves' actual biggest days fall on a single weekday at most 38% of the time.
* Check: `rule_checks.py` R4.

## Significance

**4. The null must keep the signal's persistence: shift the signal in time, don't shuffle days.**
* Evidence: with no true effect, a time-shift null gives 2.8% false positives at p < 0.05. Drawing random days gives 8.8% (full run, 400 replicates).
* Check: `rule_checks.py` R2, or the full `edge_lab.py`.

**5. Count episodes, and know what size of edge the data can show.**
* Evidence: with about 60 real episodes, an edge needs roughly +16 to +17 points to be detected 80% of the time. Seven hand-picked events never reach 80% detection, even at +20 points.
* Check: `rule_checks.py` R3. The full power curves are in `edge_lab.py`, with pass criteria frozen in `research/microstructure/edge_lab_controls.md`.

**6. Free choices get a multiverse with one joint p.**
* Free choices are thresholds, horizons and move definitions.
* Evidence: `own_multiverse.py` runs 2,016 specifications against 300 shifted nulls. Its joint p is the number to quote, not the best single specification.
* Check: rerun it, or add specifications and see whether the joint p holds.

**7. Freeze the pass/fail criteria before running.**
* Evidence: in `edge_lab_controls.md` (committed before the run), a review of the written criteria found one planned check that could not fail. It was replaced before the first run, and the change is logged in the file.
* Check: compare the commit dates of the controls file and the results.

## Data choices

**8. Use `^GSPC`, not SPY, for S&P returns around monthly expiry.**
* Evidence: on all 85 quarterly expiry Fridays since 2005, SPY's close lagged the S&P by 0.50 points on average. On other days the gap is 0.008 points. This is the dividend drop.
* Check: `rule_checks.py` R5.

**9. Choice: states are percentiles against the trailing 252 sessions** (bottom, middle and top thirds), not fixed thresholds.
* Reason: levels drift over years. A fixed cutoff silently changes meaning.
* Test the alternative: swap in fixed thresholds in a multiverse and compare the joint p.

**10. Choice: analyse each asset on its own data** unless the idea is explicitly cross-asset.
* Reason: QQQ gamma added no consistent signal to single stocks (4 of 16 tests, with mixed signs; measured before the timing fix and not rerun). The MSFT/SPY release effect did not carry over to TSLA (p 0.53).
* Test the alternative: add the other asset as a control and check the joint p.

## Practicalities (verify by timing)

* Use `OMP_NUM_THREADS=1` with multiprocessing or many small model fits. Without it, the math library starts its own threads in every worker and runs crawl; one case went from minutes per fit to about 2 ms.
* Write live or intraday snapshots to a scratch folder, never over tracked data.
* Keys live in environment variables only. Licensed raw data (ThetaData chains, paid samples) stays out of git; derived daily metrics may be committed.

## Rule changes

| Date | Rule | Change | Evidence |
|---|---|---|---|
| 2026-10-14 | edge_lab check F1 | Replaced a check that could not fail with a random-day-null check, before any run | `edge_lab_controls.md` amendment log |
