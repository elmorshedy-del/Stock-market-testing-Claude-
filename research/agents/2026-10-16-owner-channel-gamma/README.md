# The owner's weekly TSLA channel (lower line → mid line → upper line) against the options state

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-16
**Type:** descriptive.
* The lines were drawn by the owner on a finished chart, so they fit their own history by construction.
* This shows which options states **go with** each channel zone. It cannot show that the channel predicts.
* Forward returns by zone are reported only as in-sample description.
**Committed before the run.**

## The owner's observation
Each leg moves up from the lowest lines, consolidates at the middle line, then runs to the top line (TradingView, weekly, log scale, 2022–2026).

## Reconstruction of the lines
The owner's screenshot (`data/owner_channel_screenshot.png`, gitignored) is read through its log price axis (2200 … 41) and year axis.

| Line | Anchor 1 | Anchor 2 | Slope | Level on Oct 16, 2026 |
|---|---|---|---|---|
| A, upper | 2022.655, $179 | 2027.188, $656 | 0.286 ln/yr | ~$587 |
| B, mid | 2022.931, $156 | 2027.456, $571 | 0.287 | ~$474 |
| C, second lowest | 2022.983, $129 | 2028.484, $578 | 0.273 | ~$365 |
| D, lowest | 2022.421, $103 | 2028.207, $497 | 0.271 | ~$339 |

Reading error is about ±3% per line. The screenshot itself was taken on Oct 16 at $364.62, which sits on line C, so the reconstruction matches that point.

## Zones and metrics (daily, Aug 2022 – Oct 2026)
* **Zones:**
  * below D
  * D–C (the lower band)
  * C–B
  * B–A
  * above A
* **For each zone:**
  * days in the zone
  * share of days below the gamma flip, and the median distance from it
  * median dealer-gamma percentile
  * median near-price OI percentile, and the share of days freed
  * in-sample next-20-session return and up-burst odds within 10 sessions
* **Figure:** price with the 4 lines; price vs flip (shaded blue below, orange above); dealer-gamma percentile; near-price OI percentile. All on one time axis.

## Results

![channel and gamma](out/channel_gamma.png)

`out/zones.csv`; Aug 2022 – Oct 14, 2026.

| Zone of the owner's channel | Days | Below the flip | Median vs flip | Dealer-gamma pct (median) | Near-price OI pct (median) | Freed | Next 20 sessions (in-sample) |
|---|---|---|---|---|---|---|---|
| below D (lowest line) | 47 | **72%** | −2.2% | **18** | 47 | 36% | +21.1% |
| D–C lower band | 94 | 37% | +1.0% | 34 | 56 | 34% | +10.1% |
| C to B (lower half) | 325 | 21% | +2.9% | 48 | 49 | 32% | +6.2% |
| B to A (upper half) | 346 | 17% | +4.7% | 63 | **67** | **20%** | −3.1% |
| above A (upper line) | 245 | 21% | +5.1% | **69** | 56 | 32% | −9.4% |

* **The channel and the options state move together, step by step.**
  * At and under the lower lines, TSLA is mostly below its flip, with dealer gamma at its most negative: the coiled spring of the full setup.
  * Up through the channel, the price sits further above the flip and gamma turns steadily more positive.
* **The consolidation above the mid line coincides with pinning.** B to A has the most open interest near the price (67th percentile) and the fewest freed days (20%).
* **Why they line up:** both measure the same thing from two angles. A drop toward the lower lines leaves the price under a lagging flip; a run to the upper lines leaves it far above a rising one (see `2026-10-16-named-moves-gamma`).
* **Limits:**
  * The lines were drawn after the fact. The forward returns are in-sample, so they overstate any edge.
  * Earlier channel studies found touches of fitted channels no better than a random walk (`2026-10-15-channel-reversion-*`).
  * The options state, by contrast, was tested forward (§4w, §4ad).
* **Now (Oct 16):**
  * TSLA ~$364 sits on line C (~$364), in the D–C lower band. D is about $338.
  * After today's expiry TSLA is above its flip (~$348–356) and freed: the channel says "lower band", the options say not yet coiled.
  * A drop to line D would bring it near or below the flip, which is the full setup.
