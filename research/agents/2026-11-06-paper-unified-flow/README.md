# Literature review: "A unified theory of order flow, market impact, and volatility" (arXiv:2601.23172)

**Type:** literature review requested by the owner. No test was run. Cost: $0.
**Paper:** Muhle-Karbe, Ouazzani Chahdi, Rosenbaum, Szymanski (2026), preprint, v2.

## What was read
* **Read:** the main text (Sections 1–5) and Appendix C (data and stock list).
* **Not read:** the reference list and the proof appendices (A and B).
* **Figures:** Figures 3, 4 and 5 were checked from their vector files at `https://arxiv.org/html/2601.23172v2/{fbm_final, mfbm_final, unsigned_volume_hurst}.svg`. Plotted values were read with `extract_fig_values.py`, which maps gridlines to axis ticks. The values are in `out/fig_values.json`.

## Key numbers (from the paper's figures)
* **Fig. 4, mixed-fractional H0, 25 bin sizes (10 s to 80 min):**
  * The average runs 0.741–0.785, with a mean of 0.762.
  * The cross-stock 5% edge runs 0.56–0.69 and the 95% edge 0.84–0.93.
  * A normal approximation to that band puts about 43% of stock-level estimates below 3/4 (26–54% depending on bin size).
  * The average sits about 1 standard error above 3/4 (median z = 1.2, assuming independent stocks).
* **Fig. 3, naive fBM estimate:** 0.514 at 10 s, 0.657 at 1 h, 0.666 at 80 min. This is the source of the "0.65" in the text of Section 3.3.
* **Fig. 5, volume roughness (5–12 s bins):** the mean runs 0.239–0.293, which implies H0 = 0.739–0.793. That is consistent with Fig. 4.

## Review and how it fits the program
The review is in [PROGRAM.md](../PROGRAM.md), section "Literature read", together with its same-day correction.

## Figure
`out/paper_review_h0_edge.png`
* **Panel A:** the paper's claim, with three laws set by H0. The price side exists only for H0 above 3/4.
* **Panel B:** the paper's own H0 estimates against that threshold.
