# Reading notes: the baobach/hft_papers list

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-02 (intraday)
**Type:** literature review (reading notes). No data tested, so nothing here is a result. The ideas at the bottom are candidates to pre-register.
**Owner's ask:** "https://github.com/baobach/hft_papers I want u read all of this … anything that seems interesting for any kind of trades, or understanding underlying mechanisms."

## What the repo is

* It is **a list, not a library.** `download_papers/papers.csv` holds 2,302 rows (title, authors, an optional one-line highlight, link and date), dated 2019-2026. It contains no PDFs.
* **Source:** a monthly GitHub Action scrapes PaperDigest's "recent papers on algorithmic trading / high-frequency trading" page (`main/crawler.py`).
* **Mix**, by keyword buckets over titles and highlights; the buckets overlap:
  * about 735 ML, deep-RL, LLM and agent trading-bot papers;
  * 183 crypto;
  * 149 energy and power trading (P2P, batteries, intraday power);
  * 84 technical-indicator papers;
  * 69 pairs trading and stat-arb;
  * many event studies in low-tier journals.
* **Few top-journal market-microstructure papers.** The classics we already use (Ni-Pearson-Poteshman 2005 pinning, Baltussen et al. 2021 gamma momentum, Cont-Kukanov-Stoikov OFI, Kyle 1985) are not in it.
* **Data quality:** at least one entry is mislinked. "Retail Trading and Stock Volatility: The Case of Robinhood" resolves to a language-teaching portfolio.

## How it was read

1. **All 2,302 titles** were screened. Topic buckets covered:
   * options, gamma and volatility;
   * order flow, the order book and price impact;
   * dark trading and short selling;
   * crashes and forced selling;
   * politics and prediction markets;
   * intraday patterns.

   The ~530 titles left in no bucket were read by eye.
2. **87 papers shortlisted** for any trade or mechanism relevance.
3. **About 65 abstracts read.** They came from Semantic Scholar, OpenAlex, arXiv and the publisher pages, with 6 found via search. Elsevier abstracts were often unavailable through the APIs.
4. **Full texts were not read.** Everything below is at abstract level.

## The useful ones, ranked by relevance to how we trade

### A. Mechanisms behind our gamma, flow and forced-selling rules (top journals)

| # | Paper | What it finds | What it means for us |
|---|---|---|---|
| A1 | Ni, Pearson, Poteshman & White, *Does option trading have a pervasive impact on underlying stock prices?* (RFS, ~97 cites) | Option market makers' hedge rebalancing changes stock volatility and the probability of large moves through a non-informational channel. | It is the foundation for our freed, long-gamma-damps and short-gamma-amplifies rules (REPORT §4). Our results agree with it. Cite it in the playbook. |
| A2 | Bogousslavsky, Collin-Dufresne & Sağlam, *Slow-moving capital and execution costs: Knight Capital glitch* (JFE 2021) | A pure supply shock with no news moved prices about ±4%. Half reverted within about an hour of the news, and all of it by the close, with an overshoot around 15:00. Spreads normalised within a day, but institutional execution costs stayed high for more than a week. | It is the model for forced selling (our LQ question). Non-fundamental shocks revert, but over hours to days, and liquidity can look normal on spreads while big-order costs stay high. That is how our "thin book" read and the "liquidation" read can both be true. |
| A3 | Hu, Kirilova, Park & Ryu, *Who profits from trading options?* (Management Science 2023) | About 66-70% of retail option traders hold simple one-sided positions, and they lose to the rest of the market. Selling volatility is the best style for retail and institutions alike. | It supports our structure rule (ladder R4 → a 60-day ATM/+5% call spread, not naked calls). Buying premium after an IV spike is the losing side. |
| A4 | Bergsma, Fodor, Singal & Tayal, *Option trading after the opening bell and intraday stock return predictability* (Financial Management 2020) | Signed option-to-stock volume in the **first 30 minutes** predicts the stock's return over the rest of the day. The effect is stronger after overnight earnings and for higher-volatility stocks. | It is directly testable on TSLA, our flow-driven name, and on earnings reaction days. It needs signed option trades (ThetaData Options Standard, which is blocked). → idea HP2. |
| A5 | *How common is insider trading? Evidence from the options market* (SSRN 2022) | The S&P 500 put-call ratio's alpha (0.24% a week) **vanished** after the 2009 insider-trading crackdown. | Option-flow edges can die when their information source dries up. It fits our informed-flow nulls; don't trust old option-flow alphas without a recent out-of-sample test. |
| A6 | Wang & Zhang, *Informed options trading and stock price crash risk* (JFR 2026) | A higher option-to-stock volume ratio goes with **lower** future crash risk, because information gets into prices early instead of being hoarded. | A cross-sectional lean. It doesn't change a rule. |
| A7 | *Retail margin trading* (Journal of Finance 2026, China account data) | Levered retail investors sell as they approach margin calls. The selling moves prices and spills from lottery-like stocks to other stocks. | It is a mechanism for concentrated forced selling in high-beta AI names that spills into neighbours. It fits the LQ footprint. US margin data are monthly only (FINRA), so we can't test it daily. |
| A8 | *Do retail traders destabilize financial markets?* (JBF 2022) | Marketable retail trades, identified with the subpenny method of Boehmer-Jones-Zhang-Zhang (BJZZ), raise volatility for about 15 days, about 30% more in crises. | Retail flow could be measured for TSLA from trade prints. → idea HP6. |
| A9 | *The Chinese warrants bubble* (RFS 2020) | A precipitating event plus feedback trading on investors' own past returns explains bubble prices. | It is a mechanism for TSLA "named moves" and bursts: a catalyst followed by a feedback loop. It supports our burst work and adds no new rule. |

### B. Market-structure facts that change how to read our signals

| # | Paper | What it finds | What it means for us |
|---|---|---|---|
| B1 | *Breaking VIX at open* (JBF 2021) | On average VIX **rises overnight and falls during trading hours.** The overnight rise is larger over weekends and holidays, and there are patterns around scheduled macro releases. | A Monday-morning VIX pop is partly mechanical, not fear. Keep the R6/R7 rungs on **closes**, as we do. After election night, expect VIX up at Wednesday's open, then resolution intraday. → idea HP4. |
| B2 | *Social media, HFT and after-hours market making: presidential tweets* (JFR 2026) | Liquidity breaks down within fractions of a second after market-moving news. It is **much worse in extended hours**, when designated market makers are optional. | Election results land after hours. Treat pre-market prints, including Yahoo pre-market, as noisy, and wait for the open. |
| B3 | *Crashing in the dark? Dark trading and crash risk* (JBFA 2025) and *Dark pool trading and information acquisition* (RFS 2021) | More dark trading goes with more information acquisition, **and** with higher crash risk. In crash weeks, dark volume and trade size jump, more so in institution-heavy stocks with bad news. | **A caution for DIX/DPI:** heavy dark-venue activity during a selloff can be institutions exiting, not only "dark-pool buying." Check the DIX before treating R5 (weak S&P with DIX > 45.4%) as bullish in crash weeks. |
| B4 | *Buy-sell imbalances around round numbers and HFT* (SSRN 2019) | Non-HFT aggressors show buy pressure **just below** round numbers and sell pressure **just above**. HFTs trade the reverse and earn on it. | It is the mechanism for our round-number stall rule (TSLA 400, 420). → idea HP5, testable with Databento trades. |
| B5 | *HFT in stocks and the costs of option market making* (SSRN 2024) | HFT liquidity demand raises option market makers' hedging costs: through the hedging channel for ATM options, and through stale-price arbitrage for ITM. | When stock depth is thin, dealers' hedges are costlier. That links our "SPY = liquidity" rule to how strongly gamma hedging shows up. A lean only. |
| B6 | *Market impact decay and capacity* (2021) and *Learning about latent dynamic trading demand* (arXiv 2021) | Impact decays slowly. Liquidity providers infer a large hidden parent order from its child orders and **front-run** it. | It explains why forced selling shows multi-day drift (the July sequence: −6.95, −6.30, −5.56, then +12.6 relief once the block printed). |
| B7 | *Spectral volume models* (Management Science 2025) | Algorithms with fixed schedules create universal high-frequency periodicities in intraday volume, which help VWAP execution. | Execution timing only. No signal for us. |

### C. Practitioner strategies worth a skeptical replication

| # | Paper | Claim | Our take |
|---|---|---|---|
| C1 | Zarattini & Aziz, *Can day trading really be profitable?* (SSRN 2023, practitioner) | An opening-range breakout (ORB) on QQQ in 2016-2023 earned **33% annual alpha** after commissions; 1,484% using TQQQ. | Not peer-reviewed, and the claim is huge. A breakout strategy should work when dealers amplify (below the flip, or freed) and fail when they damp (long gamma, near a call wall). We have the 1-minute data and the gamma regimes. → idea HP1, the most interesting one here. |
| C2 | *VIX-timed cross-sectional strategy* (2021, 29 cites) | Hold sentiment-prone stocks when VIX is low, and sentiment-immune stocks when it is high. | It fits the R6/R7 logic of rotating into high beta (TSLA) once VIX falls to the rung. A lean. |
| C3 | *Aggregate congressional trading predicts market returns* (2021, 2004-10 data) | Aggregated congressional stock trades predict monthly market returns. | Possible with the Alpha Vantage CONGRESS_TRADES endpoint. Low priority, and the sample is old. |
| C4 | *Smart money on Polymarket* (arXiv 2026) | Wallet-level profitability persistence on Polymarket. | Off scope for SPY and TSLA, but relevant to how we read election odds. |
| C5 | Intraday momentum: Taiwan ETFs (JBEF 2021), KOSPI (2022), China last hour (2021) | Early-session returns predict the last half hour, driven by late-informed institutions. | **We already tested this for the US: dead in 2023-26** (forced-flow A2; intraday-hours B1). Nothing new. |

### Skipped (with reasons)
* **ML, RL and LLM trading bots (~735):** mostly backtests with no or fixed costs. One paper in the list (*Realistic market impact modeling for RL*) shows that adding Almgren-Chriss costs reorders which algorithm "wins."
* **Crypto, energy and power, P2P:** out of scope.
* **Low-tier event studies** (stock splits, local elections, volume-return): no transferable mechanism.
* **Theory papers** (Kyle extensions, AMM loss-versus-rebalancing, broker-informed-trader games): no direct trade use.

## Candidate studies (not run; each needs pre-registration before any data)

| ID | Idea | Data | Prediction to register |
|---|---|---|---|
| **HP1** | ORB replication on SPY, QQQ and TSLA, **conditioned on gamma regime** (below or above the flip, freed, near a wall) | 1-minute bars plus our daily gamma maps (in hand); out-of-sample 2024-26; realistic costs | ORB profit is concentrated in short-gamma or freed days and is about zero or negative in long-gamma or pinned days. |
| **HP2** | First-30-minute signed option flow → TSLA return from 10:00 to the close; separately on earnings reaction days | ThetaData Options Standard trades (blocked) | Positive slope, stronger after overnight news (Bergsma et al.). |
| **HP3** | Do non-news forced shocks revert? AI-basket extreme-spread days split into news days (earnings, filings) and no-news days | Daily data in hand (LQ) plus an earnings calendar | No-news extreme days revert over 1-5 sessions; news days don't (Knight-glitch logic). |
| **HP4** | VIX split into overnight and intraday by weekday; R6/R7 rung hits measured on the open vs the close; the post-event Wednesday pattern | Yahoo VIX OHLC (free) | Positive overnight drift and negative intraday drift, larger after weekends. Rungs defined on the close are cleaner. |
| **HP5** | Aggressor imbalance in TSLA within ±$0.50 of round $10 levels; does it predict stalls? | Databento trades (small cost; ask first) | Buy pressure just below and sell pressure just above, and stalls more likely when the imbalance is large. |
| **HP6** | BJZZ retail-flow measure for TSLA, and its effect on 1-15 day volatility | Databento or TAQ trade prints | Retail-flow shocks raise TSLA volatility, more in stress. |

## Sources
* Repo: https://github.com/baobach/hft_papers (list file `download_papers/papers.csv`, scraped from PaperDigest).
* Abstract sources: Semantic Scholar API, OpenAlex, the arXiv API, and publisher, SSRN and RePEc pages.
* Key links:
  * [Ni et al. RFS](https://doi.org/10.1093/rfs/hhaa091)
  * [Bogousslavsky et al. JFE](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2613667)
  * [Hu et al. Management Science](https://pubsonline.informs.org/doi/10.1287/mnsc.2023.4916)
  * [Bergsma et al. Financial Management](https://ideas.repec.org/a/bla/finmgt/v49y2020i3p769-804.html)
  * [Zarattini & Aziz SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622)
  * [Baig et al. JBF](https://pmc.ncbi.nlm.nih.gov/articles/PMC9355410/)
  * [Intraday TS momentum JBEF](https://ideas.repec.org/a/eee/beexfi/v31y2021ics2214635021001015.html)
