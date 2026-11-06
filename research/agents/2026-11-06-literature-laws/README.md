# Literature review: the laws of price formation

**Type:** literature review requested by the owner. No test was run. Cost: $0.
**Output:** [FOUNDATION.md](../FOUNDATION.md), the program's theory: 16 laws with mechanism, evidence grade, contested points, our status and the test for each.

## How the search was done
1. **Search.** Targeted searches for each candidate law: impact, flow memory, latent liquidity, invariance and business time, self-excitation and aftershocks, endogenous vs exogenous shocks, liquidity feedback, inelastic markets, forced and hedging flows, levels, trend reversal. Tools: the arXiv and research-paper index (Firecrawl), web search (Exa) for economics journals and SSRN, and the arXiv API.
2. **Verification.** Every paper was checked against Crossref (`crossref_check.py`; `out/crossref1.json`, `out/crossref2.json`) or arXiv (`arxiv_check.py`; `out/arxiv_abs.json`). The Scite citation service was unavailable because it needs a paid plan.
3. **What was read.** Abstracts, or publisher and SSRN summaries, for every paper whose claim is used. Full text was read only for Muhle-Karbe et al. 2026 (see [2026-11-06-paper-unified-flow](../2026-11-06-paper-unified-flow/)).
4. **Quoted numbers.** Every number quoted in FOUNDATION.md comes from an abstract or publisher summary.
5. **Preprints.** Marked as preprints and weighted lower.

## References (grouped by law; DOI or arXiv id)

### F1 impact, F3 memory, F4 liquidity geometry, F6 decay, F7 spread
- Tóth, Lempérière, Deremble, de Lataillade, Kockelkoren, Bouchaud (2011). Anomalous price impact and the critical nature of liquidity in financial markets. Phys. Rev. X. arXiv:1105.1694
- Donier, Bonart, Mastromatteo, Bouchaud (2015). A fully consistent, minimal model for non-linear market impact. Quant. Finance. doi:10.1080/14697688.2015.1040056
- Benzaquen, Bouchaud (2018). Market impact with multi-timescale liquidity. Quant. Finance. doi:10.1080/14697688.2018.1444279
- Sato, Kanazawa (2024). Strict universality of the square-root law in price impact across stocks: a complete survey of the Tokyo stock exchange. arXiv:2411.13965
- Maitrier, Loeper, Kanazawa, Bouchaud (2025). The "double" square-root law: evidence for the mechanical origin of market impact using Tokyo Stock Exchange data. arXiv:2502.16246
- Maitrier, Bouchaud (2025). The subtle interplay between square-root impact, order imbalance & volatility: a unifying framework. arXiv:2506.07711 (part II: Maitrier, Loeper, Bouchaud, arXiv:2509.05065)
- Sato, Kanazawa (2025). Why do financial prices exhibit Brownian motion despite predictable order flow? arXiv:2502.17906 (exact model: Sato, Fujiwara, Kanazawa 2026, arXiv:2608.00988)
- Bonart (2026). Diffusive in plain sight: an inconspicuous law of market impact. arXiv:2606.07059 (preprint)
- Bouchaud, Mastromatteo, Tóth (2026). On Bonart's interpretation of the square-root impact law. arXiv:2610.10053 (preprint)
- Saddier, Marsili (2023). A Bayesian theory of market impact. arXiv:2303.08867
- Zhou, Chen, Wei (2026). Order splitting and liquidity replenishment are jointly necessary for the square-root law of market impact. arXiv:2607.04280 (preprint, agent-based)
- Vasaikar (2026). Empirical confirmation of the square-root law of market impact in a U.S. large-cap equity. arXiv:2606.24019 (preprint, single author)
- Donier, Bonart (2015). A million metaorder analysis of market impact on the Bitcoin. Market Microstructure and Liquidity. doi:10.1142/s2382626615500082
- Bucci, Benzaquen, Lillo, Bouchaud (2019). Crossover from linear to square-root market impact. Phys. Rev. Lett. doi:10.1103/physrevlett.122.108302
- Bucci, Mastromatteo, Benzaquen, Bouchaud (2019). Impact is not just volatility. Quant. Finance. doi:10.1080/14697688.2019.1622768
- Zarinelli, Treccani, Farmer, Lillo (2015). Beyond the square root: evidence for logarithmic dependence of market impact on size and participation rate. arXiv:1412.2152
- Moro, Vicente, Moyano, Gerig, Farmer, Vaglica, Lillo, Mantegna (2009). Market impact and trading profile of hidden orders in stock markets. Phys. Rev. E. doi:10.1103/physreve.80.066102
- Farmer, Gerig, Lillo, Waelbroeck (2013). How efficiency shapes market impact. Quant. Finance. arXiv:1102.5457
- Bucci, Benzaquen, Lillo, Bouchaud (2019). Slow decay of impact in equity markets: insights from the ANcerno database. Market Microstructure and Liquidity. doi:10.1142/s2382626619500060
- Said, Bel Hadj Ayed, Husson, Abergel (2018). Market impact: a systematic study of limit orders. arXiv:1802.08502
- Naviglio, Bormetti, Campigli, Rodikov, Lillo (2025). Why is the estimation of metaorder impact with public market data so challenging? arXiv:2501.17096
- Cont, Kukanov, Stoikov (2014). The price impact of order book events. J. Financial Econometrics. doi:10.1093/jjfinec/nbt003
- Takahashi (2025). Returns and order flow imbalances: intraday dynamics and macroeconomic news effects. arXiv:2508.06788 (preprint)
- Lillo, Mike, Farmer (2005). A theory for long-memory in supply and demand. Phys. Rev. E. arXiv:cond-mat/0412708
- Lillo, Farmer (2004). The long memory of the efficient market. Stud. Nonlinear Dyn. Econom. doi:10.2202/1558-3708.1226
- Bouchaud, Gefen, Potters, Wyart (2004). Fluctuations and response in financial markets: the subtle nature of 'random' price changes. Quant. Finance. doi:10.1080/14697680400000022
- Farmer, Gillemot, Lillo, Mike, Sen (2004). What really causes large price changes? Quant. Finance. doi:10.1080/14697680400008627
- Joulin, Lefevre, Grunberg, Bouchaud (2008). Stock price jumps: news and volume play a minor role. arXiv:0803.1769
- Patzelt, Bouchaud (2018). Universal scaling and nonlinearity of aggregate price impact in financial markets. Phys. Rev. E. doi:10.1103/physreve.97.012304
- Zovko, Farmer (2002). The power of patience: a behavioural regularity in limit-order placement. Quant. Finance. doi:10.1088/1469-7688/2/5/308
- Obizhaeva, Wang (2013). Optimal trading strategy and supply/demand dynamics. J. Financial Markets. doi:10.1016/j.finmar.2012.09.001
- Wyart, Bouchaud, Kockelkoren, Potters, Vettorazzo (2008). Relation between bid-ask spread, impact and volatility in order-driven markets. Quant. Finance. doi:10.1080/14697680701344515
- Farmer, Patelli, Zovko (2005). The predictive power of zero intelligence in financial markets. PNAS. arXiv:cond-mat/0309233
- Hendershott, Menkveld (2014). Price pressures. J. Financial Economics. doi:10.1016/j.jfineco.2014.08.001
- Schmidhuber (2021). Trends, reversion, and critical phenomena in financial markets. Physica A. doi:10.1016/j.physa.2020.125642

### F5 levels
- Osler (2003). Currency orders and exchange rate dynamics: an explanation for the predictive success of technical analysis. J. Finance. doi:10.1111/1540-6261.00588
- Garzarelli, Cristelli, Pompa, Zaccaria, Pietronero (2014). Memory effects in stock price dynamics: evidences of technical trading. Sci. Rep. doi:10.1038/srep04487
- Chung, Bellotti (2021). Evidence and behaviour of support and resistance levels in financial time series. arXiv:2101.07410 (preprint)
- Jung, Lee (2026). Do round numbers hold prices? Occupation densities and depth-conditioned hazards in the limit order book. arXiv:2610.34787 (preprint)

### M1 clock and invariance
- Clark (1973). A subordinated stochastic process model with finite variance for speculative prices. Econometrica. doi:10.2307/1913889
- Ané, Geman (2000). Order flow, transaction clock, and normality of asset returns. J. Finance. doi:10.1111/0022-1082.00286
- Jones, Kaul, Lipson (1994). Transactions, volume, and volatility. Rev. Financial Studies. doi:10.1093/rfs/7.4.631
- Kyle, Obizhaeva (2016). Market microstructure invariance: empirical hypotheses. Econometrica. doi:10.3982/ecta10486
- Andersen, Bondarenko, Kyle, Obizhaeva (2015). Intraday trading invariance in the E-mini S&P 500 futures market. SSRN. doi:10.2139/ssrn.2693810
- Benzaquen, Donier, Bouchaud (2016). Unravelling the trading invariance hypothesis. Market Microstructure and Liquidity. doi:10.1142/s238262661650009x
- Bucci, Lillo, Bouchaud, Benzaquen (2020). Are trading invariants really invariant? Trading costs matter. Quant. Finance. doi:10.1080/14697688.2020.1741667
- Pohl, Ristig, Schachermayer, Tangpi (2020). Theoretical and empirical analysis of trading activity. Math. Programming. doi:10.1007/s10107-018-1341-x
- Aldrich, Heckenbach, Laughlin (2014). The random walk of high frequency trading. arXiv:1408.3650 (preprint)
- Ludescher, Bunde (2014). Universal behavior of the interoccurrence times between losses in financial markets: independence of the time resolution. Phys. Rev. E. doi:10.1103/PhysRevE.90.062809
- Chang, Geman, Hsieh, Hwang (2013). Invariance in the recurrence of large returns and the validation of models of price dynamics. Phys. Rev. E. doi:10.1103/physreve.88.022116
- Filimonov, Sornette (2015). Power law scaling and "Dragon-Kings" in distributions of intraday financial drawdowns. arXiv:1407.5037

### M2 self-excitation, M3 signature, M4 feedback
- Hardiman, Bercot, Bouchaud (2013). Critical reflexivity in financial markets: a Hawkes process analysis. Eur. Phys. J. B. arXiv:1302.1405
- Filimonov, Sornette (2012). Quantifying reflexivity in financial markets: toward a prediction of flash crashes. Phys. Rev. E. arXiv:1201.3572
- Bacry, Mastromatteo, Muzy (2015). Hawkes processes in finance. Market Microstructure and Liquidity. doi:10.1142/s2382626615500057
- Jaisson, Rosenbaum (2015). Limit theorems for nearly unstable Hawkes processes. Ann. Appl. Probab. doi:10.1214/14-aap1005
- Gatheral, Jaisson, Rosenbaum (2018). Volatility is rough. Quant. Finance. doi:10.1080/14697688.2017.1393551
- El Euch, Fukasawa, Rosenbaum (2018). The microstructural foundations of leverage effect and rough volatility. Finance Stoch. doi:10.1007/s00780-018-0360-z
- Muhle-Karbe, Ouazzani Chahdi, Rosenbaum, Szymanski (2026). A unified theory of order flow, market impact, and volatility. arXiv:2601.23172
- Lillo, Mantegna (2003). Power-law relaxation in a complex system: Omori law after a financial market crash. Phys. Rev. E. doi:10.1103/physreve.68.016119
- Petersen, Wang, Havlin, Stanley (2010). Market dynamics immediately before and after financial shocks: quantifying the Omori, productivity, and Bath laws. Phys. Rev. E. doi:10.1103/physreve.82.036114
- Cutler, Poterba, Summers (1989). What moves stock prices? J. Portfolio Management. doi:10.3905/jpm.1989.409212
- Sornette, Malevergne, Muzy (2002). Volatility fingerprints of large shocks: endogeneous versus exogeneous. arXiv:cond-mat/0204626
- Sornette, Helmstetter (2003). Endogeneous versus exogeneous shocks in systems with memory. Physica A. arXiv:cond-mat/0206047
- Saichev, Sornette (2009). Generation-by-generation dissection of the response function in long memory epidemic processes. arXiv:0904.0872
- Marcaccioli, Bouchaud, Benzaquen (2021). Exogenous and endogenous price jumps belong to different dynamical classes. arXiv:2106.07040
- Lambiotte, Ausloos (2005). Endo- vs. exo-genous shocks and relaxation rates in book and music "sales". arXiv:physics/0509107
- Garcia Seuma (2026). Where does the criticality live? Early-warning signals are event-heterogeneous across seven crypto-perpetual liquidation cascades. arXiv:2607.27070 (preprint)
- Fosset, Bouchaud, Benzaquen (2020). Endogenous liquidity crises. arXiv:1912.00359
- Nagel (2012). Evaporating liquidity. Rev. Financial Studies. doi:10.1093/rfs/hhs066
- Brunnermeier, Pedersen (2009). Market liquidity and funding liquidity. Rev. Financial Studies. doi:10.1093/rfs/hhn098
- Bouchaud, Matacz, Potters (2001). Leverage effect in financial markets: the retarded volatility model. Phys. Rev. Lett. doi:10.1103/physrevlett.87.228701
- Zumbach (2009). Time reversal invariance in finance. Quant. Finance. doi:10.1080/14697680802616712
- Wehrli, Sornette (2022). The excess volatility puzzle explained by financial noise amplification from endogenous feedbacks. Sci. Rep. doi:10.1038/s41598-022-20879-0

### S1–S4 sources of flow
- Gabaix, Koijen (2021; rev. 2023). In search of the origins of financial fluctuations: the inelastic markets hypothesis. NBER w28967. doi:10.3386/w28967
- Hartzmark, Solomon (2025). Market-wide predictable price pressure. American Economic Review 115(9). doi:10.1257/aer.20231725 (NBER w30688)
- Bouchaud (2021). The inelastic market hypothesis: a microstructural interpretation. arXiv:2108.00242
- Koijen, Yogo (2019). A demand system approach to asset pricing. J. Political Economy. doi:10.1086/701683
- Coval, Stafford (2007). Asset fire sales (and purchases) in equity markets. J. Financial Economics. doi:10.1016/j.jfineco.2006.09.007
- Ni, Pearson, Poteshman, White (2021). Does option trading have a pervasive impact on underlying stock prices? Rev. Financial Studies 34(4)
- Baltussen, Da, Lammers, Martens (2021). Hedging demand and market intraday momentum. J. Financial Economics. doi:10.1016/j.jfineco.2021.04.029
- Dim, Eraker, Vilkov (2024). 0DTEs: trading, gamma risk and volatility propagation. SSRN 4692190. doi:10.2139/ssrn.4692190
- Adams, Fontaine, Ornthanalai (2024). The market for 0DTE: the role of liquidity providers in volatility attenuation. SSRN 4881008
- Vasquez, Amaya, Pearson, Garcia-Ares (2025). 0DTE index options and market volatility: how large is their impact? SSRN 5113405
- Garcia-Ares, Vasquez, Pearson, Amaya (2026). The price impact of hedging expiring index options. SSRN 7330098
- Anderegg, Ulmann, Sornette (2022). The impact of option hedging on the spot market volatility. J. International Money and Finance 124
- Gabaix, Gopikrishnan, Plerou, Stanley (2003). A theory of power-law distributions in financial market fluctuations. Nature. doi:10.1038/nature01624
- Kyle, Obizhaeva (2023). Large bets and stock market crashes. Review of Finance 27(6). doi:10.1093/rof/rfad008

### Cautions and reviews
- Plerou, Gopikrishnan, Stanley (2003). Two-phase behaviour of financial markets. Nature. doi:10.1038/421130a; Potters, Bouchaud (2003). Comment. arXiv:cond-mat/0304514
- Preis, Schneider, Stanley (2011). Switching processes in financial markets. PNAS. doi:10.1073/pnas.1019484108; Filimonov, Sornette (2011). Spurious trend switching phenomena in financial markets. arXiv:1112.3868
- Bouchaud (2026). Non-equilibrium economics: a physicist's point of view. arXiv:2607.09620
- Book, not verified here: Bouchaud, Bonart, Donier, Gould (2018), *Trades, Quotes and Prices*, Cambridge University Press. It is the standard text that most of the fast-layer laws come from.

## Data note
Nothing licensed was used.
