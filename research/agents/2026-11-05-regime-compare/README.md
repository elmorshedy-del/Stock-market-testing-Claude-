# Is this a 2022, or an early-2025 / early-2026 scare? Macro, Fed pricing, valuation vs rates, AI earnings revisions

**Agent / session:** Claude, for the owner, 2026-11-05 after the close.
**Type:** descriptive comparison and judgement (owner question). There is no test and no pre-registration.

**Owner:** "Knowing today's macro and fundamentals with rates and credits and inflation and fed sentiment and all and companies multiples, does this look like something that should unfold like 2022 or just like a correction where everything seems scary like in early 2026 or early 2025 and then the AI trade just go back to normal?"

**Files:**
* `regime.py` → `out/regime.json`, `out/regime_compare.png`.
* Inputs are monthly FRED series in `data/` (gitignored, copied from `2026-11-05-channels-deep/data/`), plus the Shiller CAPE from multpl.com, fetched live.
* EPS-estimate revisions come from Alpha Vantage `EARNINGS_ESTIMATES`, pulled 2026-11-05. Only derived % changes are recorded here.

## Side by side (month of each record close)
| | Mar 2000 (bear) | Jan 2022 (bear) | Feb 2025 (scare, −18.9%) | Jan 2026 (scare, −9.1%) | **Oct 2026 (now)** |
|---|---|---|---|---|---|
| Fed funds / change over 12 months | 5.85 / +1.04 | 0.08 / 0.00 | 4.33 / −1.00 | 3.64 / −0.69 | **3.88 / −0.21** (hiked in Sep) |
| 2y − fed funds (> 0 = hikes priced) | +0.68 | +0.90 | −0.12 | −0.10 | **+0.86** (+0.70 on Nov 4) |
| 10y nominal | 6.26 | 1.76 | 4.45 | 4.21 | **5.13** (4.84 on Nov 5) |
| 10y real (TIPS) / change over 6 months | n/a | −0.69 / +0.32 | 2.03 / +0.27 | 1.91 / −0.10 | **2.78 / +0.84** (2.64 on Nov 4) |
| Core CPI y/y / change over 6 months | 2.45 / +0.38 | 6.05 / +1.84 | 3.14 / −0.15 | 2.51 / −0.54 | **2.57 / −0.04** (Sep) |
| Oil y/y | +114% | +60% | −7% | −21% | **+68%** (+53% on Nov 5) |
| Baa − 10y | 2.11 | 1.82 | 1.47 | 1.67 | **1.46** (1.54 on Nov 3) |
| Unemployment − its 12-month low | 0.0 | 0.1 | 0.3 | 0.2 | **0.1** (Sep) |
| Shiller CAPE | 43.2 | 36.9 | 37.2 | 39.7 | **40.6** (38.8 on Nov 5) |
| Earnings yield − TIPS (1/CAPE − real 10y) | ≈ −1.5 (proxy) | **+3.40** | +0.66 | +0.61 | **−0.32** (≈ −0.06 on Nov 4-5) |

* **Valuation against rates:** in October, the earnings yield minus the TIPS yield was the lowest since TIPS data began in 2003. The proxy (10y minus core CPI; +0.05 in Sep 2026) is the lowest since 2000, when it sat below zero.

## AI earnings revisions (consensus EPS, Alpha Vantage, 2026-11-05)
* **Suppliers: still rising, with no cuts this week.**
  * NVDA: FY to Jan-2027 +0.1% over 30 days and +4.0% over 90; FY to Jan-2028 +1.5% and +24.2%. Revisions in 30 days: 7 up, 0 down.
  * AMD: FY2027 +2.1% over 30 days, +14.7% over 90.
  * MU: FY to Aug-2028 +14.8% over 30 days, +27.5% over 90.
  * Over the last 7 days, all three moved between −0.0% and +0.5%.
* **Spenders: flat to down.**
  * META: FY2026 −6.6% over 30 days (6 down, 4 up); FY2027 −0.3%.
  * GOOGL: FY2026 −4.5% over 30 days; FY2027 −0.8%.
  * AMZN: FY2026 −0.6%; FY2027 +0.6%.
  * ORCL: FY to May-2027 0.0% over 30 days; FY to May-2028 +0.4%.
  * GOOGL and AMZN expect lower EPS in FY2027 than in FY2026, which points to one-time items in 2026, so read their changes with care.
* **Debt-funded AI infrastructure:** CRWV's expected 2027 loss widened from about −$3.69 to −$4.68 a share over 90 days.
* **Not retrieved:** AVGO, MSFT and AAPL. The Alpha Vantage key hit its 25-requests-a-day limit. Twelve Data's eps-trend and earnings-calendar endpoints need a higher plan.

## Read
* **The 2022 engine is missing.**
  * 2022 needed core inflation at 6% and rising, and a Fed starting from zero. The real 10y went from −0.69 to +1.59 in nine months and the CAPE fell from 37 to 27.
  * Today core is 2.6% and flat, fed funds is already 3.88, and the real yield is already 2.6-2.8.
  * A 2022-sized jump would take real yields near 5%, which needs an inflation spiral that is not in the data.
  * Credit is calm, jobs are fine, and the AI suppliers' earnings estimates are still going up.
* **This is not a clean early-2025 / early-2026 replay either.** Three things are worse than in those scares:
  1. **Fed pricing has flipped.** The market prices hikes, not cuts, after September's hike. This is the one real 2022 (and 2000) rhyme.
  2. **There is no valuation cushion against rates.** Stocks yield less than TIPS. The scares had +0.6 pp, and Jan 2022 had +3.4.
  3. **The spenders' estimates are being trimmed while the suppliers' still rise.** That is the late-capex-cycle shape of 2000, where suppliers crack last.
* **Judgement.** The most likely path is a scare-type correction (≈75%):
  * early-2026 style, holding about 7,000-7,350: ≈45%;
  * early-2025 style, a 10-20% drop and then back: ≈30%.
* **But the AI trade should come back slower and choppier than in 2025.** With no rate cushion and no Fed put, the rebound needs the 10y to fall (oil and peace is the path) or AI earnings to keep beating.
* **The ≈25% bear tail is mostly the 2000 shape for AI (≈20%), not 2022 (≈5%).**
  * 2000 shape: the spenders' capex cuts lead to cuts in the suppliers' estimates.
  * 2022 shape: oil passes through to inflation and the Fed keeps hiking.
* **What to watch:**
  * the 10y back above 5% and the 2y − fed funds gap widening (the 2022 path);
  * the first estimate cuts at NVDA, AMD or MU, or capex cuts by the spenders (the 2000 path);
  * Baa − 10y above about 1.9 or HY OAS above about 4 (either path);
  * on the other side, oil falling, the 10y under about 4.6, hikes priced out, and VIX back under about 20 with RSP leading (the scare path).
