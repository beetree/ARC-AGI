## Method

### Core idea: modalities as search operators

The solver is built around a practical observation: to solve tasks that frontier systems *do not already solve*, the correct solution is often a **minority hypothesis**. Therefore, the solver intentionally creates many *independent* candidate solutions across heterogeneous reasoning modalities (text, image, and code), maximizing the probability that at least one candidate captures a genuinely novel hypothesis. Each modality provides a structurally different representation of the same task, which empirically produces candidates that cluster differently (Section 4).

### Pipeline overview

Figure 1 shows the end-to-end pipeline. For each ARC task:

![Solver pipeline: candidate generation with adaptive early stopping, holistic judging, and weighted scoring.](figures/pipeline.png)

1. **Candidate generation (up to 29 candidates).** Run modality-specific solvers across text, image, and code reasoning channels. Each candidate produces one output grid and a reasoning trace; for code candidates, this includes iterative tool calls and execution logs. If early-stage candidates show strong agreement, the system terminates early and skips remaining modalities (adaptive early stopping).

2. **Holistic judging (3 parallel judges).** Concatenate all candidate traces into a single long-context prompt (30k--80k tokens) and ask a judge model to identify the top-2 most likely correct candidates (or propose a synthesis), explain why other clusters are wrong, and output the final grids.

3. **Weighted scoring.** Each judge's first choice receives 2 points and second choice receives 1 point. The two distinct output grids with the highest total score become the solver's pass@2 guesses.

### Candidate generation

Candidate generation uses three foundation models --- **Gemini 3 Preview**, **GPT-5.2**, and **Claude Opus 4.5** --- across three modality families. The full configuration (29 generators; see appendix for details) groups candidates as follows:

- **Text (8 candidates):** Standard text prompting with a minimal prompt (see appendix) across multiple models, plus a "deep think" configuration that allocates a larger reasoning budget. The prompt deliberately avoids prescribed reasoning templates to maximize hypothesis diversity.
- **Image (10 candidates):** Grids are rendered as annotated images alongside the instruction prompt (example rendering in the appendix). Renderings are intentionally **imprecise** --- slightly distorted rather than pixel-perfect --- because imprecision empirically encourages models to reason about shapes and spatial relationships at a higher level of abstraction rather than falling back to cell-by-cell numerical reasoning.
- **Code (11 candidates):** Program synthesis via two regimes: (i) *tool-integrated* code generation with iterative sandbox execution and debugging, and (ii) *one-shot* code generation without execution feedback. Tool-integrated generation produces rich intermediate artifacts consumed by the holistic judge.^[The ARC Prize semi-private evaluation uses OpenAI's zero-data-retention (ZDR) API mode, which disables tool calls. For that run, tool-integrated candidates were replaced with one-shot code generation.]

### Holistic judging

The key insight is that **having all context together beats abstracting traces into scores**. Three alternative judging approaches were tested:

1. **Logic judge (failed):** scoring candidates by reasoning consistency. Failure mode: candidates can be "logical" yet overfit to training pairs.
2. **Consistency judge (partial):** rewarding themes that repeat across candidates. Failure mode: rewards the majority cluster, but the correct solution on hard tasks is often a minority hypothesis.
3. **Holistic judge (final):** providing *all traces together* and asking the judge to pick the top-2 candidates. This lets the judge detect subtle but decisive differences between near-identical hypotheses.

The holistic judge can be understood as an **anti-consistency** mechanism: it is designed to override the plurality answer when trace-level reasoning suggests a minority candidate better generalizes to the test instance. Self-consistency [@wang2022selfconsistency] selects the most common answer --- effective when the majority is correct. On ARC-AGI-2, the majority is often *wrong* on the hardest tasks, making consistency-based selection a liability.

All three judges use **GPT-5.2** (x-high reasoning). A mixed-model ensemble was tested but three homogeneous GPT-5.2 judges outperformed the mixed configuration. The judge prompt (detailed in the appendix) provides all candidate traces and outputs, and asks for a "meta-conclusion" without instructing the judge to prefer majority or minority answers. Each candidate's content block contains the full reasoning trace --- for text/image candidates, the chain-of-thought response; for code candidates, the complete iterative tool-use trace including intermediate program drafts, execution outputs, and debugging steps.

**Synthesis.** The judge may also propose a **novel solution** not identical to any candidate output, recombining correct subcomponents of multiple flawed candidates. This matters on tasks where no single candidate is fully correct but multiple candidates contain partial truths.

**Known limitations.** Candidate order is not shuffled between judge runs, which could introduce position bias. The judge may also exhibit verbosity and format biases [@zheng2023judging]. No debiasing is applied in the current implementation.

