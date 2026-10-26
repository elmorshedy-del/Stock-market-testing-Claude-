# Do TSLA gaps that open in a different "state" fill less often?

* **Owner, 2026-10-26:** "tsla opened with a gap up. Usually gaps happen about critical levels where the stock opens in a different 'state'. I'm not sure if it will fill the gap or it's going on from here."
* **Today:** TSLA closed Fri Oct 23 at $372.22, opened Mon Oct 26 at $383.98 (**+3.2% gap**) and closed $391.62 (+5.2%).

## Test (pre-registered before computing)
* **Data:**
  * TSLA daily OHLC from Yahoo, 2020-01 to 2026-10-23;
  * TSLA's dealer-gamma flip from `research/microstructure/out/td_gamma_TSLA.csv` (2020 to 2026-10-09), using the flip known at the prior close;
  * the 50-day average from the closes.
* **Events:** up-gaps of at least 2% (open ÷ prior close − 1 ≥ 0.02). Also reported for ≥ 3%.
* **Outcomes:**
  * **filled same day:** the day's low ≤ the prior close;
  * **filled within 5 sessions:** any low over the next 5 sessions ≤ the prior close;
  * the close-to-close return from the gap day's open over 5 sessions.
* **States:**

  | State | Definition |
  |---|---|
  | S1, flip crossing (primary) | the prior close was below the flip and the open is above it ("opens in a different gamma state"), vs every other up-gap |
  | S2, breakaway | the open is above the prior day's high, vs inside the prior day's range |
  | S3, trend | the prior close was above vs below the 50-day average |

* **Prediction (owner's hypothesis):** S1 and S2 gaps fill **less** often than the other gaps.
* **Statistic:** the difference in 5-session fill rate. Bootstrap by event, two-sided p. Descriptive with 95% intervals, because events are few.
* **Today's gap is placed in its cell.**
