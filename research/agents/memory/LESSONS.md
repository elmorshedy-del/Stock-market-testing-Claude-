# Lessons (append only, newest first)
Each entry: what went wrong → the rule that prevents it. Read this at the start of every session.

## 2026-11-06
* **Proxy failure caught by a pre-registered cross-check.** ^GSPC share volume × index level is not a dollar-volume series across decades: it was 8× too low in 1987 against Kyle–Obizhaeva's documented $10.2bn.
  → For any constructed series that enters a law, pre-register a cross-check against an independent documented value, and a fallback.
* **A main hypothesis can be guaranteed by its own definitions.** HB1 (the square-root law needs impossible selling) follows from the shock threshold. I said so in the pre-registration, and the informative hypothesis became HB2.
  → Before pre-registering, ask whether the definitions already force the answer. If they do, label it as a baseline, not as evidence.
* **I read the literature through the owner's questions:** M3 because of the signature idea, F4 because of absorption. I ignored the field's own central claims and open questions.
  → The literature sets the agenda: measure the field's core laws on our market and look for where they fail. The owner's questions are food for thought, to be re-posed as sub-questions of the laws. I lead the brainstorm and propose the order.
* **The owner rated the M3 signature test low-value.** It mostly confirmed volatility clustering, which traders already know. The part that could have been useful (second legs) failed.
  → Before running a test, ask: is the answer unknown to a trader, and would it change a trade? Volatility-only tests rarely pass. Edge in direction must come from flow mechanics (who is forced to trade, where liquidity sits), not from price-history signatures.
* **Multiverse joint p.** I permuted each specification independently, so the joint p came out under 0.001; coupled permutations gave 0.08.
  → Couple permutations across specifications: one random rank per event, shared by every specification. Otherwise the joint p is too optimistic.
* **A pre-registered drop rule can bias one class.** All 13 shocks dropped for E1 ≤ 0 were abrupt shocks.
  → Always report which group a drop rule removes, and run a sensitivity check that keeps them.
* **Built a law map from abstracts only.** The owner asked why I hadn't read the papers.
  → Read the full text before building on a paper; abstracts hide scope limits. Example: Marcaccioli et al. 2021 removed market-wide events, which are exactly the index shocks we want to test.
* **Explained the forced-flows null without checking the literature.** I said "predictable flow is priced early"; Hartzmark & Solomon 2025 contradicts it.
  → Before explaining a null with theory, search for contrary evidence.
* **Called a paper internally inconsistent (H0 0.65 vs 0.75–0.80) from its text.** The figure file showed it was a typo.
  → Check figures and data before calling anything a contradiction.
* **Described a paper's sample wrongly** ("no tech names", "no stress episodes") without reading its stock table and dates.
  → Verify sample claims against the paper's tables.
* **Asserted "quiet for 1–2 weeks means the shock is fading" without data.** The owner's experience said otherwise, and the pause data agreed with the owner.
  → Don't assert dynamics without measuring them. Treat the owner's experience as a hypothesis to test.
* **Jumped from test to test.** The owner asked for coherence.
  → Every test must map to a law in FOUNDATION.md and a step in PROGRAM.md.

## 2026-11-05 and earlier (from the session summary)
* **Pre-registration drift.** I ran the P3 zigzag instead of the pre-registered record-close rule, and counted an open event as complete.
  → Re-read the pre-registration before running. Use a complete-window rule.
* **Bad data.**
  * Yahoo SOXX daily closes were about 3x too high on Nov 2–4, which created a fake −70.7% day.
  * Yahoo intraday volume is unreliable.
  * Direct FRED downloads fail.
  * A CAPE parse read an HTML entity as numbers.
  → Cross-check daily closes against intraday last prints, assert value ranges, and flag volume quality.
* **Several of my predictions failed** (T2 sign, A1, H-FF1, the Omori exponent).
  → Report failures plainly; they are results.
* **Owner rules (standing):**
  * Answer first, then evidence, then a figure.
  * ADHD-friendly, plain words.
  * Keys never go in files.
  * Licensed data stays out of git.
  * No model names in commits.
