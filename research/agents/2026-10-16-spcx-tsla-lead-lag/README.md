# Does SpaceX (SPCX) lead TSLA, so it can be used as a signal?

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-16
**Started:** 2026-10-16   **Pre-registered at commit:** (the first commit of this README, pushed before any return was computed)
**Type:** new question (cross-asset; the owner's observation)
**Verdict:** _to be filled in after the run_

## Question

The owner noticed that SPCX (Space Exploration Technologies, on Nasdaq since 2026-06-12) and TSLA have moved together since SPCX listed.

Moving together on the same day is not a signal: by the time you see SPCX's move, TSLA has already made its own. SPCX is only usable if its move comes **first**, in one of three ways:
* yesterday's SPCX move predicts today's TSLA move;
* SPCX's last 5 minutes predict TSLA's next 5 minutes;
* a gap that opens between the two closes, with TSLA catching up.

Each test controls for TSLA's own last move and the market (QQQ), so SPCX must add something those don't.

## Data

* Yahoo daily bars for SPCX, TSLA and QQQ, 2026-06-12 to 2026-10-15: about 86 daily returns. Day 1's return from the IPO price is not available.
* Yahoo 5-minute bars, regular hours, for the last ~60 sessions only (Yahoo's limit). Returns within a session only; the overnight gap is excluded. The first weeks after the IPO are therefore not in the intraday test.

## Tests and pass/fail criteria (fixed before any result)

| | Statistic | Null |
|---|---|---|
| **D0** (description, not a test) | Same-day correlation of daily returns, SPCX vs TSLA; the same after removing QQQ; TSLA vs QQQ for comparison; 20-day rolling correlation | none |
| **H1** daily lead | Partial correlation of TSLA's return on day t+1 with SPCX's on day t, controlling for TSLA's and QQQ's day-t returns | Circularly shift the SPCX series against the others, every offset from 10 to n−10 |
| **H2** intraday lead | Partial correlation of TSLA's next 5-minute return with SPCX's last 5-minute return, controlling for TSLA's and QQQ's last 5-minute returns, pooled over sessions | Pair SPCX's session d with TSLA's session d+k, every k ≠ 0 (keeps the intraday pattern, breaks the same-day link) |
| **H2r** reverse (diagnostic) | The same with the roles swapped: does TSLA lead SPCX? | as H2 |
| **H3** catch-up | Correlation of TSLA's next-5-session return with the prior 5 sessions' SPCX-minus-TSLA return gap | Circular shift of the gap series, offsets 10 to n−10 |

* **Usable signal:** H1, H2 or H3 with p < 0.0167, which is 0.05 split over the three tests.
* All p-values are two-sided: a negative lead would also be usable.
* For H2, also report how much of TSLA's next 5-minute move the lead explains, and the size of the move it implies. A real but tiny lead is not tradable.
* **Power, stated in advance:**
  * About 86 daily returns can only detect a daily lead with |r| ≥ ~0.33 (80% power at α 0.0167).
  * The intraday test has about 4,500 bar pairs and can detect |r| ≥ ~0.05.
  * A null daily result therefore means "no strong lead", not "no lead".
* **What would prove the idea wrong:**
  * All three tests have p ≥ 0.0167.
  * Or H2r shows TSLA leading SPCX, which would make SPCX the follower.

## Results
_to be filled in after the run_

## Threats to validity
_to be filled in after the run_

## Reproduce
```bash
python spcx_lead.py            # fetches Yahoo bars into data/ (gitignored), runs D0-H3, writes out/
```
