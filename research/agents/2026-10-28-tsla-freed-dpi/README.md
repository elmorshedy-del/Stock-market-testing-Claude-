# Why TSLA becomes "deeply freed" after Oct 30, and TSLA's own dark-pool index (descriptive live read)

* **Owner, 2026-10-28:** "Why does TSLA become 'deeply' freed, and how is its DIX?"
* **Data:**
  * ThetaData OI dated Oct 27 (positions at the Oct 26 close; aggregates only), priced at Tuesday's close 407.46;
  * the engine's TSLA history (2021 – Oct 14 2026);
  * FINRA daily short-sale volume files (free).
* **Reproduce:** `python freed_dpi.py <live27/td> <live28/finra> <ladder28>` → `out/freed_dpi.json`.
* No new test. Part (b) is a post hoc descriptive split.

## (a) The mechanism: "freed" is a ratio, and this week's expiries hold most of the numerator
* Freed = the share of all open interest (expiries ≤ 120 days) sitting within ±5% of the price in expiries ≤ 45 days, ranked against the past year.
* **55%** of TSLA's near-price contracts (153k of 280k) expire **Oct 28 or Oct 30**. Those two expiries are only **16%** of all open interest.
* When they expire, the numerator roughly halves and the denominator barely moves. The share goes 0.087 → 0.047, from the 16th to the 0.4th percentile.
* Biggest near-price strikes (total / expiring by Friday):
  * 400: 59.6k / 24.2k;
  * 420: 41.9k / 23.1k;
  * 395: 32.2k / 19.6k;
  * 390: 29.9k / 16.7k.
* **Why it matters:** less open interest at the current price means less dealer hedging tied to that price. Fewer "springs" hold price in place, so moves can run. The engine's tested result (REPORT §4t/§4z): freed → 1.8× up-burst odds within 3 sessions, no extra down-bursts, with vol, IV and gamma controlled.
* **Caveat:** this assumes nobody opens new contracts near the price. History says they do, fast. Of 59 deep-freed episodes (≤ 5th pctile), the median time back above the 33rd pctile was **4 sessions** (IQR 2–8.5).

## (b) Freed depth vs what followed (post hoc, descriptive; bursts = ±5% in a day or ±9% in two, next 3 sessions)
| State | Days | Up-burst | Down-burst | 10d median |
|---|---|---|---|---|
| deeply freed (≤ 5th), above own flip | 20 | 50% | 20% | +3.6% |
| deeply freed, below own flip | 51 | 57% | 49% | +3.2% |
| freed (5th–33rd), above flip | 216 | 27% | 19% | +0.5% |
| freed, below flip | 123 | 37% | 46% | −0.8% |
| not freed, above flip | 838 | 17% | 17% | −0.3% |
| not freed, below flip | 203 | 17% | 19% | +1.9% |

* Deeper freed → bigger moves. Above the flip they lean up.
* The deep-freed rows are small, a few episodes each. Lean, not proof.

## (c) TSLA's own "DIX": FINRA dark-pool index (short share of off-exchange volume; high = off-exchange buying)
* **Daily readings:**
  * Oct 12–14: 0.395–0.410, the 2nd pctile of the 5-day measure on Oct 14.
  * Since Oct 20: 0.48–0.60.
  * Oct 26: 0.468; Oct 27: 0.487 (22M shares).
  * One-year range 0.356–0.680, median 0.483.
* **5-day mean 0.532 = the 75th pctile of the trailing year,** up from the 15th on Oct 20.
* **What it has meant before** (REPORT §4r, §4ae):
  * Top-tercile TSLA DPI: +5.6% over 20 days vs +2.5% (bottom tercile); 60% vs 49% up-burst odds within 10 days. Borderline (p 0.19 / 0.07).
  * Bottom-tenth DPI adds down-bursts (p 0.049). That warning state is **off**.
* **S&P DIX** (SqueezeMetrics) Oct 27: 0.455, the 54th pctile. Neutral.
