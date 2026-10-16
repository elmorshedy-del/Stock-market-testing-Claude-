# The owner's named TSLA moves, bottom to top: price, flip, dealer gamma, freed state and walls on one timeline

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-16
**Type:** descriptive (8 hand-picked moves). **No pass/fail.** Eight events cannot establish an edge (§4ad). This shows how the metrics track so the owner can see the mechanics; any rule seen here needs its own pre-registered test.
**Committed before the run.**

## The owner's view to check
* The trends were driven by negative gamma.
* That only works if the flip keeps moving up ahead of the price during the rally.
* The top comes when gamma turns heavily positive again, which could serve as a profit-taking or top signal.

## Moves
The 8 moves in `research/microstructure/named_weeks.MOVES` (the owner's dates):
* Oct 2021
* Jan 2023
* May 2023
* Jun–Jul 2024
* Oct–Nov 2024
* Apr–May 2025
* Sep 2025
* Oct 2025

## Bottom and top, fixed now (mechanical, so they cannot be picked to fit a story)
* **Top:** the highest close from the window's first day to 15 sessions after its last day.
* **Bottom:** the lowest close in the 15 sessions before the window up to the top.

## Metrics, daily (`research/microstructure/out/td_gamma_TSLA.csv`; the row for day t uses OI going into day t)
* the price and the gamma flip, with the zone below the flip shaded (dealers short gamma)
* call wall and put wall
* dealer gamma at the price: own-gamma percentile vs its trailing year (low = most negative)
* freed: near-price OI percentile at or below 1/3

## Read-outs per move
At the bottom, through the rally, and at the top:
* price vs flip
* the share of rally days below the flip
* whether the flip rose during the rally
* gamma percentile at the bottom and at the top
* freed at the bottom and at the top
