# Agent research

This is where AI agents do their own research. They are encouraged to build on the existing work. Treat it like science: methods get questioned, sharpened, replaced or extended, and a careful negative result counts as much as a positive one.

## What you may do

* **Replicate** an existing result with independent code and see whether it holds.
* **Critique** a method: find a leak, a bias, a weak null, or a sample too small for the claim.
* **Improve** a method: a better estimator, a stronger test, cleaner data, a faster engine.
* **Extend** a result to new assets, periods, horizons or data.
* **Ask a new question** the existing work raises but doesn't answer.

You have autonomy over the question, the method and the tools. Pick what you think will move the work forward most, and say why.

## What you must not do

* **Never edit or overwrite the originals:** anything outside your own folder, including `research/microstructure/`, `engines/`, `docs/` and other agents' folders. Read them, import them, copy them into your folder; don't change them.
* Don't change your pass/fail criteria after seeing results. If you must, log the change and the reason.
* Don't commit keys or licensed raw data (see `docs/data-sources.md`).

## How to run a study

1. **Create** `research/agents/<YYYY-MM-DD>-<short-topic>/` and copy [`_template/README.md`](_template/README.md) into it.
2. **Pre-register.** Before any result-producing run, fill in the question, the prior work you build on (file and commit hash), your hypothesis and your pass/fail criteria. Commit that README first; the commit date is your proof.
3. **Do the work in your folder.**
   * Import from `engines/` or the original study by path, or copy code in.
   * Keep data in your folder's `data/` (gitignored).
   * Write outputs to your folder's `out/`.
4. **Report** results with denominators: days, episodes, base rate, lift, p, and the null used. Include what failed.
5. **Give a verdict** against the prior work: **replicates**, **refines**, **contradicts**, **extends** or **inconclusive**, with the evidence.
6. **Add one line** to [`INDEX.md`](INDEX.md).

## When your work challenges the originals

* Write the challenge up in your folder with a command that reproduces it.
* Add it to `INDEX.md` with the verdict *contradicts* or *refines*.
* The owner decides whether the original report, the engine or `docs/conventions.md` gets a dated correction. Agents don't edit them.

## Reviewing other agents

You may review another agent's study by adding `review-<your-date>.md` **in your own folder**. Cover what you reran, what you found, and whether the verdict stands. Link it from `INDEX.md`.
