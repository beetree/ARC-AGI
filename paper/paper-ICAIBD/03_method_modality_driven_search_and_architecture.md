## Method

The solver is built around a practical observation: to solve tasks that frontier systems do not already solve, the correct solution is often a **minority hypothesis**. If the most common solution were correct, the task would likely already be within the main cluster of model behavior. The solver's first phase therefore creates many *independent* candidate solutions across heterogeneous reasoning modalities (text, image, and code), maximizing the probability that at least one candidate captures a genuinely novel hypothesis. Each modality provides a structurally different representation of the same task, which empirically produces candidates that cluster differently (Section IV-E).

### Pipeline Overview

Fig. 2 shows the end-to-end pipeline. For each ARC task:

![System pipeline overview.](figures/pipeline.png)

1. **Candidate generation (up to 29 candidates).** A set of modality-specific solvers is run, each producing a predicted output grid, a reasoning trace, and, for code candidates, the code plus tool-use logs. Each candidate produces one output; the pass@2 two-guess format is introduced only at the judging stage. Candidate generation proceeds in stages: if early candidates already show strong agreement, the system terminates early and skips the remaining, more expensive modalities. This adaptive early stopping improves cost efficiency on tasks that can be solved with a shallower search. On the ARC-AGI-2 public evaluation, 37 of 167 instances stopped after the initial 8-candidate probe, and **36 of those 37 were solved correctly** (97.3%), showing that shallow search is often sufficient on easier tasks. The same principle is even more effective on easier ARC-AGI-1 tasks, where the system achieves 94.5% on the official semi-private evaluation at only $11.40/task, substantially cheaper than the $38.99/task on ARC-AGI-2. Both semi-private scores and costs are as reported by ARC Prize's verification infrastructure. The single early-stopping failure (`dbff022c:1`) is a case of extreme groupthink: all models confidently assume the simpler of two valid legend-to-color interpretations while the ground truth requires the more complex one. This validates the heuristic on easy tasks, but also shows that early consensus can mask genuine ambiguity.

2. **Holistic judging (3 parallel judges).** All candidate traces are concatenated into a single long-context prompt. Each judge model is asked to identify the top-2 most likely correct candidates (or propose a synthesis that recombines correct subcomponents), explain why other candidate clusters are wrong, and output the final grids.

3. **Weighted scoring.** Each judge's first choice receives 2 points and second choice receives 1 point. The system sums points across judges for each distinct output grid. The two grids with the highest total score become the solver's pass@2 guesses.

ARC-AGI-2 tasks often introduce new concepts that were not exercised in the training pairs. A solution can be perfectly "logical" on the training examples but still be a brittle overfit that fails to abstract the intended rule. This makes naive logic checking of traces insufficient (Sections III-C and VI). In practice, the system needs broad hypothesis exploration across structurally different representations, combined with a judge that can identify **where** a candidate is likely overfitting — even when its reasoning reads as coherent.

---
