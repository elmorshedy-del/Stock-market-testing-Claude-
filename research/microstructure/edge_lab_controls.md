# edge_lab controls — frozen before the run (2026-10-14)

Protocols followed: BootLoops `planted-truth` and `acceptance-gate`
(github.com/BootLoops-ai/skills). This file was written and committed before
`edge_lab.py` was run. The pass criteria below are not to be edited after the run.

**Question.** How big must an edge be, and how many events does it need, before
this repository's backtest method can tell it from luck on a stock like TSLA?
Does the method actually catch the two mistakes made in this project?

**Production path under test.** This is the path used for the TSLA burst results
(§4w ladder, §4z).
* TSLA daily closes → `stock_now.burst_days` (up-burst = +5% day or +9% over two days).
* Outcome = an up-burst in sessions t+1..t+h.
* Lift = mean outcome on signal days minus mean on all days.
* p = share of circular shifts of the signal (offset ≥ 60 sessions, 1,000 shifts) with a lift at least as large.

Real data: TSLA 2021-01-01 .. 2026-10-09.

## Plants and nulls

* **P1, shift-null calibration.**
  * Setup: the real outcome series; the signal is the real "freed and below flip" series slid by a random offset of at least 120 sessions (no true relation). 400 replicates.
  * Pass: the false-positive rate at p < 0.05 is within [2.5%, 8%].
* **P2, bootstrap-null calibration.**
  * Setup: TSLA daily returns resampled in blocks (stationary bootstrap, mean block 20) → new closes → bursts; the real signal is unshifted. 400 replicates.
  * Pass: the false-positive rate at p < 0.05 is within [2.5%, 8%].
* **P3, plant recovery through the full path.**
  * Setup: a shifted (unrelated) signal, as in P1. After each signal day, with probability q, one of days t+1..t+3 (uniform) gets its return raised to at least +6%. Then closes → bursts → outcome → lift. q ∈ {0.1, 0.2, 0.3}; 200 replicates each.
  * Expected lift comes from a separate simple implementation (explicit loop, no burst de-duplication), never from the production code.
  * Pass: the mean recovered lift is within 2 pts of the mean expected lift, for every q.
* **P4, power curve (the deliverable).**
  * Same plant as P3, q ∈ {0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.45}, 300 replicates each. Detection = p < 0.05.
  * Three signal profiles:
    * (a) the real "freed and below flip" persistence (about 150 days, about 60 episodes), 3-session outcome
    * (b) the real "freed" persistence, 3-session outcome
    * (c) 7 single-day events at least 60 sessions apart (like a hand-picked list of named moves), 10-session outcome
  * Report: detection rate against true lift; the smallest lift detected 80% of the time.

## Corruptions (each must be caught; a clean twin must pass)

* **C1, same-day timing leak** (the §4z bug).
  * Setup: the signal is a dip trigger (today's return ≤ −4%). The leaky twin counts down-bursts in t..t+2; the clean twin counts t+1..t+3.
  * Detector: compute the lift both ways. Flag "same-day leak" when the same-day lift exceeds the forward lift by more than 5 pts and the forward p ≥ 0.05.
  * Pass: it fires on the leaky twin and stays silent on the clean twin.
* **C2, week-start dates read as event days** (the §4ac mistake).
  * Setup: an event-date list.
  * Detector: flag when 90% or more of the dates share one weekday.
  * Pass: it fires on the week-start version of the named moves' biggest days and stays silent on the actual biggest days.

## Machinery nulls

* **N1:** an all-False signal → "no events" (no lift, no p), never 0.
* **N2:** an all-True signal → lift exactly 0.
* **N3:** an all-zero outcome → lift exactly 0.

## Proving each check can fail

* **F1 (amended before the first run, see below):** in P1, replace the time-shift null with an iid null that draws signal days at random and ignores their persistence. The calibration check must fail: false-positive rate above 8%.
* **F2:** in P3, plant with a k that can fall on day t (k ∈ {0, 1, 2}). Recovery against the forward-window expectation must miss by more than 2 pts.

## Applying the gate to real results

The real "freed and below flip" lift (§4w) is placed on the profile (a) power curve, and the 7 named moves on profile (c).
* A real result counts as **robust** only if its lift exceeds profile (a)'s 80%-power lift and its p < 0.05.
* Anything below that lift is **unresolved**, not "confirmed".

## Amendment log

* **2026-10-14, before any run of `edge_lab.py`:** F1 as first written (swap the p-value inequality) could not fail.
  * With no true effect, both one-sided p-values are uniform, so the false-positive rate stays near 5% either way. It was a check that cannot fail (planted-truth §5).
  * Replaced by an iid-null break, which ignores the signal's persistence and should inflate false positives.
  * No result had been seen when this was changed.
