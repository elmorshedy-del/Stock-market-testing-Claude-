# SPY in the owner's daily channel: what the moves to the upper line had, and what a 2024-25-style year needs

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-16
**Type:** descriptive. The owner's screenshot is the input. Nothing new is tested here; it lines up the channel against the results already tested in `research/microstructure/REPORT.md` (§4d, §4g, §4x).
**Builds on:** owner-channel-gamma (the TSLA version), microstructure §4d (S&P dealer gamma → up-legs), §4g (eras), §4x (Q4 window)
**Verdict:**
* **The channel tracks the S&P gamma cycle.**
  * Both moves from the lower to the upper line (from Apr 21 and from Jul 23) are the two 2026 "legs" §4d already documents. Each started after dealer gamma fell to a low and stalled when gamma rebuilt to its 99th percentile.
  * The touches that stalled at the mid line (Sep 15, Oct 1) came with VIX at 16–17. §4d's tested result is that the index cannot sprint without vol.
* **The channel's own slope is an ordinary Q4.** Riding the lower line to Dec 31 is +3.6% from today, about the median Q4 since 1971 (+3.6%), and lands at a 2025-like year (+16.8%).
  * The upper line by year-end (+8%) is about a top-fifth Q4.
  * A 2024-like year (+23%) is above the channel and was matched in 13% of years.

## The owner's observation
* SPY rose from the lower line to the upper line twice: from late April, and from late July.
* The owner asks whether that repeats from here (SPY is on the lower line today) and whether it fits the tested data.
* The owner also asks for the "narrative" of another green year in the range of the last two (+23.3% in 2024, +16.4% in 2025) and the Q4 run-up.

## Line reconstruction (`spy_channel.py: detect_lines`)
* **The lines:** read from the screenshot's blue pixels, not by eye.
  * Each of the three lines is fitted through 851 pixel columns. Residual scatter is 0.4–0.5 px.
  * The three slopes agree to 0.02%, so the lines are parallel.
* **Price axis:** fitted to the 17 gridlines.
  * A log scale fits within 0.007% at every label; a linear scale is off by up to 0.84%. So the chart is log.
* **Time axis:** fitted to the four month labels on a trading-day axis, which is how TradingView spaces bars.
  * The residuals are under 0.6 px (about 0.1 bar). A calendar axis is off by up to 2.8 px.
* **The channel:**
  * 4.3% wide. The mid line sits at 0.45 of the width above the lower line, not halfway.
  * It rises about 19% a year.
  * 90% of closes since SPY first closed inside it (Apr 17) have been inside it.
* **Levels:**

| | Lower | Mid | Upper |
|---|---|---|---|
| Oct 15 | $767.9 | $782.5 | $800.7 |
| Nov 30 | $784.5 | $799.4 | $818.0 |
| Dec 31 | $796.4 | $811.6 | $830.5 |

## Data
* **SPY and VIX daily bars:** Yahoo, fetched fresh on Oct 16 into `data/` (gitignored).
  * The committed `SPY_1d.json` has a stale intraday Oct 15 bar ($770.19 against the $771.79 close).
  * Today's bar is intraday. All statistics use closes through Oct 15.
* **S&P dealer gamma (GEX) and dark-pool buying (DIX):** SqueezeMetrics, fetched fresh to the Oct 15 row.
  * Each is ranked against its trailing 252 days, the same way as `forecast.build`.
* **SPY's own gamma flip:** `research/microstructure/out/td_gamma_SPY.csv`, through Oct 9.
* **The Q4 record:** S&P 500 (^GSPC) closes, 1971–2025, from the last close on or before Oct 16 to the last close of the year.

## Touches of the lower line (`out/touches.csv`)
**Definition:** a touch is a day whose low reaches the lower line after a close at or above the mid line. The first day inside the channel counts too.

| First touch | S&P GEX pct | VIX | DIX pct | SPY vs its own flip | What followed |
|---|---|---|---|---|---|
| Apr 21 | 0.52 (after the −$7.2B trough on Mar 27, §4d) | 19.5 | 0.61 | −0.4% | **upper line May 13 (16 sessions)** |
| Jun 26 | **0.00** | 18.4 | 0.19 | −2.3% | stalled at 0.71 of the width |
| Jul 23 | **0.11** | 18.7 | 0.76 | −1.8% | **upper line Aug 4 (8 sessions)** |
| Sep 15 | 0.40 | 17.2 | 0.72 | −1.6% | stalled at the mid line (0.47) |
| Oct 1 | 0.44 | 16.4 | 0.81 | −0.6% | stalled at the mid line (0.46) |
| **Oct 14 (now)** | 0.31, then 0.52 on Oct 15 | 16.9 → 16.4 | 0.36 → **0.05** | (no chain after Oct 9) | ongoing |

**Read** (5 completed touches, descriptive):
* **The two launches are the two legs in §4d.** §4d describes the mechanism: a leg starts when dealer gamma is low or negative and ends when the rally rebuilds gamma to an extreme. Here that was the 99th percentile on Apr 16–17 and on Aug 5.
  * **April:** gamma bottomed on Mar 27. The leg ran through the touch of Apr 21.
  * **July:** after July's expiry and the Jul 22 VIX settlement, gamma sat at its 10th–20th percentile on Jul 23–28. The leg then ran through earnings.
* **VIX separates better than GEX here.**
  * Both launches had VIX at 18.7–19.5.
  * The September and October stalls had 16–17.
  * Jun 26 had gamma at zero and VIX at 18.4, and still stalled. It was the only one of the five that rose above the mid line without reaching the upper line.
  * This is 5 cases and descriptive. It matches §4d's tested finding that in low-VIX markets the chance of an up-leg is near zero whatever gamma does.
* **SPY was below its own flip at every touch,** so its own flip does not separate the launches from the stalls.
* **Now:**
  * Gamma is middling: 0.52 on Oct 15.
  * VIX is 16.4, the 38th percentile of its year.
  * Dark-pool buying fell to its 5th percentile on Oct 15. §4y found the high side of DIX weakly supportive (+0.9 pts over 20 sessions, p 0.06), so this is the unsupportive side.
* **The calendar matches July's.** Monthly expiry is today, the VIX settlement is Wed Oct 21, and mega-cap earnings follow. That is the window where gamma fell to its bottom fifth in July.

## The tested result this leans on (§4d, §4g; not re-tested here)
* **S&P dealer gamma in its bottom fifth:**
  * 24% of days are followed by a top-decile 10-day rise, against a 10% base and 2% in the top fifth.
  * Below zero: 33%.
* **It holds in every era,** including 0DTE: 25% → 2% since May 2022 (§4g).
* **It needs vol:** in low-VIX markets the up-leg chance is about zero whatever gamma does.

## Q4 and the year (`out/q4.csv`)

| S&P, Oct 16 close to Dec 31 | Years | Up | Median | Middle half |
|---|---|---|---|---|
| All years 1971–2025 | 55 | 78% | +3.6% | +0.7% to +6.6% |
| S&P up on the year at Oct 16 | 39 | 79% | **+4.5%** | +0.9% to +6.8% |
| Midterm years (2026 is one) | 13 | 69% | +3.6% | −2.1% to +7.2% (2018: −10.8%) |
| 1990–2025 | 36 | 81% | +5.1% | +1.4% to +7.2% |

**What the year needs** (SPY closed 2025 at $681.92; it is +12.8% YTD at today's $768.9):
* **A 2025-like year (+16.4%):** $793, which needs +3.2% from here. 53% of years did that.
  * The median Q4 gets there.
  * So does riding the lower line to Dec 31 ($796, +16.8%).
* **The mid line at Dec 31:** $812 (+19.0%).
* **The upper line at Dec 31:** $830 (+21.8%). That needs about +8%, roughly a top-fifth Q4.
* **A 2024-like year (+23.3%):** $841, which needs +9.4%. 13% of years did that (7 of 55).
  * It is above the channel's upper line at year-end, so it needs a breakout.
* **Midterm years are no better than other years from this date,** and more spread out. The well-known midterm strength mostly comes earlier, off the October low.

## Threats to validity
* **The lines are the owner's, drawn with hindsight** through these touches.
* **Small sample:** the touch table is 5 completed cases.
* **The future part of the time axis assumes NYSE holidays.** TradingView's future bars may not skip them, which would shift the projected levels by under a day.
* **Q4 history is price-only S&P,** not SPY total return.

## Reproduce
```bash
cd research/agents/2026-10-16-spy-channel
curl -sS -o data/SPY_1d.json "https://query1.finance.yahoo.com/v8/finance/chart/SPY?interval=1d&range=2y" -H "User-Agent: Mozilla/5.0"
curl -sS -o data/VIX_1d.json "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=1d&range=2y" -H "User-Agent: Mozilla/5.0"
curl -sS -o data/DIX.csv https://squeezemetrics.com/monitor/static/DIX.csv
OMP_NUM_THREADS=1 python spy_channel.py
```
* The screenshot is `data/owner_spy_channel_screenshot.png` (gitignored, like the TSLA one). Without it, `detect_lines` cannot run; the fitted pixel lines are saved in `out/lines.json`.
* Fresh data will move today's numbers.

![SPY channel](out/spy_channel.png)
