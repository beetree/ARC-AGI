## Negative Results

This section summarizes explored approaches that were ultimately discarded; full details are in the appendix.

**Sequential decomposition** (hint-then-solve, object-then-transform-then-solve) consistently reduced candidate diversity by collapsing the hypothesis space at each handoff stage, counteracting the system's core diversity strategy. **Strict output constraints** (JSON schemas, prescribed reasoning templates) degraded performance on hard tasks through a "compliance tax on reasoning" --- the model allocates reasoning budget to following instructions rather than solving the problem. **Synthetic data augmentation** for code candidates (color permutation, rotation) added little signal because surface-level augmentations do not test new structural properties, and geometric transforms can break task semantics.

The most counterintuitive finding: **the more prescriptive the prompt, the worse the system performed** on the hardest tasks. The final system uses a deliberately minimal prompt (see the appendix) with no prescribed structure, step-by-step template, or domain heuristics. This also interacts with diversity: a prescriptive prompt narrows the hypothesis space across candidates, causing them to converge on the same (possibly wrong) answer. For novel reasoning tasks where the solution is not known in advance, the best prompt is often the least prescriptive one.

