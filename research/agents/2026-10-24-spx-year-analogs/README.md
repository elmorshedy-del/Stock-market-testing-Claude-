# Which past years has the S&P's 2026 rhymed with, and what came next?

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-24
**Type:** analog study plus a skill test, pre-registered at 8c1c59b before any analog was computed. The only thing looked at beforehand was 2026's own path.
**Builds on:**
* microstructure §4x (state analogs for the S&P: neutral; the Oct–Dec season is the tailwind);
* spy-channel (the Q4 record since 1971).

**Verdict: 2026 does rhyme with past years, but a rhyme has never predicted the next month.**
* **The closest rhymes, by the shape of the year's path:** 1935, 1978, 1989, 2003 and 1933 (correlation 0.89–0.92).
* **From the same point in the year to the end of November** they went +5.5%, −3.4%, −0.3%, +2.7% and +6.9%: three up, two down.
* **Walk-forward over 1950–2025 fails**, with analogs picked only from earlier years:
  * correlation with the realized next month −0.14 (p 0.90);
  * right sign 47% vs 53% for the season.
* **Every secondary variant fails:** year-end outcome, K = 3 or 10, recent-month selector, RMSE selector, and calendar alignment (post-hoc).
* **The year's shape is a memory, not a map.**

## The owner's question
* Based on what the S&P has done this year and this month, what will next month look like?
* Is there a past year that rhymes with this one?
* Show it in a way that is neat, not only averages.

## 2026 so far (^GSPC, through the Oct 23 close)
* **Year to date:** +11.4%.
* **Spring correction:** −5.1% in March, low 6,344 on Mar 30.
* **V rebound:** +10.4% in April, +5.1% in May.
* **Summer plateau:** Jun −1.1%, Jul −0.1%, Aug +2.6%, Sep −0.5%.
* **October:** +2.2% to a new high of 7,819 on Oct 6, then a fade to −0.4% month to date.

## Design
* **Data:** ^GSPC daily from Yahoo, 1928 to 2026-10-23.
* **Path:** each year's log close relative to the prior year's last close, indexed by trading day. Today is trading day n0 = 204.
* **Similarity (primary, shape):** Pearson correlation between 2026's path and year Y's path over trading days 1..n0.
* **Also reported:**
  * the correlation over the last 21 sessions (this month's shape), each re-based to its start;
  * the RMSE of the raw paths (shape plus size).
* **Analogs:** the top K = 5 years by the primary score. A year needs at least n0 + 30 sessions.
* **Outcomes from day n0 in year Y:**
  * (a) to Y's last November close (**"next month"**);
  * (b) to Y's year end.
* **Picture:** 2026's path with the analog years overlaid, each scaled to 2026's level at day n0 and continued to year end.

## Pre-registered skill test: do analogs say anything about the next month beyond the season?
* **Walk-forward over Y = 1950 to 2025:**
  * Pick the top 5 analogs for Y among years before Y only, by the same primary score at Y's day n0.
  * Prediction: the mean of the analogs' outcome (a).
  * Naive prediction: the mean outcome (a) of all prior years (the season).
* **Scores (76 test years):**
  * the correlation of the analog prediction with the realized outcome;
  * the sign hit rate vs the naive hit rate;
  * the realized outcome when the prediction is in its top vs bottom third.
* **Null:** permute predictions across test years, 5,000 draws. One-sided p for the correlation.
* **Pass:** correlation > 0 with p < 0.05 **and** a sign hit rate above naive.
* **Secondary:**
  * outcome (b), to year end;
  * K = 3 and K = 10;
  * the recent-month score as the selector instead of the year-to-date shape.
* **Prediction (written before the run):** analogs add little beyond the season. November is up in most years, so the naive hit rate is hard to beat.

## Threats to validity
* With 76 test years the test has low power: it can detect a strong signal, not a subtle one.
* Choosing the shape metric is itself a degree of freedom. It is fixed above, and the alternatives are reported as secondary.
* Markets before 1950 differ (volatility, the role of index investing). They serve only as candidate analogs, never as test years.


## Results (`analogs.py`; outputs in `out/`)
![analogs](out/analogs.png)

**Run:** `python analogs.py <GSPC_max.json>`, which takes a few seconds. Outputs: `out/analogs.json`, `out/analogs.csv` (every year's scores and outcomes) and `out/analogs.png`.

### The rhymes (primary: correlation of the January-to-October path, trading-day index)
| Year | Shape correlation | This month's shape | From day 204 to end of Nov | To year end | Whole year |
|---|---|---|---|---|---|
| 1935 | 0.92 | −0.61 | +5.5% | +9.2% | +41.4% |
| 1978 | 0.91 | +0.50 | −3.4% | −1.9% | +1.1% |
| 1989 | 0.91 | +0.71 | −0.3% | +1.8% | +27.3% |
| 2003 | 0.89 | +0.28 | +2.7% | +7.6% | +26.4% |
| 1933 | 0.89 | −0.46 | +6.9% | +7.8% | +44.1% |
| **analog mean** | | | **+2.3%** | | |
| all years 1928–2025 | | | mean +0.55%, up 58% | | |

* **Closest by this month's shape alone:** 1971, 1989, 1999, 2004, 1970.
* **Closest by shape and size (RMSE):** 1964, 2003, 2017, 1944, 1963.
* **1989 and 2003 appear in more than one list.** 1989 was flat to the end of November; 2003 rose.

### The skill test (pre-registered)
* **Primary:** 75 test years, analogs from earlier years only. Correlation −0.14 (p 0.90). Right sign 47% vs 53% naive. **Fail.**
* **Realized outcome by the analogs' forecast:**

  | Forecast third | Mean next month | Up |
  |---|---|---|
  | bottom | +2.0% | 76% |
  | middle | +2.0% | 68% |
  | top | +0.9% | 52% |

  If anything it runs backwards, but not significantly.
* **Secondary, all fail:**

  | Variant | Correlation (p) |
  |---|---|
  | year-end outcome | −0.02 (0.57) |
  | K = 3 | −0.08 |
  | K = 10 | −0.04 |
  | recent-month selector | −0.13 |
  | RMSE selector | −0.01 |

### Post-hoc check: calendar alignment
* **Why:** exchanges traded on Saturdays until 1952, so "trading day 204" falls on a later calendar date in old years (1933: Nov 2).
* **Fix:** every year is re-indexed to 2026's calendar.
* **Result:** the same five rhymes (1935, 1989, 1978, 1933, 2003). The walk-forward still fails: correlation −0.19, p 0.95.
* **The figure uses this alignment.**

### Reading
* **This year's shape:** a March flush (−7% year to date at the low), a V in April and May, a flat summer, and an October stall after a new high.
* **The five years that drew the same curve did not agree on what came next.** In 75 years of out-of-sample tests, the curve has carried no information about the following month.
* **What has carried information** in this repository is the market's positioning state: the S&P gamma rungs, ARMED, and the VIX × gamma cells (spy-channel follow-ups). See those for the month ahead.

## Amendment 2 (owner's follow-up: which years had a similar macro background?). Pre-registered before any macro analog was computed.
**Question:** which past years looked like September 2026 in their macro and valuation backdrop, and did those years say anything about what came next?

**Data:**
* the repository's macro panel (`2026-10-15-channel-reversion-macro/out/macro_monthly.csv`; Fed H.15 rates, BLS CPI, dollar index), 1981–2026;
* the monthly Shiller CAPE (multpl.com table, 1871–2026);
* Shiller's `ie_data.xls` for 10-year yields and CPI before 1981.

Unemployment is not included: FRED and the BLS API are unreachable from this environment.

**Snapshot:** each year's September values (the latest complete month for 2026).

**Primary set, 1981–2025 (45 candidate years), z-scored across the candidates, equal weights, Euclidean distance. Seven features:**
1. fed funds rate;
2. its 12-month change (cutting vs hiking);
3. CPI year on year;
4. 10-year yield;
5. curve (10y − 3m);
6. CAPE;
7. S&P return from January to September.

**Secondary set, 1900–2025 (long history, no Fed data), five features:**
1. CAPE;
2. 10-year yield;
3. CPI year on year;
4. the 12-month change in the 10-year yield;
5. S&P January-to-September return.

**Reported:**
* the 5 nearest years;
* their September values next to 2026's;
* what the S&P did from day 204 to the end of November, to year end, and over the next 12 months (from the end of October);
* whether each analog was a midterm year. 2026 is a midterm year; this is descriptive, not a feature.

**Skill test (walk-forward, same rules as the shape test):**
* for each test year, the 5 nearest earlier years; prediction = their mean outcome; naive = the mean over all earlier years.
* **Primary:** the next-12-month return, with test years 1991–2025 (at least 10 earlier candidates).
* **Also reported:** the end-of-November outcome, and the secondary feature set with test years 1930–2025.
* **Null:** permutation, 5,000 draws, one-sided.
* **Pass:** correlation > 0 with p < 0.05 and a sign hit rate above naive.

**Prediction (written before the run):**
* The valuation backdrop (CAPE about 40) will pull the analogs toward 1998–2000 and 2021.
* 12-month outcomes after those years were mixed: 1999 up, 2000 and 2021 followed by bear markets.
* The walk-forward has low power (35 test years) and is expected to fail.
