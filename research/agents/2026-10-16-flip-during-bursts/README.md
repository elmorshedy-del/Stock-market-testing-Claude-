# How do the flip and positions move around TSLA's up-bursts? (descriptive event study)

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-16
**Type:** exploratory, descriptive. **No pass/fail is applied.** Any pattern found here is a hypothesis for a separate, pre-registered test.
**Committed before the run.**

## Question
The owner's point: our setup reads where the price sits against the flip, but the flip is recomputed every day from positions. How does it move through a burst? Does it chase the price up, lag behind it, or stay put? And what do call OI, put OI, near-price OI and dealer gamma do?

## Design (fixed now)
* **Events:**
  * TSLA up-burst days 2020-2026 (`stock_now.burst_days`, unchanged). Day 0 is the burst day.
  * Split by the state at the close of day −1: in the full setup, below the flip only, or above the flip.
* **Daily series** from `research/microstructure/out/td_gamma_TSLA.csv`:
  * price
  * flip
  * distance above the flip
  * dealer gamma, scaled by price × total OI
  * call OI and put OI as % change vs day −1
  * near-price OI share (trailing-year percentile)
  * call and put walls
* **Timing:** the row for day t uses OI going *into* day t, so the burst day's own new positions appear from day +1.
* **Window:** day −10 to day +10. Medians, with the interquartile range.
* **Baseline:** the same paths around 2,000 random days, for comparison.

## Results
_to be filled in after the run_
