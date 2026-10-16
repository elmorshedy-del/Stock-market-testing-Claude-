# Is a day that trades below the flip but closes back above it the same setup as a close below?

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-16
**Started:** 2026-10-16   **Pre-registered at commit:** (this commit; pushed before any outcome was computed)
**Type:** new question (the owner's hypothesis), builds on the full setup (microstructure §4w, reproduced by `edge_lab.py`)
**Verdict:** (after the run)

## Question
The owner's two paths into the Oct 21 report:
1. TSLA dips into the report and closes below the flip, which turns the full setup on; the report then launches it.
2. The report reaction drops, then climbs back the same day to close flat or green. The owner's view: structurally the same as path 1, only the flush happens inside the day instead of at a close.

Path 1 is the tested full setup (freed AND close below the flip → up-burst within 3 sessions 39% vs 17% down, 155 days / 59 episodes since 2021).
Path 2 has never been measured. The full setup is read at the close, and an earlier check found no edge on the day the close reclaims the flip (16% / 16%). This test asks whether an *intraday* dip below the flip that recovers by the close carries the same edge.

## Data
* `research/microstructure/edge_lab.load()`: the production analysis frame, 2021-01-04 to 2026-10-14, 1,452 days. It includes the freed state (near-OI percentile ≤ 1/3) and `below` (close below the flip, or no flip in range with negative gamma).
* The flip (row t) is converted to Yahoo's split-adjusted units with the split factor (spot ÷ close, nearest of 1, 3, 15).
* Yahoo daily low for day t.
* Outcome: the production up-burst mark (`burst_days`: +5% in a day or +9% in two) in sessions t+1 to t+3, `edge_lab.outcome(..., 3)`.

## Groups (freed days only, read at the close of day t)
* **A, the full setup:** closed below the flip. 155 days, 59 episodes.
* **B, pierce and reclaim:** did not close below the flip, but the day's low was below it. 39 days, 31 episodes.
* **C, stayed above:** the low never went below the flip. 216 days, 82 episodes.

The group sizes were counted before the run; no outcomes were looked at.

## H1 (primary)
* **Statistic:** the up-burst-within-3 rate on B days minus the rate on all 1,452 days.
* **Null:** circular shift of the B marks, 1,000 shifts of at least 60 days, using `edge_lab.edge_test`, the same machinery as the published full setup.
* **Pass:** p < 0.05 with a positive lift. The smallest attainable p is 0.001.
* **Power:** 31 episodes. A lift as large as the full setup's (+23 pts) is about 2 standard errors, so a real but smaller effect can fail.

## Secondary (descriptive, no pass/fail)
* The up- and down-burst rates for A, B and C side by side. The owner's "structurally the same" claim reads as B ≈ A.
* B on all days, freed or not (232 days, 172 episodes), with its own shift-null p.
* Every report reaction day since 2020 whose low went below the flip or the prior close and that closed above the flip, with the next 3 and 20 sessions.

## Prediction written now
* B falls between C and A, closer to C.
* H1 does not pass: the earlier reclaim result says the close is what carries the state, and B is small.

## Threats to validity
* **Approximate intraday flip.** The flip on row t is computed from end-of-day quotes, so the intraday flip was at a slightly different level. An intraday pierce of a level computed at the close is an approximation.
* **Small B.** 39 freed days.
* **Partly overlapping groups.** B days often sit next to A days in the same episode.

## Results
(after the run)

## Reproduce
```bash
OMP_NUM_THREADS=1 python pierce_reclaim.py
```
