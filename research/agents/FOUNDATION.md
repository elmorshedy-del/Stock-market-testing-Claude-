# Foundation: the laws of price formation we build on

**Started:** 2026-11-06, after a literature review the owner asked for.
**Sources:** about 75 papers, each verified against Crossref or arXiv records. Method and the full reference list are in [2026-11-06-literature-laws](2026-11-06-literature-laws/).
**Purpose:** this is the program's theory. Every future test should measure one of these laws on our instruments, or test one of the owner's ideas as an extension of a law. A pattern search with no law behind it does not belong here.

**How to read each entry:**
* **Law:** what is observed, in one line.
* **Mechanism:** why it happens.
* **Evidence:** how strong it is.
* **Contested:** what is disputed.
* **Us:** what we have measured.
* **Test:** the free or paid test that would measure it.

**Evidence grades:**
* **Established:** replicated across many markets and decades, with a mechanism that predicts it.
* **Supported:** good evidence, but few studies or an open dispute.
* **Open:** plausible, not yet tested well. This is where the owner's own ideas mostly sit.

---

## The theory in one paragraph
Price is a particle pushed by order flow through a medium of liquidity, on a clock that runs at the speed of trading.
* **The push (slow layer).** Investors with mandates (inelastic money), forced sellers and option hedgers create flow. Big decisions arrive as big orders that are split into many small trades over hours to days.
* **The medium (fast layer).** Most liquidity is hidden intention, not posted orders. It is thinnest exactly at the current price and refills over several timescales. That geometry makes a big order move price by the square root of its size. After the order ends, part of the move reverts.
* **The rhythm (medium layer).**
  * Trading excites more trading, close to the tipping point.
  * Shocks leave aftershocks that fade slowly.
  * Liquidity withdraws when volatility rises, which feeds the next move.
  * The market's internal clock runs on activity, not on the calendar.
* **The constraint.** Predictable drift gets traded away. So pushes that can be seen coming are partly priced before they arrive, and transient impact must decay.

Almost every stylized fact we have tested so far sits inside this picture: fat tails, volatility clustering, random-walk prices, aftershocks, failed channels and gamma effects.

---

## Fast layer: how flow moves price (mechanics)

### F1. Impact law: impact grows as the square root of size. *Established.*
* **Law.** A big order of size Q moves price by about Y·σ·√(Q/V), where σ is daily volatility, V is daily volume and Y is about 1. This holds across stocks, futures, FX and Bitcoin.
* **Mechanism.** Hidden (latent) liquidity is V-shaped and vanishes at the current price, so each extra share meets less resistance (Tóth et al. 2011; Donier et al. 2015).
* **Evidence.**
  * Tokyo, every account and every liquid stock over 8 years: the exponent is 1/2 within error, per stock and per trader (Sato & Kanazawa 2024).
  * Single child orders already show a square-root impact once the market has digested them. That impact then decays as one over the square root of time, and reshuffled "fake" big orders show the same law. So impact is mechanical, not informational (Maitrier, Loeper, Kanazawa & Bouchaud 2025).
  * Bitcoin shows the law over four decades of size (Donier & Bonart 2015).
  * Below a crossover size, impact is linear (Bucci et al. 2019).
* **Contested.**
  * Over five decades of size a logarithm fits better (Zarinelli et al. 2015).
  * Why the law holds is debated right now: diffusion of prices (Bonart 2026) versus volume conservation (Bouchaud, Mastromatteo & Tóth 2026). A model ablation finds that order splitting and liquidity refill are jointly necessary (Zhou, Chen & Wei 2026, preprint).
* **Us.** Not measured.
* **Test (paid data).** Rebuild proxy big orders from the anonymous tape, as done for Tokyo (Maitrier et al. 2025) and for one US stock (AAPL, Vasaikar 2026, preprint). Fit Y and the exponent on ES/NQ and the semis.

### F2. Instant law: price change = order-flow imbalance ÷ depth. *Established at short horizons.*
* **Law.** Over seconds to minutes, the mid-price change is linear in the imbalance of queue changes at the best bid and ask, with slope one over depth. This is "F = m·a" for prices, with depth as inertia (Cont, Kukanov & Stoikov 2014, 50 US stocks).
* **Mechanism.** Queues get consumed or refilled; the price moves when a queue empties.
* **Evidence.** The relation to plain trade volume is noisier than the relation to the imbalance. In E-mini futures, impact rises on macro-news days (Takahashi 2025, preprint).
* **Us.** Not measured. We hold one day of TSLA 10-level book data (Oct 28) as a pilot.
* **Test (paid data).** ES/NQ 10-level book for a few key days.

### F3. Memory law: order flow persists, yet price stays random. *Established.*
* **Law.** The signs of trades are correlated over very long lags (power law), but prices still diffuse (Hurst exponent about 1/2).
* **Mechanism.**
  * Big orders are split. If big-order sizes have a power-law tail with exponent α, sign memory decays with exponent α − 1 (Lillo, Mike & Farmer 2005).
  * Liquidity providers lean against the predictable flow. Persistent market orders push prices to trend; mean-reverting limit orders pull them back. The balance sits at a critical point (Bouchaud et al. 2004).
  * With square-root impact the price is provably diffusive (Sato & Kanazawa 2025).
* **Implication.** Volatility can be built entirely from big-order impact, which is the "order-driven" view of excess volatility (Maitrier & Bouchaud 2025).
* **Us.** Not measured.
* **Test (paid data).** Sign memory on ES/NQ and the semis.

### F4. Liquidity geometry: big moves are holes in liquidity, not big orders. *Established in parts.*
* **Laws.**
  * Large price changes come from gaps in the book, not from large orders (Farmer et al. 2004).
  * Most price jumps have no news and no unusual volume; they come from order-flow fluctuations where liquidity is vanishing (Joulin et al. 2008).
  * Placement depth follows volatility (Zovko & Farmer 2002).
* **Owner's "absorption".** Extreme one-sided aggressive flow is not linked to large returns. It happens when the price is pinned at a level. Prices move only when local flow is balanced, and the chance that a trade moves the price falls toward zero as flow becomes one-sided (Patzelt & Bouchaud 2018). That is absorption, measured.
* **Open.** The owner's claim that absorption must complete before price moves on is not tested in what we read.
* **Us.** Not measured.
* **Test (paid data).** Footprint plus book around pinned episodes: does the break come when the passive side is exhausted?

### F5. Levels law: orders cluster at round numbers. *Supported.*
* **Law.**
  * Take-profit orders cluster at round numbers, which explains reversals there. Stop-loss orders cluster just beyond them, which explains fast moves after a level breaks (Osler 2003, actual bank order data).
  * Prices rebound from support and resistance more often than they cross them (Garzarelli et al. 2014). The more prior bounces, the likelier the next, and the effect decays with time (Chung & Bellotti 2021, preprint).
* **Contested.** Round levels attract more resting liquidity, but they do not hold longer once depth is accounted for (Jung & Lee 2026, preprint, five Nasdaq stocks). Levels hold because liquidity sits there: mechanics, not magic.
* **Us.** Earlier level studies were pattern tests, not mechanism tests.
* **Test (paid data).** Depth-adjusted break hazard at round numbers and prior extremes on ES/NQ.

### F6. Decay law: after the push ends, part of the move reverts. *Established on averages.*
* **Law.**
  * At the end of the day, the impact of a finished big order is about 2/3 of its peak. It keeps decaying, as a power law at first, and settles near 1/2 of the end-of-day value after about 50 days (Bucci et al. 2019, 8 million institutional orders).
  * Fair-pricing theory predicts the 2/3 (Farmer, Gerig, Lillo & Waelbroeck 2013), and it has been confirmed elsewhere (Said et al. 2018; Moro et al. 2009: 0.5–0.7).
  * Intermediary price pressure averages 49 bp with a half-life of 0.92 days: 17 bp and 0.54 days for the largest stocks, 118 bp and 2.11 days for the smallest (Hendershott & Menkveld 2014).
  * Trends revert once they reach a critical level of statistical significance, universally across asset classes and horizons (Schmidhuber 2021).
* **Owner's "exhaustion".** Selling stops when the big order ends, then part of the move reverts. That is the average law. Seeing the end in real time from anonymous data is the open problem: public-data estimates of big-order impact are biased (Naviglio et al. 2025).
* **Us.** Exhaustion test A4 failed twice: no exhaustion signature on flip days.
* **Test.** Paid trades data: reversion after reconstructed big-order ends. Free: Schmidhuber-style critical-trend reversal on our indices.

### F7. Spread law: volatility per trade ∝ spread. *Established.*
* **Law.** Volatility per trade is proportional to the bid-ask spread, with R² above 0.9 across stocks. Most volatility comes from trade impact (Wyart et al. 2008).
* **Related.** A "zero-intelligence" order model predicts 96% of the cross-stock variance of spreads and 76% of the variance of price diffusion, with one free parameter. Its dimensionless variables collapse different stocks onto one curve (Farmer, Patelli & Zovko 2005).
* **Us.** Not measured.
* **Test (paid data).** Cheap with trades and quotes data.

---

## Medium layer: energy and rhythm

### M1. Clock law: markets run on business time. *Established.*
* **Law.**
  * Returns look Gaussian when time is counted in trades or volume, not hours (Clark 1973; Ané & Geman 2000). In E-mini futures this holds at fine scales once news events are controlled for (Aldrich et al. 2014, preprint).
  * The number of trades, not their size, drives volatility (Jones, Kaul & Lipson 1994).
* **Invariance (Kyle & Obizhaeva 2016).** The number of bets per day is proportional to trading activity W = price × volume × volatility, raised to the power 2/3. The 3/2 law W ∝ N^(3/2) holds in E-mini (Andersen et al. 2015), across 12 futures and 300 US stocks at many scales (Benzaquen, Donier & Bouchaud 2016), and in large institutional order data (Bucci et al. 2020). It is forced by dimensional analysis (Pohl et al. 2020).
* **Same at every timeframe.**
  * Waiting times between large losses have the same distribution from 1-minute to daily data, once scaled by the mean (Ludescher & Bunde 2014).
  * Waiting times between large returns are invariant across years, stocks and scales (Chang et al. 2013).
  * The biggest drawdowns are the fastest; drawdown size goes with speed, not duration (Filimonov & Sornette 2015, preprint).
* **Owner's "volatility signature sets speed and pause length".** In business time, a COVID leg and a slow grind may be the same move run at different clock speeds. This is open and testable for free.
* **Us.** The volatility first-passage model was calibrated but thin. Pause odds were measured in sessions, which is calendar time.
* **Test (free).** Measure legs and pauses on a volume clock and check whether they collapse across regimes.

### M2. Self-excitation law: activity begets activity, near the tipping point. *Established; size contested.*
* **Law.**
  * Mid-price changes in E-mini behave like a self-exciting process whose kernel integrates to about 1 (critical) in every year 1998–2011 (Hardiman, Bercot & Bouchaud 2013).
  * Another estimate has the self-made share rising from 30% (1998) to over 70% (2007+) (Filimonov & Sornette 2012). The two estimates disagree on the level and the trend.
  * Aftershocks follow Omori decay, bigger shocks have more aftershocks, and the largest aftershock has a typical relative size (Petersen et al. 2010: 219 shocks, 531 stocks, 1-minute data; Lillo & Mantegna 2003).
  * Volatility is rough, with H ≈ 0.1 (Gatheral, Jaisson & Rosenbaum 2018). Nearly unstable self-exciting order flow produces both roughness and the leverage effect (Jaisson & Rosenbaum 2015; El Euch, Fukasawa & Rosenbaum 2018; Muhle-Karbe et al. 2026).
  * Big moves often have no news (Cutler, Poterba & Summers 1989; Joulin et al. 2008).
* **Us.** The branching ratio is 0.87 / 0.95 / 0.90 on daily big days (S&P / NDX / SOX). Power-law memory wins for NDX and SOX but not the S&P. The Omori exponent was not supported on the S&P.
* **Test (free).** ETAS (size-dependent triggering), as already planned.

### M3. Signature law: the shape of the build-up tells how the shock will fade. *Supported.*
* **Law.** Shocks from outside (news) hit abruptly and fade faster. Self-made shocks build up with accelerating volatility and fade more slowly.
  * The theory derives this from long-memory response (Sornette & Helmstetter 2003; Saichev & Sornette 2009).
  * It was shown on market events: 1987 self-made versus 9/11 from outside (Sornette, Malevergne & Muzy 2002).
  * It was confirmed on 300 stocks with a news database. Individual events can be classified by their volatility profile alone, without news (Marcaccioli, Bouchaud & Benzaquen 2021).
* **Contested.** In book and music sales, self-made shocks relaxed faster and exponential fits did as well as power laws (Lambiotte & Ausloos 2005).
* **Owner's link.** This is the owner's "each move has its own signature that controls how long the quiet lasts", in the physics literature, with a measured direction.
* **Us.** Not measured. It explains a gap we left: 28 of our 54 down shocks had a new leg and 26 did not, and we never asked which kind of shock each was.
* **Test (free, proposed first).** Classify our past shocks as self-made or news-driven from data before the shock only. Then check relaxation speed and new-leg odds after each.

### M4. Feedback law: liquidity runs from volatility, and down is not the mirror of up. *Established.*
* **Law.**
  * Liquidity falls after volatility and trends. That feedback makes a phase transition to liquidity crises possible (Fosset, Bouchaud & Benzaquen 2020).
  * The returns earned by liquidity providers are predicted by the VIX and spike in turmoil (Nagel 2012).
  * Margin and funding spirals amplify falls (Brunnermeier & Pedersen 2009).
* **Asymmetry.**
  * Falls raise future volatility more than rises. The effect is moderate for stocks and decays over about 50 days; for indices it is stronger and faster, a panic effect (Bouchaud, Matacz & Potters 2001).
  * Past trends predict future volatility but not the reverse: time has a direction (Zumbach 2009).
  * The owner's "up and down are symmetric" holds for the mechanics of impact, but not for the volatility response in indices.
* **Us.** Consistent with earlier findings: the THIN gamma phase had larger ranges, and low gamma gave a bigger reaction per unit of news surprise.

---

## Slow layer: sources of the push (cause)

### S1. Inelastic-market law: money in moves prices a lot. *Established, recent.*
* **Law.**
  * $1 into equities raises market value by about $5, because mandated institutions barely respond to price (Gabaix & Koijen 2021/2023).
  * Even fully predictable flows move prices. On top-quintile days for dividend-reinvestment buying, market returns are four times those of the lowest quintile; the market-level multiplier is about 1.9 (Hartzmark & Solomon 2025, AER).
  * Latent-liquidity theory predicts the multiplier is of order 1, rising with volatility and falling with turnover (Bouchaud 2021).
* **Us.** Not measured.

### S2. Forced-flow law: forced trades push prices, then they come back. *Established.*
* **Fund flows.** Flow-driven mutual-fund selling creates price pressure that reverses over the following months. It is predictable enough to front-run (Coval & Stafford 2007).
* **Dealer hedging.**
  * Option hedging changes stock volatility and the odds of large moves (Ni, Pearson, Poteshman & White 2021).
  * Short gamma creates intraday momentum into the last 30 minutes, 1974–2020, everywhere (Baltussen, Da, Lammers & Martens 2021).
  * Dealers' net gamma is positive on average and lowers future intraday volatility. Positive gamma strengthens reversals; negative gamma, momentum (Dim, Eraker & Vilkov 2024).
  * 0DTE trading lowers index volatility by 60–90 bp annualized (Adams, Fontaine & Ornthanalai 2024).
  * The gamma effect is modest: at most +3.3 volatility points daily and +6.4 on 30-minute windows (Vasquez, Amaya, Pearson & Garcia-Ares 2025).
* **The close.** Unwinding the hedges of expiring cash-settled index options moves the last 30 minutes: about 6 bp per one standard deviation of dealers' 3:30 pm delta (Garcia-Ares, Vasquez, Pearson & Amaya 2026).
* **FX.** The same gamma-to-volatility link appears in FX (Anderegg, Ulmann & Sornette 2022).
* **Us.**
  * Leveraged-ETF close flows showed no last-30-minute effect (H-FF1/2/3 failed).
  * I explained that as "predictable flow is priced early". S1 and the expiry-unwind paper contradict that explanation, so the null more likely reflects how we measured: estimated flows, possibly executed earlier by dealers, against very deep closing liquidity. Correction logged in PROGRAM.md.
* **Test (paid data).** Closing-auction imbalances (already quoted at about $19.70) give the flow directly instead of an estimate.

### S3. Size law: big investors make fat tails. *Classic, partly contested.*
* **Law.** The fat tails of returns and volume are derived from the size distribution of large investors (Zipf's law) combined with square-root impact (Gabaix, Gopikrishnan, Plerou & Stanley 2003).
* **Contested.** The Tokyo survey rejects this model's impact-exponent prediction (Sato & Kanazawa 2024).
* **Us.** Not measured.

### S4. Crash law: crash size = imbalance measured in business time. *Supported.*
* **Law.** Measuring sell imbalances in market-specific business time explains the size of the 1987 crash and of the 2008 Société Générale liquidation. Too-rapid selling made 1987 and 2010 worse than predicted; slower selling made 1929 milder (Kyle & Obizhaeva 2023).
* **Us.** Not measured. With M1 and S2 this could estimate how much forced selling a decline still needs.

---

## The constraint

### C1. Efficiency constraint: no free lunch at the scale anyone can trade. *Established.*
* **Law.** Predictable drift gets arbitraged away, so transient impact must decay and the exponents are linked (Bouchaud et al. 2004; Donier et al. 2015; Muhle-Karbe et al. 2026).
* **Us.** Our channel and random-walk tests agree: drawn channels did not beat sign-randomized random walks, and channel position predicted nothing.

---

## Claims that did not survive (cautions for our own work)
* **"Two-phase" markets:** the result follows from how the data were conditioned (Plerou et al. 2003; reply by Potters & Bouchaud 2003).
* **Scale-free laws at trend switches:** produced by how peaks were selected, even in random walks (Preis et al. 2011; critique by Filimonov & Sornette 2011). Any study of what happens before tops or bottoms needs the same selection applied to surrogates. Our sign-randomized nulls already do this.
* **Big-order impact from public data:** biased toward linear paths with little reversion (Naviglio et al. 2025).
* **Power-law versus exponential relaxation:** hard to tell apart on short samples (Lambiotte & Ausloos 2005). Pre-register both.
* **Self-organized criticality for crises:** "no smoking gun" yet, in the field's own review (Bouchaud 2026).

## The owner's ideas, mapped

| Owner's idea | Law | Status | Test |
|---|---|---|---|
| Price is motion through levels of liquidity | F1, F2, F4, F5 | Established as physics | Paid: impact, imbalance÷depth, levels |
| Absorption must complete before the move continues | F4 | Pinning is measured; the "must complete" part is open | Paid: pinned episodes, footprint plus book |
| Selling exhausts at bottoms and tops | F6, S2, S4 | Average reversion is established; seeing the end live is open | Paid: reconstructed big-order ends; free: critical-trend reversal |
| Volatility signature sets speed | M1 | Business time is established | Free: volume-clock legs |
| Volatility signature sets pause length | M3, M2 | Supported in the literature, open for us | **Free, first:** self-made vs news shocks |
| Up and down are symmetric | F1 vs M4 | Mechanics yes; volatility response no, for indices | Within the M3 test |
| Options give the signature in advance | S2 | Gamma sign sets reversal vs momentum, modestly; expiry unwinds move the close | Paid or partly free: dealer delta at 3:30 |
