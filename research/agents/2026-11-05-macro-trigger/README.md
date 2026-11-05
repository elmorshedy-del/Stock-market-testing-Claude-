# Do jobs and CPI days trigger bounces after sharp drops in low gamma?

**Agent / session:** Claude, for the owner, 2026-11-05 ~11:15 ET. **Pre-registered at commit:** the commit that first adds this README.

**Owner:** "Many times job and inflation surge the market especially on these low gamma environment and after sharp drops."

**Why now:** the jobs report is Fri Nov 6 and CPI is Tue Nov 10 (FRED release calendar).

## Data
* **Release dates:** FRED release-dates API (release 50 = Employment Situation, 10 = CPI), 2011–2026.
  * Jobs: the earliest date in each month (later same-month dates are benchmark or revision releases).
  * CPI: the latest date in each month (earlier February dates are seasonal-factor revisions).
* **Prices:** S&P (^GSPC) and NDX daily closes, from Yahoo.
* **Gamma:** SqueezeMetrics GEX, as a trailing 252-session percentile. Usable from about May 2012.

## Conditions, at the prior close (t−1)
* **DROP:** S&P ≥ 3% below its 10-session closing high.
* **LOWG:** GEX percentile ≤ 0.30.
* **SETUP:** DROP and LOWG together (the owner's claim).

## Outcomes
* The S&P close-to-close return on release day t (releases come out at 08:30 ET, before the open).
* Secondary: NDX day-t return; S&P return from t−1 to t+5; |day-t return| (size).

## Tests
* **H1 (primary, SETUP):** release days beat non-release SETUP days on the day-t S&P return.
  * One-sided permutation: shuffle release labels within SETUP days, 10,000 draws.
* **H2 (DROP only)** and **H3 (LOWG only):** the same test.
* **Holm across H1–H3.** Pass: adjusted p < 0.05 **and ≥ 15 release days in the condition**. Otherwise "can't say."
* **Descriptive:**
  * Share up and mean, jobs vs CPI separately.
  * Size: |return| on release vs non-release days.
  * Unconditional release-day returns.
  * The list of SETUP release days.

## Today (descriptive)
* DROP status at the Nov 5 close.
* LOWG status: Nov 5's GEX is not published until tonight, so report Nov 4's value and say so.

## Reproduce
`python trigger.py <DIX.csv>` → `out/trigger.json`. Release dates are saved in `out/release_dates.csv` (public FRED data).

---

# Results (run ~11:30 ET)
Span: 2012-05 → 2026-11-04. 340 release days (169 jobs, 171 CPI).

**H1–H3 all fail (Holm adj 1.0).** The sign is the opposite of the claim.

**H1, SETUP (drop ≥ 3% and GEX ≤ 30th pct):** 33 release days.
* S&P −0.56% on average, 42% up. Non-release SETUP days: +0.21%, 58% up. Permutation p 0.98.
* Jobs days: −1.14%, 3 of 12 up. CPI days: −0.22%, 11 of 21 up.
* NDX: −0.62% vs +0.28%.
* S&P t−1 → t+5: −0.52% vs +0.81%.
* Size: release |r| 1.58% vs 1.41%. Bigger moves, in either direction.
  * Big up days (≥ +1%): 9. Big down days (≤ −1%): 14.

**H2, DROP only:** 36 days, −0.34%, 44% up; jobs days 4 of 14 up (p 0.94).

**H3, LOWG only:** 90 days, −0.19%, 46% up (p 0.96).

**All days, unconditional:** release days +0.075% vs +0.05%, 57% vs 54% up. Normal-sized moves on average (|r| 0.79% vs 0.69%).

**Robustness (exploratory):** without the COVID (Mar 2020) and tariff-crash (Apr 2025) days, SETUP release days are flat.
* −0.08%, 48% up, n 29.
* Jobs days 3 of 10 up; CPI days 11 of 19 up (+0.19%).
* The negative tilt partly comes from shock days, but the claim ("surge") still fails.

**Memorable surges exist but are not the norm:** 2022-10 CPI +2.6%, 2014-12 CPI +2.0%, 2021-03 jobs +1.95%, 2023-03 CPI +1.65%.

**Today (live):**
* DROP is met: S&P −3.4% from its 10-day high.
* LOWG is not met on the last published GEX: Nov 4, 45th pct. Nov 5's value comes tonight.

**Verdict**
* Release days in this setup are a trigger for a *big* move, not a reliably *up* one.
* After drops, jobs days have leaned down (n small). CPI days are close to a coin flip, slightly up without the shock days.

---

# Amendment A1 (pre-registered before running): the test done properly
**Owner's critique (fair):** "U lump data together and do very shallow statistics."

What was wrong with H1–H3:
* They averaged good and bad prints (no surprise measure).
* They used close-to-close returns, mixing the 08:30 reaction with the rest of the day.
* They lumped regimes in which "good" news has opposite signs.
* They cut 340 days down to 33 with arbitrary thresholds.

## Data added
* **Consensus vs actual** from the ForexFactory calendar (via the Firecrawl Alexandria provider):
  * Non-Farm Employment Change, 2010-03 →.
  * Core CPI m/m, 2010-01 →.
  * The raw values stay out of git (`data/`). Only aggregates are committed.
* **SPY daily OHLC** (Yahoo):
  * gap = prior close → open, which holds the 08:30 reaction;
  * follow-through (ft) = open → close.
  * Both are divided by the trailing 20-day stdev of daily returns, so they are in sigma units, not raw %.
* **Surprise z**
  * Payrolls: (actual − forecast) ÷ the median |surprise| of the prior 24 releases, clipped at ±4.
  * Core CPI: (actual − forecast) ÷ 0.1.
* **"Good for stocks"**
  * s = z × the sign of the correlation between surprise and gap over the prior 24 releases of that type. Out of sample, so it is the direction the market has *recently* been rewarding, not one I assume.
* **State at t−1, continuous**
  * LOW = 1 − GEX percentile.
  * DROP = −(drawdown from the 10-day high), in %.
  * VIX_{t−1} as a control.
* **Sample:** all jobs and CPI release days 2012-05 → 2026-10 (FRED dates, matched to the ForexFactory points by date).

## Hypotheses (one primary coefficient each; HC3 robust SEs plus a by-year block bootstrap; one-sided)
* **A (amplification):** low gamma makes the data reaction bigger per unit of surprise.
  * Model: |gap_σ| = α + type + β|z| + γ·LOW + **δ·|z|·LOW** + VIX.
  * Test: δ > 0.
* **B (asymmetric relief):** after a drop, good prints get a bigger rally than bad prints get a selloff.
  * Model: gap_σ = α + type + b1·s⁺ + b2·s⁻ + **b3·s⁺·DROP** + **b4·s⁻·DROP** + b5·DROP + VIX, where s⁺ = max(s, 0) and s⁻ = min(s, 0).
  * Test: b3 − b4 > 0.
  * Secondary: b5 > 0 (a relief gap regardless of the surprise).
* **C (follow-through):** in low gamma the move after the open continues in the gap's direction.
  * Model: ft_σ = α + type + c1·gap_σ + **c2·gap_σ·LOW** + c3·LOW + c4·DROP + VIX.
  * Test: c2 > 0.
  * Control, descriptive: the same model on non-release days, to see whether it is specific to release days.

## Rules
* Holm across A, B and C; pass at adjusted p < 0.05.
* Robustness: jobs and CPI separately; 2012–19 vs 2020–26; binary SETUP instead of continuous; without Mar–Apr 2020 and Apr 2025.

**For Friday, descriptive:** which payrolls surprise direction the market has rewarded over the last 24 releases, and the model's predicted reaction under today's state.

---

# A1 results (run ~12:10 ET)
* 339 release days, 2012-05 → 2026-10: 169 jobs, 170 CPI.
* ForexFactory dates matched the FRED main release dates for 95% of jobs and 94% of CPI releases.

**A, amplification: PASSES (Holm adj 0.047).**
* δ = +0.168 σ of gap per unit |z| per unit LOW (HC3 t 2.15; year-bootstrap p 0.005; 90% CI 0.06–0.29).
* Sensitivity is about 0 in high gamma and about 0.13σ per |z| at GEX near the 10th pct.
* Descriptive: big surprises (|z| > 1.5) gapped 1.01% in low gamma (n 25) vs 0.48% in high gamma (n 41).
* Fragile:
  * Strongest in 2012–19 (p 0.01); 2020–26 p 0.29.
  * Jobs-only p 0.14 and CPI-only p 0.11. Same sign, lower power.
  * The binary version fails (p 0.24).
  * Stronger without the shock days (p 0.002).

**B, asymmetric relief after drops: FAILS (p 0.95).**
* b3 − b4 = −0.06: good prints do not get bigger rallies than bad prints get selloffs after a drawdown.
* Secondary b5 (a relief gap per 1% drawdown, regardless of the surprise): +0.05σ, t 1.1, not significant.

**C, follow-through in low gamma: FAILS (p 0.57).**
* Low gamma does not make the post-open move extend the gap on release days.
* It does not on non-release days either (control: t 0.4).

**For Friday, descriptive:**
* Over the last 24 payrolls, corr(surprise, gap) is +0.06, i.e. no stable "good news" direction.
* The last 6: weak prints gapped up 3/3 (Jul, Aug, Oct 2026). Strong prints gapped down 2/3 (Jun, Sep; May gapped up).
* Core CPI over the last 24: corr −0.13 (hot = down, mildly).
* State: DROP 4.0% at the live close, LOW 0.55 (Nov 4 GEX); Nov 5's GEX is due tonight.

## Erratum to H1–H3 interpretation (the originals above are left unchanged)
* The H1–H3 descriptive "jobs days lean down after drops (3/12 up)" should **not** be used.
* It averaged over surprises and shock days. With the surprise and the state modelled (A1-B), there is no directional tilt on release days after drops, up or down.
* What survives is A: **release days in low gamma move more per unit of surprise.** The direction comes from the surprise, not from the setup.
