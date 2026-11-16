# Lessons (append only, newest first)
Each entry: what went wrong → the rule that prevents it. Read this at the start of every session.

## 2026-11-15 (from the audit)
* **Forecasts were logged and then not scored on time; five studies never reached INDEX.md; the to-do list reached 79 open items against 7 closed.**
  → Score on the due date before any new work. A study is not finished until it has an INDEX row and a playbook line. Cap the backlog.
* **My adjustments to the options-implied odds lost to the unadjusted odds** (0.279 vs 0.256 Brier, 12 forecasts).
  → Quote the market's odds as the default. Deviate only where a proven rule applies, and keep the deviation's own score.
* **Three jobs (live desk, edge hunt, science) ran in one stream,** so each interrupted the others and the goal moved three times.
  → Label every piece of work with its lane. A desk read may add one backlog line; it may not start a test.
* **I took the working memory as the whole record.** The owner pointed out that the thread is much older (it began Oct 2) and that work sits in other repositories.
  → For any audit or summary, start from the full log, the transcript and the commit history by session tag, not from STATE.md.

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

## 2026-11-16 (step 1: reading before the derivation)
* **A hypothesis I wrote into the plan before reading was half wrong.** I put "options are cheapest after expiry because positioning clears" into MAP.md on Nov 15. The papers gave a different cause (writers re-selling) and a sign that flips with who the customers are.
  → Put a hypothesis in a plan only as a question. Write the derivation after the reading, and say plainly what changed.
* **I nearly quoted an effect size I had not derived** ("8% of implied volatility per standard deviation"). The paper gives 1.7 points on average and half a standard deviation per standard deviation.
  → Every number in a derivation is either copied from the card or labelled as my own arithmetic, with the arithmetic shown.
* **The power check changed the plan before any data.** The state question as a ratio test can detect a gap of 0.14–0.21; the literature implies 0.05–0.15. The expiry test is well powered.
  → Do the power check from the papers' effect sizes while deriving, and let it order the tests.
* **Low gamma and "after a selloff" arrive together.** A sort on gamma alone cannot tell positioning from fear.
  → Look for a change in positioning on a known date with no price move (an expiry) before trusting a state sort.
* **Record which version of a paper was read.** Ni et al. was the 2006 draft; Dim–Eraker–Vilkov is now inside Adams et al. 2026.
  → The card's first line states the version; the foundation cites it that way.
