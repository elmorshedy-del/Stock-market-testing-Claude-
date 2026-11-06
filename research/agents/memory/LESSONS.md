# Lessons (append only, newest first)
Each entry: what went wrong → the rule that prevents it. Read this at the start of every session.

## 2026-11-06
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
