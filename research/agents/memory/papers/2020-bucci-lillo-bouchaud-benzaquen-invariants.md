# Bucci, Lillo, Bouchaud & Benzaquen (2020). Are trading invariants really invariant? Trading costs matter. Quantitative Finance 20(7). doi:10.1080/14697688.2020.1741667 (arXiv:1902.03457v1)
**Read:** the full arXiv text (13 pages, Appendices A–C), 2026-11-06. Verified: Crossref (literature-laws).
**Laws:** M1 (the 3/2 law at the bet level), S4 (the constant C in the crash law), F7 (spread ∝ volatility per trade).

## Claim
* **At the level of bets (metaorders), the 3/2 law holds:** exchanged risk R ∝ N^(3/2), with N the number of bets per stock-day.
* **But KO's invariant I = R/N^(3/2) is not invariant.** It varies by at least 10× across stocks and tracks the bet's total trading cost (R² ≈ 0.8).
* **Dividing by cost gives a much tighter quantity.** The authors' reading: invariance comes from traders sizing bets to what trading costs, and "has little to do with the Modigliani–Miller theorem".

## Data
* ANcerno, Jan 2007–Jun 2010 (880 days): about 8 million metaorders in Russell 3000 stocks, completed within one day.
* About 5% of total market volume; about 5 metaorders per stock-day on average.
* Daily volatility (high − low)/open; Rogers–Satchell and monthly averages give the same results.
* Spreads come from CFM data.

## Method
* Per stock-day: R = Σ σ_d·v_i·p_i over the day's metaorders. Average R conditional on N; fit the slope.
* **Cost per bet:** C = Y_spd·mean(S·v) + Y_imp·mean(σ_d·v·p·√(v/V_d)), fitted by OLS of I on C.
* New invariants I/C, I/C_spd and I/C_imp, compared by coefficient of variation (CV).

## Results
* **The 3/2 law holds at the bet level** across size, sector and year (2007–10), and stock by stock (slopes cluster at 1.5). Mechanism (Appendix B): E[Rᵢ|N] ∝ N^0.5, with σ_d ∝ N^0.25 and dollar bet size ∝ N^0.20.
* **The level is not universal:**
  * fit Y_spd ≈ 3.5, Y_imp ≈ 1.5, R² ≈ 0.8;
  * impact is about half of the total cost (C_imp/C mean 0.51);
  * spread cost dominates small bets, impact dominates large ones.

  | Invariant | CV | Robust CV (MAD) |
  |---|---|---|
  | KO's I (mean $6.3k) | 1.74 | 1.09 |
  | I/C | 0.84 | 0.57 |
  | I/C_spd | 0.66 | 0.47 |
  | I/C_imp | 1.56 | 0.97 |
* **Why I/C is stable:** three things are about the same in every stock:
  * spread ∝ volatility per trade, S = c·p·σ_d/√N_d;
  * the metaorder size distribution (its normalized 3/2 moment m);
  * the bets' share of volume (η ≈ 5%) and of trade count (ξ).
  
  So I/C = 1/(Y_spd·c·√ξ + Y_imp·m·√η).

## Caveats
* **The authors':** only US equities; futures, bonds and FX untested; country differences could matter.
* **Mine:**
  * same-day metaorders only, so multi-day bets (the kind behind crashes) are excluded;
  * ANcerno is about 5% of volume;
  * N here is ANcerno bets, not all bets;
  * the cost model uses the square-root law, so it already assumes square-root impact.

## What it means for us
* **For the crash law (S4).**
  * KO's single bet cost constant does not hold even across stocks; it is set by each market's trading costs. The relevant C for the whole market is that market's own cost level, which our data can partly measure (spreads and impact in ES/SPY).
  * Combined with Benzaquen 2016 (futures' invariant about 10× that of stocks), this gives test #4 a ±10× uncertainty on C, i.e. about ±2.2× on the predicted fall (C enters as C^(−1/3)).
  * **A second finding against the linear model:** the cost model that makes I/C invariant uses square-root impact.
* **For M1:** the 3/2 law is now shown at the trade level (Benzaquen 2016) and the bet level (here). Business-time scaling is solid; the absolute level is market-specific.
* **For F7:** spread ∝ volatility per trade appears again as the reason the invariants are stable.

## How we would replicate or extend it on our data
* Bet-level data are not available to us. The trade-level version is in the Benzaquen 2016 card.
* For test #4: set the market's cost constant from its spread (SPY/ES spread × typical trade size) and report the range.

## Open questions
* Is there a dimensionless invariant for index futures and ETFs (where Modigliani–Miller is irrelevant)? The authors say trade-level invariance holds there, so the cost mechanism must be the reason.
