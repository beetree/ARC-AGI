## Method: Modality-Driven Search and Architecture

### Core idea: independent candidates across modalities maximize diversity

The solver is built around a practical observation: to solve tasks that frontier systems and labs *do not already solve*, the correct solution is often a **minority hypothesis**. If "the most common solution" were correct, the task would likely already be within the main cluster of model behavior.

Therefore, the solver's first phase intentionally creates many *independent* candidate solutions across heterogeneous reasoning modalities (text, image, and code), maximizing the probability that at least one candidate captures a genuinely novel hypothesis. Each modality provides a structurally different representation of the same task, which empirically produces candidates that cluster differently (Section 6.5).

### Pipeline overview

Figure 2 shows the end-to-end pipeline. For each ARC task:

![Solver pipeline: candidate generation with adaptive early stopping, holistic judging, and weighted scoring.](figures/pipeline.png)

1. **Candidate generation (up to 29 candidates).**
   Run a set of modality-specific solvers, each producing:
   - a single predicted output grid,
   - a reasoning trace,
   - for codegen-with-tools candidates: the code, tool calls, and tool outputs (execution logs).

   Each candidate produces one output; the pass@2 two-guess format is introduced at the judging stage (step 2). Candidate generation proceeds in stages: if early-stage candidates already show strong agreement (multiple candidates converging on the same output), the system terminates early and skips the remaining, more expensive modalities. This adaptive early stopping improves cost efficiency on tasks that can be solved with a shallower search. On ARC-AGI-1 (which contains easier tasks that more frequently trigger early stopping), the same system achieves 94.5% on the official semi-private evaluation at only $11.40/task — substantially cheaper than the $38.99/task on ARC-AGI-2, where harder tasks require the full candidate budget more often. Both semi-private scores and costs are as reported by ARC Prize's verification infrastructure.^[The semi-private evaluation is run by ARC Prize on non-public tasks; the author does not control that environment. Because the semi-private logs are not available for inspection, the detailed analysis in this paper (Sections 6--8) is based on the public evaluation run, where full data is available.]

2. **Holistic judging (3 parallel judges).**  
   Concatenate all candidate traces into a single long-context prompt and ask a judge model to:
   - identify the top-2 most likely correct candidates (or propose a synthesis),
   - explain why other clusters are wrong,
   - output the final grids.

3. **Weighted scoring.**
   Each judge's first choice receives 2 points and second choice receives 1 point. The two distinct output grids with the highest total score become the solver's pass@2 guesses.

### Development methodology

The solver was developed over several months during the fall of 2025, with the author iterating on the approach, architecture, and candidate strategies as new frontier models became available. The core architectural ideas — modality-driven search, independent candidate generation, and holistic trace-based judging — were developed and tested against earlier model versions before the final system was assembled with GPT-5.2 and Gemini 3 Preview in December 2025.

The codebase was built with AI-assisted development tools, and the design process was supported by frontier AI models to explore architectural alternatives, evaluate trade-offs between candidate diversity strategies, and iterate on judge prompt design.

This development pattern — using AI assistance for both design and implementation, with the author directing strategy and evaluating results — proved effective for building a complex, multi-component pipeline within a solo-researcher setting.

### Why candidate diversity matters specifically on ARC-AGI-2

ARC-AGI-2 tasks often introduce new concepts. A solution can be perfectly "logical" on the training pairs but still be a brittle overfit that fails to abstract the intended rule. This makes naive "logic checking" of traces insufficient (details in Section 5 and Section 8). In practice, the system needs:

- broad hypothesis exploration across structurally different representations, and
- a judge that can identify **where** a candidate is likely overfitting—even when it reads as coherent.

---

