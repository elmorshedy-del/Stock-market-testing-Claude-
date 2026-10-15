# What predicts a full swing to the other side of a multi-year log channel? (NVDA 2018 and 2022)

**Agent / session:** Claude (Opus 5.5), claude.ai session for the owner, 2026-10-15
**Started:** 2026-10-15   **Pre-registered at commit:** see `git log --follow README.md` (first commit adding this file)
**Type:** new question (extends `research/microstructure` §1–4 from daily channels to multi-year monthly channels)
**Verdict:** *(filled in at the end)*

## Question

NVDA's monthly log chart (2016→2026) sits in a rising channel. Twice (Oct 2018 → Dec 2018, Nov 2021 → Oct 2022) it
swung from the top of the channel to the bottom. The owner asks:

1. **Premise:** is "top of the channel → lower line" more common than a random walk with the stock's own drift and
   volatility would produce?
2. **Under the hood:** did liquidity, rates, the dollar, leverage, credit, market gamma or the company's inventory
   cycle mark the tops that swung to the lower line, as opposed to tops that didn't?
3. **The tail:** what preceded upside breakouts above the channel (the 1998–2000 dot-com pattern)?
4. **Today:** where NVDA sits now on all of the above.

Universe: 44 large US-listed tech, semiconductor and internet stocks plus ^NDX, ^IXIC, ^SOX, ^GSPC
(`fetch_data.py`, list frozen before any outcome was computed; 45 listed, JNPR has no Yahoo history after its
acquisition), monthly bars from the 1970s–2010s to Oct 2026.

## Prior work

* `research/microstructure/REPORT.md` §1–4b @ 2c6250c: on **daily** channels (126/252 bars) line touches are "mostly not
  magic" (rejection rates inside the block-bootstrap null's CI); breakout odds are partly predictable (AUC 0.62).
  This study asks the same kind of question at the **monthly, multi-year** scale and with **macro** predictors.
* Channel fit: `fit_channel` copied verbatim from `research/microstructure/channels.py` @ 2c6250c into `channel_fit.py`.
* Rules followed: `docs/conventions.md` @ 2c6250c (timing, circular-shift null, episodes, multiverse, frozen criteria,
  trailing-percentile states).

## Disclosure before running

Before writing this file the agent had seen: data coverage per series (`out/data_coverage.csv`), spot values of the
macro table at 8 dates, and NVDA's inventory-vs-revenue growth for 2017–2022 (used to check SEC filing dates). No channel
position, outcome or variable-outcome relation had been computed. From general knowledge the agent also expects that
both NVDA tops coincided with Fed tightening and an inventory glut; that expectation is the hypothesis being tested.

## Definitions (primary specification)

* **Bars:** calendar months; high/low from daily bars, close = last close. The current month (Oct 2026) is partial and is
  used only to score "today".
* **Channel at month t:** `fit_channel` on the trailing **W = 84** monthly log highs/lows/closes ending at t, envelope
  quantile **q = 0.05**. Valid if slope > 0 and R² (log close on the line) ≥ **0.80**. Fit uses bars ≤ t only.
* **Channel position z_t:** −1 = lower line, 0 = middle, +1 = upper line, at the month-t close.
* **Top state:** valid channel and z_t ≥ **0.5**.
* **Reversion (outcome):** within **H = 24** months after t, a monthly low reaches the lower line of the channel
  **frozen at t** and extrapolated forward. Outcome window starts at t+1.
* **Breakout (outcome):** within H months, a monthly close at z ≥ 1.5 on the frozen channel (half a band-width above the
  upper line).
* **Censoring:** months whose window runs past the last complete month (Sep 2026) are dropped unless the event already
  happened.

## Variables (all values as known at the month-t close; publication lags in `build_panel.py`)

Each is signed so that **high = the theorised bearish / tightening reading**. Its **signal is "on"** when the value is in
the top third of its own trailing 120 months (at least 36 months of history; `docs/conventions.md` rule 9 at monthly
scale).

| Family | Name | Definition | From |
|---|---|---|---|
| primary | `FF_HIKE` | 12-month change in the fed funds rate | 1981 |
| primary | `Y10_UP` | 6-month change in the 10-year Treasury yield | 1981 |
| primary | `CURVE_FLAT` | −(10y − 3m yield) | 1982 |
| primary | `USD_UP` | 6-month log change in the dollar index | 1981 |
| primary | `M2_SLOW` | −(M2 year-on-year growth) | 1981 |
| primary | `MKT_EXT` | ^NDX's own channel position z (same method, used whether or not the index channel passes R²) | 1993 |
| primary | `MARGIN_FROTH` | FINRA margin debt year-on-year growth | 1999 |
| primary | `COMPOSITE` | at least half of the seven primary signals above that have data are on | 1981 |
| secondary | `LIQ_DRAIN` | −(6-month log change in Fed net liquidity: assets − TGA − reverse repo) | 2003 |
| secondary | `TIPS_UP` | 6-month change in the 10-year TIPS real yield | 2003 |
| secondary | `CREDIT_WIDEN` | −(6-month return of HYG minus IEF) | 2008 |
| secondary | `GEX_LOW` | −(S&P dealer gamma, SqueezeMetrics, month mean) | 2011 |
| secondary | `INV_GLUT` | inventory YoY growth − trailing-12-month revenue YoY growth (SEC, known at filing date; companies with inventory) | 2010 |

Options positioning for single stocks (ThetaData, 2020+) covers one NVDA top only, so it is **not** tested here; it is
shown descriptively for the Nov 2021 top.

## Tests and frozen pass/fail criteria

**A. Premise (reversion rate vs random walk).** Statistic: P(reversion | top state), pooled over stock-months.
Null: 20 stationary block-bootstrap paths per stock (mean block 6 months, the stock's own monthly log returns), run
through the identical pipeline. **Pass ("the channel pulls price back") if the real rate exceeds the null's mean by ≥ 5
points AND exceeds the null's 95th percentile.** Otherwise: the swing to the lower line is what volatility alone does.

**B. Variables (reversion).** Statistic per variable: Δ = P(reversion | top, signal on) − P(reversion | top, signal off).
Null: circular time shift of the signal series within its own available window, shift drawn as a fraction of the window
in [0.1, 0.9], the **same fraction for every variable** in a draw (keeps cross-correlation; stock-specific `INV_GLUT`
shifts each stock by the same fraction); 1,000 draws. One-sided p. Joint p per family: maximum of the standardised Δ
across the family vs the same maximum in each null draw.
**A variable passes only if all three hold:**
1. Δ > 0 with shift p < 0.05;
2. its family's joint p < 0.05;
3. Δ > 0 in both halves of its sample (primary: before / from 2010; secondary: before / from 2018).

**Multiverse (free choices):** W ∈ {60, 84, 120} × top z ∈ {0.33, 0.5, 0.67} × H ∈ {12, 24} × signal cut {top third,
above median} = 36 specifications. For each variable, the statistic is the median Δ across specifications, with the
same shift null. A variable that passes B but has multiverse p ≥ 0.05 is reported as **fragile**, not as a pass.

**Episodes.** An episode is a run of consecutive top-state months for one stock; it "reverted" if the run's last month
has a reversion outcome. Reported: number of episodes, reverting episodes, and the number of distinct calendar
**waves** (reversion episodes whose run ends fall within the same 12 months count as one wave). Macro variables
cannot have more independent tests than there are waves; that number is stated next to every macro result.

**C. Breakouts (dot-com tail).** Same statistic and null with the breakout outcome and the signals flipped to the easing
side (`FF_CUT` = −`FF_HIKE`, etc.). Pre-declared as **descriptive**: if fewer than 4 distinct breakout waves exist, no
pass/fail is claimed, only the conditional rates and the 1998–2000 readings next to today's.

**D. NVDA and today.** Descriptive: NVDA's ex-ante channel, z, and each signal at the 2018 and 2021 tops and now; the
historical reversion and breakout rates for today's combination, with Wilson 95% intervals and episode counts.

**What would prove the hypothesis wrong:** A fails (reversion is just volatility) and no variable passes B. Then the
honest answer is that the two NVDA swings were not forecastable from these variables with the data available.

## Method notes

* Leak checks before results are trusted: (1) z_t is unchanged when all bars after t are scrambled; (2) every signal at t
  is unchanged when data after t's publication date are deleted; (3) outcomes start at t+1.
* Survivorship: Yahoo has no delisted tickers (no Sun, Lucent, Nortel, JDSU…), so dot-com collapses are
  under-represented; reversion rates are biased **down**.
* Monthly lows are daily lows, so an intramonth wick counts as a touch.

## Results

*(after the run)*

## Threats to validity

*(after the run)*

## Verdict

*(after the run)*

## Reproduce

```bash
python fetch_data.py          # downloads to data/ (gitignored), ~2 min
python build_panel.py         # monthly prices, macro table with publication lags, SEC inventory gap
```
