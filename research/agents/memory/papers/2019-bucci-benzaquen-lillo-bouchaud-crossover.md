# Bucci, Benzaquen, Lillo & Bouchaud (2019). Crossover from linear to square-root market impact. Phys. Rev. Lett. 122, 108302. doi:10.1103/physrevlett.122.108302 (arXiv:1811.05230)
**Read:** the full arXiv text (5 pages, 2 figures, notes [26]–[29]), 2026-11-06. Verified: Crossref (literature-laws) and the Firecrawl paper index (PMID 30932667).
**Laws:** F1 (square-root impact and its limits), F4 (latent liquidity), S4 (decides whether the crash law can be linear).

## Claim
* Impact of a metaorder is **linear in Q when the participation rate η = Q/V_T is small**, and **square-root (independent of execution time) when η is large**.
* The crossover follows the scaling function of the latent-liquidity (LLOB) theory. It happens at η* ≈ 3×10⁻³, far below the theory's original η* = 1.
* Explanation: two kinds of liquidity. Fast liquidity (e.g. HFT) makes most of the volume but does not resist a metaorder. Slow liquidity is what bends impact into a square root.

## Data
* ANcerno: about 8 million institutional metaorders in US equities, Jan 2007–Jun 2010 (880 days), about 5% of total market volume.
* Each order has a broker, stock, size Q, sign, and start and end time.
* Units: Q in daily volume (φ = Q/V_d); T in volume time; price in units of daily volatility (high–low)/open.

## Method
* LLOB model: ∂ₜφ = D∂ₓₓφ − νφ + λ·sign(y) + m·δ(y). The order book is linear near the price, φ = L·y with L = λ/√(Dν).
* Impact: I(Q) = √(DQ/J)·F(η), with F ≈ √(η/π) for η ≪ 1 and F → √2 for η ≫ 1.
* Test: bin by η, plot E[ε·(p_end − p_start)/√φ | η], and check the shape and crossover against F(η/η*).

## Results
* **The scaling function fits the data.**
  * Linear regime (η < η*): impact ∝ φ·T^(−β) with β = 0.45 ± 0.05 (theory: 1/2). It is linear in size and smaller for slower execution.
  * Square-root regime (η > η*): β = −0.04 ± 0.02, so impact does not depend on execution time.
  * 70% of metaorders are in the square-root regime. The asymptote of F is ≈ 0.4.
* **η* ≈ 3.15×10⁻³ = J_slow/J_total.** Most daily liquidity is "fast". Slow liquidity diffuses about 100× more slowly than price (D_s/D ≈ 10⁻²).
  * η* is about the same in 2007–08 and 2009–10.
  * η* is larger for large-cap, low-volatility stocks.
  * η* ∝ T^(−1/2): it is about 10× larger for short metaorders.
* **The authors' limits:**
  * data with φ ≳ 10⁻¹ (a tenth of daily volume) "are difficult to interpret" (conditioning effects);
  * all square-root evidence in the literature covers η ≈ 10⁻³–10⁻¹, "never in a regime where the volume of the metaorder becomes larger than the rest of the market".

## Caveats
* **The authors':** the two-speed model is a simplification of a continuous spread of trading speeds; the η* ∝ T^(−1/2) result is not what the two-speed model predicts.
* **Mine:**
  * Again no market-wide orders: single-stock metaorders only.
  * Crash bets (η ~ 0.1–1, metaorder comparable to the whole market) are beyond the tested range, as the authors say.

## What it means for us
* **This is the strongest argument against the crash law's linear assumption.**
  * Physics says impact is linear only for **slow** (low-participation) execution, and then it shrinks as 1/√T.
  * Fast, heavy selling is square-root and independent of T.
  * Crash bets are fast and heavy: 1987 sold 67% of daily volume over days; the 2010 flash crash ran at about 29% participation for 20 minutes. So the physics predicts square root at crash scale, i.e. KO's Inv-SQRT, which predicts 1987 at about 1.3% against 32% actual.
* **So the two frameworks give different explanations of crashes:**
  * **KO:** impact is linear and amplified by business time. The crash size follows from the bet size and normal-time constants.
  * **Physics (LLOB):** impact is square root under normal liquidity, which is far too small. The excess must come from the **latent liquidity itself collapsing** (L → small), a state change the normal-time constants cannot see. Donier & Bouchaud (2015) argue this on Bitcoin.
* **This is the test #4 can run.** For each recent selloff, compute the Inv-LIN and Inv-SQRT predictions from the estimated forced selling.
  * If Inv-LIN fits, KO's mechanism is supported.
  * If Inv-SQRT under-predicts, does the shortfall track a measured liquidity collapse (e.g. top-of-book depth or impact per unit of order-flow imbalance before vs during the selloff)? If yes, the physics mechanism is supported.
* **1929 fits LLOB's slow-execution branch** (selling spread over weeks: low η, linear but reduced by 1/√T). KO saw a smaller fall than predicted there.
* **For F1:** the square-root law holds for η ≳ 3×10⁻³ (most real metaorders) and is independent of execution time. That is a cleaner statement than "Y·σ·√(Q/V) always".

## How we would replicate or extend it on our data
* We have no metaorder data. The crossover cannot be replicated without ANcerno-like data or our own executions.
* We can test the market-level analogue: the price response to aggregate order-flow imbalance at different horizons (linear at short horizons, concave at long ones; Patzelt & Bouchaud 2018 card). Needs signed trades (Databento).

## Open questions
* What happens when η → 1 for the whole market (a crash)? Does fast liquidity withdraw, so that impact jumps from the slow-liquidity square root to something steeper?
* Is the slow-liquidity fraction η* lower in 2024–26 (more 0DTE and HFT volume)? If so, more of the volume is "fast" and gives no resistance, and the square-root regime starts at smaller orders.
