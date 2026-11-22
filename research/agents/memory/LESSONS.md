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

## 2026-11-16, later (the owner rejected the step-1 derivation)
* **What happened.** I delivered a "derivation" that was a summary of seven empirical papers, one line of algebra, and predictions about when options are cheap or dear. The owner: "This isn't really the kind of research I want." Asked what missed, they chose "Not from first principles" and "Wrong subject", and not "effects too small" or "too much reading".
* **Why it missed (my reading).**
  * They had said, in the black-body message, that work derived from understanding beats statistics on history. Seven papers of regressions are statistics on history, even when read in full.
  * As "consultant" I had steered the work toward pricing and trade structure. They accepted the map but that subject was mine, not theirs. Their subject is what moves the price.
  → **The product is a model:** postulates, equations, a closed-form result, and predictions sharp enough for one formula to be tested across calm days, selloffs and expiries. A literature summary is never the deliverable; papers supply the postulates and the constants.
  → **A derivation means algebra.** If the page has no equation that could be wrong, it is not a derivation.
  → **Start with an order-of-magnitude estimate from the formula** before any data. It can overturn a belief by arithmetic alone.
  → **When the owner approves a plan with a short "go on" or "do it", that is not agreement with every part of it.** State the subject of the next piece of work in one line before starting, so a mismatch shows up early.
* **Asking worked.** One question with concrete options resolved in one tap what another long page would have guessed at.

## 2026-11-22 (cross-asset study)
* **A pasted article's numbers can be right while its causes are wrong.** Every price figure checked out; the main cause (rising yields) did not fit the timing, because yields fell during the selloff itself.
  → Check the claims one by one against data, separately for the numbers and for the causes, and say which held.
* **Phases change the answer.** Pooled over Sep–Nov the story looked like "yields up, everything down". Split at the yield peak, the two halves have different mechanisms.
  → Look for the turning point of each driver before averaging over a window.
* **Check an instrument on known cases first.** The fingerprint table caught 3 of 4 known episodes and exposed a missing case (Treasuries sold in a funding crisis). I left the miss in the record instead of rewriting the table after seeing it.

## 2026-11-22, later (the discovery system)
* **The owner wants a system, not a sequence of clever ideas.** Three messages in a row pushed from "zoomed in" to "careful statistics" to "a rigorous system like scientists and ML experts use".
  → For any search for relationships, follow DISCOVERY.md: the protocol and the lockbox are committed before results; every candidate counted; chance measured by rerunning the whole search on time-shifted targets.
* **My own claim from the same morning failed careful statistics.** The gold–stock correlation jump was mostly a volatility effect (Forbes–Rigobon).
  → Any correlation compared across calm and stressed windows gets the volatility adjustment and a confidence interval.
* **Walk-forward is not enough on its own.** Slow variables produced walk-forward "skill" up to +0.17 against time-shifted targets.
  → Only skill above the time-shift null's 95th percentile counts.
* **A big flexible model loses to a three-variable one** when the effective sample is small (overlapping weekly targets).
  → Always include a strong simple benchmark; report the model against it.
* **Audit the data before the result.** NFCI looked like the best return predictor, but its history is revised and backcast.
  → Check the vintage and point-in-time status of every macro series before including it.

## 2026-11-22, evening (the owner's sharpest correction)
* **What happened.** I kept launching wide computations (226 variables, decades of data, many targets) without stating why. The owner stopped five runs in a row: "stop this wide scope... without any clear reasoning", "you always go back to a century and you don't know why", "be a scientist".
  → **Before every computation, say in a few lines why this scope, why this period, why these variables, and what result would change the next step.** One small step at a time; the last result chooses the next.
  → **With few events (about 15 corrections), start from cases**: what kind of event each was, and the non-events. Hypotheses come from cases; tests come after, with frozen rules.
  → **Older history is used only to test a specific frozen hypothesis**, with the reason stated. Never to search.
  → **Confirm the target in one line before building.** I built "danger at any time, 1990–2019" when the owner meant "correction onset inside the post-2009 bull, including October 2026".
* **Regimes change the meaning of variables.** 2y − Fed funds and the real Fed funds rate flip sign between the zero-bound era and normal times.
  → Require a relationship to hold in each regime before trusting it; diagnose sign flips by economic meaning.
* **I claimed an extreme without checking the chart** ("+109bp, the highest since 2010"; 2022 was +220bp).
  → Check any "highest since" claim against the full series before saying it.

## 2026-11-22, late (steps 5–6 of the vulnerability study)
* **I accepted "holds in both eras" from an era split chosen for data reasons (the 2-year starts in 1976).** Splitting 1976–2009 showed the effect lived entirely in 1976–89 and was absent in 1990–2009.
  → Before accepting a cross-era claim, look at sub-periods inside each era. A pooled era can hide a regime where the effect is zero.
* **My episode test (a correction within episode + 6 months) had no power:** corrections near highs come every 10–12 months, so random windows score 75–80%.
  → Compute the chance baseline of any hit-rate test before trusting it. When events are frequent, use horizon-specific odds against a matched baseline, not "did something happen in a long window".
* **A helper covered the wrong range:** the peak list started in 1975, so the 1954–76 listing printed "none".
  → When reusing a helper on a new period, check that its inputs cover that period.
* **A frozen two-part hypothesis can half-fail.** Report the frozen verdict ("not supported") first, then what each half showed. Never relabel it as supported.

