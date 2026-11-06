# Marcaccioli, Bouchaud & Benzaquen (2021). Exogenous and endogenous price jumps belong to different dynamical classes. arXiv:2106.07040v1
**Read:** the full text, including Appendices A–D, on 2026-11-06. **Verified:** arXiv. **Laws:** M3 (signature), M2 (self-excitation), F4 (liquidity before jumps).

## Claim
Price jumps that follow news ("exogenous") and jumps that come from nowhere ("endogenous", self-made) have different volatility shapes:
* **News jumps:** abrupt, then a faster decay.
* **Self-made jumps:** volatility builds up first, then decays more slowly.

You can tell the two apart from the shape alone, without the news feed, with moderate accuracy.

## Data
* **Stocks:** 300 US stocks, called "NYSE" in the paper, although the list includes Nasdaq names such as AAPL, MSFT, NVDA, TSLA and AMD.
* **Period:** 2015-01-01 to 2020-01-01.
* **Order book:** best 2 levels each side, sampled every minute, regular hours only. Kept days with at least 300 one-minute price changes.
* **News:** Bloomberg articles whose title names the ticker or company.

## Method (enough to replicate)
1. **Jump score.** 1-minute mid-price log return divided by local volatility and an intraday-seasonality factor.
   * Local volatility is the bipower variation over K = 390 minutes: σ² = (π/2K) Σ|r_{t−i}||r_{t−i+1}|.
   * The seasonality factor uses a robust two-step estimate.
   * A jump is a score above 4.36 in absolute value (Lee–Mykland/Gumbel threshold, α = 0.01, K = 390).
   * Jumps in the first and last 15 minutes are dropped.
2. **Clusters, not single jumps.** Jump inter-times follow a power law (exponent 0.88), so jumps cluster. Consecutive jumps are merged when the gap is improbable under a Bernoulli null (ε = 0.05). Gaps between clusters are then exponential (rate 0.11), i.e. the clusters are close to independent.
3. **Labels.**
   * News-driven: the cluster starts between 1 minute before and 4 minutes after a news cluster.
   * Self-made: all other clusters, minus those starting inside a news cluster.
   * **Market-wide or sector-wide events are removed:** any cluster overlapping clusters in more than 30 stocks (10%). Results are robust to 15 or 60, or to a shuffle-based null.
   * Clusters within 100 minutes of each other are excluded.
4. **Average profiles** around the first jump: jump score, a 16-minute moving average of past volatility, past trend (signed and binarized), and order-book sparsity at the best 2 levels.
5. **Shape fit.** A double power law in |t − t_c| on each side of the shock, plus a baseline. Fit by non-linear least squares, with a Shapiro–Wilk check of the residuals.
6. **Classifying single events.** Features: the fitted pre-shock exponent p_l, the post-shock exponent p_r, and the asymmetry A (area before vs after). Logit and probit models, an 80/20 out-of-sample split repeated 1,000 times, and a k-nearest-neighbours check.

## Results
* **Counts.** 258,671 jumps (0.70 per stock per day), 197,197 clusters, and 106,680 after the filters. **Only 1,073 (1%) were news-related**: almost all jumps are self-made.
* **Shape of news clusters.** They have more jumps, and the biggest jump tends to come first.
* **Build-up before self-made jumps.**
  * Volatility and trends build up; the rise is significant from about **75 minutes before** the first jump.
  * The book thins slightly about 15 minutes before.
  * News jumps show no build-up.
* **After the jump.**
  * Self-made jumps relax more slowly.
  * News jumps relax faster and **undershoot** the baseline: two hours later, volatility is lower than two hours before. Uncertainty has been resolved.
* **Exponents.**

  | | Before (p_l) | After (p_r) |
  |---|---|---|
  | Self-made | 0.36 ± 0.02 | 0.40 ± 0.02 |
  | News | 0.08 ± 0.01 | 0.68 ± 0.01 |

  An earlier study (Joulin et al. 2008) found about 0.5 and about 1.
* **Theory match.** Near-critical self-exciting activity with a power-law memory kernel 1/τ^(1+θ) predicts:
  * news decay with exponent 1 − θ;
  * self-made with exponent 1 − 2θ, symmetric on both sides.

  θ = 0.3 matches both, and is the same θ found for YouTube views and Amazon book sales.
* **Classifying single events.**
  * Out-of-sample AUC 0.72 ± 0.03.
  * An alternative fitting procedure gives AUC 0.82 in-sample.
  * k-nearest-neighbours agreement score (adjusted Rand index) about 0.15: overlapping but distinguishable classes.

## Caveats
* **Theirs.**
  * Self-made jumps are not perfectly symmetric (more volume after than before); the authors suggest trend feedback, or news missing from the feed.
  * Being near-critical is questioned elsewhere (Wehrli et al. 2021).
* **Mine.**
  * **Market-wide shocks were removed.** Index-level shocks, the ones we care about, are untested here. Our test would be an extension, not a replication.
  * Minute-scale and single stocks, 2015–2019, before COVID. Whether this holds on daily index data is unknown; the authors ask for other timescales.
  * The news labels are coarse (titles only, about 1% news); some "self-made" jumps are surely unlabelled news.
  * AUC 0.72 is moderate: good for averages, weak for single calls.
  * Only power laws were fitted. Exponential decay was not compared (see Lambiotte & Ausloos 2005).
  * The Figure 1 caption swaps the two labels (it calls exogenous shocks symmetric with a slow build-up). The text and the fits are consistent with each other; the caption is wrong.

## What it means for us
* This is the measured version of the owner's idea that each move's signature sets how long the quiet lasts:
  * a build-up before the shock means a self-made shock and slower relaxation;
  * an abrupt shock means news, a fast fade and then calm.
* **It gives quantitative targets** for M3: relaxation exponents of about 0.4 (self-made) and 0.7 (news), and θ ≈ 0.3.
* **It also bears on F4:** the book thins slightly before self-made jumps, which is the liquidity landscape giving way.

## How we would replicate or extend it on our data
1. **Daily index version (free).**
   * Label each of our 54 down shocks: news-driven if it falls on a scheduled macro release (FOMC, CPI, jobs; the FRED release dates from the macro-trigger study) or a known event day; otherwise self-made.
   * Fit p_l, p_r and the asymmetry A to the daily |return| profile within ±40 sessions.
   * Pre-register the predictions: p_r(self-made) < p_r(news); a slower return to baseline for self-made shocks; and a higher new-leg rate for self-made shocks.
   * Compare power-law and exponential fits.
2. **Intraday version (data we hold).**
   * Run their exact jump detector on the SPY, QQQ and TSLA 1-minute bars, 2020–26.
   * Label with the macro calendar, and keep market-wide events, since index products are market-wide by nature.
3. **Classifier without labels.** Train on the labelled shocks, then classify the current Nov 2026 shock from its own profile.

## Open questions
* Do the exponents carry over from minutes on single stocks to days on indices, as a law should?
* Is "new leg after the pause" more likely for self-made shocks? The paper does not measure follow-on legs.
