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
