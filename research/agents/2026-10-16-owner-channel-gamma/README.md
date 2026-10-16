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

## Follow-up: why the Jan 2023 leg overshot while later legs paused at the mid line (`legs.py`, `out/legs.csv`, `out/legs.png`; descriptive, 4 legs)

![legs](out/legs.png)

| | Jan 2023 | Apr 2024 | Apr 2025 | Jul 2026 (now) |
|---|---|---|---|---|
| Low (close) | $108.1, Jan 3 | $142.1, Apr 22 | $221.9, Apr 8 | $298.3, Jul 29 |
| **Below the 52-week high** | **−73%** | −52% | −54% | −39% |
| Below line D | −10.5% | −17.4% | −0.6% | −6.4% |
| Below the flip | −16.4% | −15.0% | −8.0% | −3.7% |
| Dealer-gamma pct / near-OI pct at the low | 10 / 3 | 5 / 1 | 9 / 5 | 2 / 5 |
| ATM IV at the low (pct of its year) | 86% (99) | 64% (100) | 98% (100) | 49% (71) |
| **IV during the climb** | **stayed at its 60–80th pct** | fell to ~5th, rose late | fell to ~50th | fell to ~0, then 20–35th |
| Calls/puts OI at the low | 1.26 | 1.12 | 1.09 | 1.24 |
| Highest channel position in 80 sessions (A = 1) | **1.09** | 0.71 | 0.85 | 0.26 so far |
| Sessions within 0.08 of the mid line | 7 | 12 | **29** | 0 |
| S&P over the window | +8% | +9% | +25% | +6% |
| TSLA 40 sessions after the low | **+88%** | +32% | +50% | +27% |

**What separates Jan 2023 in the data:**
* **The deepest crash before the low:** −73% from its high, against −39% to −54% for the others. This was the first leg out of a bear-market capitulation, not a leg inside an established channel.
* **IV stayed high through the climb.** The market kept paying up for options all the way up; in every later leg IV collapsed as the price recovered.

**What does not separate it:**
* Depth below the flip (Apr 2024 was as deep).
* Dealer gamma and the freed state at the low (all near their extremes).
* The market backdrop (Apr 2025 had a far bigger S&P rally, and TSLA still consolidated at the mid line).
* The spot-vol correlation in the first 30 sessions: Jan 2023 +0.14, Apr 2024 +0.10, Apr 2025 −0.62, now +0.61. Mixed.
* The other big overshoot, Nov–Dec 2024 (the election), did come with spot-up/vol-up (+0.45 over 20 sessions, near the 90th percentile of the measure).

**Read:**
* The overshoots came out of an extreme (a −73% crash, or an event like the election) with options demand that stayed high.
* The clean legs came out of ordinary pullbacks, with IV deflating as the price rose. Those consolidate at the mid line.
* This is 4 legs; a hypothesis for a pre-registered test, not a finding: does IV holding up during a rally off the lower lines predict an overshoot of the upper line?

## Follow-up 2: was the July 2026 dip to line D the launch pad? (`report_launch.py`, `out/reports.csv`, `out/report_launch.png`; descriptive, written after seeing the legs)

The owner's question: the 2023, 2024 and 2025 legs shot straight off line D. In 2026, TSLA dipped to D in July and has drifted between C and D since. That looks like 2025, which also hung around C and D before its shot came from D, where the flip was. So is the July dip the launch pad, and how does it fit the Q4 catch-up and the Oct 21 report?

![report launch](out/report_launch.png)

**What the legs have in common:** every launch off the lower lines started on an earnings report.
* **Jan 2023:** low on Jan 3; the launch came at the Jan 25 report.
* **Apr 2024:** low on Apr 22; the launch came at the Apr 23 report.
* **Apr 2025:** lows on Mar 10 and Apr 8 (two touches of D, with full-setup runs from Feb 21 to Apr 22); the launch came at the Apr 22 report.
* **Oct 2024:** the Q3 report from line C.
* **Jul 2026 is the exception in order:** its low (Jul 29) came *after* a report, the −14.5% reaction on Jul 23, not before one. It had the deepest gamma of the four legs (gamma pct 2, near-OI pct 5, 9 full-setup closes), but no report to launch it. It crept from D to C instead (highest channel position 0.26 in 56 sessions, against 0.71–1.09 for the other legs).

**Every report reaction since Aug 2022** (16 reports, sorted by channel position at the close before; D = 0, A = 1, B = 0.58; the 2026 report dates are from Tesla's releases, because the volume detector in `q4_forensics.py` picks Apr 15 for Q1 2026):

| Report reaction | Position before | vs flip before | Reaction day | 20 sessions later |
|---|---|---|---|---|
| 2024-04-24 | −0.34 | −11.0% | +12.1% | **+29%** |
| 2025-04-23 | 0.10 | −3.3% (full setup) | +5.4% | **+45%** |
| **now: 2026-10-22** | **0.14** | **about +3–5% vs the post-expiry estimate** | | |
| 2024-10-24 | 0.15 | +3.0% | +21.9% | **+60%** |
| 2026-07-23 | 0.30 | +1.1% | −14.5% | −6% |
| 2023-01-26 | 0.33 | +5.5% | +11.0% | **+40%** |
| 2024-01-25, 2026-04-23, 2024-07-24 | 0.50–0.56 | 0 to +18% | −12% to −4% | −10% to +8% |
| the 8 above the mid line B | 0.60–1.46 | | 2 of 8 up | 1 of 8 up, median −7% |

* **Below the mid line:** 5 of 8 reports were higher 20 sessions later (median +18%).
* **The five closest to D:** 4 launched (+29% to +60% in 20 sessions), and 1 failed: Jul 2026, which produced the July low.
* **The flip does not separate them:** the launches came from below the flip (Apr 2024, Apr 2025) and from above it (Jan 2023, Oct 2024). The failure came from 1% above it.
* **The closest match to now is Oct 2024:**
  * a Q3 report in a catch-up year;
  * channel position 0.15 (now 0.14);
  * about 3% above the flip, without the full setup.
  * Its +60% was helped by the election inside the 20 sessions.
* **What the data shows for Oct 21, not tested:**
  * The report is the first since the July low at D, the slot where the earlier launches came.
  * TSLA sits where 4 of the last 5 launches started.
  * The one failure from this spot was a report that disappointed (an EPS miss and a capex shock).

**Threats to validity:**
* **Hindsight lines.** The owner drew line D under these very lows, so "near D before a launch" is partly built in.
* **Small sample.** There are 16 reports and 5 near D, with no p-value. The news in the report dominates any position effect.
* **The flip band ($348–356) is an estimate** from Friday's expiry. Recompute it Monday with real OI (`research/microstructure/tsla_live.py`).

**Honest test, proposed and not yet run:** refit the channel lines walk-forward, using only prices before each report. Then score report reactions by that position across TSLA and other high-beta names, and pre-register the design before the run.
