### Context-Preserving Holistic Judging

Given 8--29 candidates per task, many are plausible and internally coherent. Worse, models tend to **cluster** around the same wrong interpretation on the hardest tasks. The key difficulty is identifying a rare candidate that is correct — or close enough that it can be repaired — without reducing everything to an overly lossy score. Three judging approaches were tested:

1. **Logic judge (failed):** Scoring candidates by whether their reasoning appears logically consistent fails because a candidate can be internally coherent yet overfit to training pairs or miss a latent concept introduced in the test case.
2. **Consistency judge (partial):** Selecting themes that repeat across candidates rewards the majority cluster, but breaking new ground requires elevating *divergent* hypotheses — the correct solution to an unsolved task is often not the modal answer.
3. **Holistic judge (final):** All traces are provided *together* in a single prompt, and the judge picks the top-2 most likely correct candidates. Three judges run in parallel and their picks are aggregated via weighted scoring. This works because having all context together beats abstracting traces into scores, letting the judge detect subtle but decisive differences between near-identical hypotheses.

The holistic judge can be understood as an **anti-consistency** mechanism. Self-consistency [@wang2022selfconsistency] selects the most common answer across samples — an effective strategy when the majority is likely correct. On ARC-AGI-2, the majority is often *wrong* on the hardest tasks (Section IV-F), making consistency-based selection a liability. The holistic judge inverts this: it is designed to identify a correct *minority* hypothesis against a confidently wrong majority, using full-trace comparison to distinguish genuine insight from plausible groupthink.

All three judges use **GPT-5.2** (x-high reasoning setting), the same model used for candidate generation but in a distinct role with a different prompt. A mixed-model ensemble (combining Opus, Gemini, and GPT-5.2) was tested, but three homogeneous GPT-5.2 judges outperformed the mixed configuration.

**Judge prompt structure.** The holistic judge prompt is assembled programmatically and follows this structure (condensed; full implementation in the open-source release):

```text
Below is a problem attempted {N} times:
{training pairs + test input}
<SOLUTION 1 START>
<CONTENT>{full reasoning trace}</CONTENT>
<PREDICTED_GRID>{candidate output as CSV}</PREDICTED_GRID>
<SOLUTION 1 STOP>
... (repeated for all N solutions) ...
Your task is to assess how well they've understood the
problem. Often, new mechanics are introduced in the test
example. Please output two solutions that represent the
right mechanic for solving the problem.
```

Each candidate's `CONTENT` block contains the full reasoning trace — for text/image candidates this is the model's chain-of-thought response, and for code candidates it is the complete iterative tool-use trace including intermediate program drafts, execution outputs, and debugging steps. Candidates producing identical output grids are listed as separate solutions with separate traces, preserving the judge's ability to assess reasoning quality even when outputs agree. The prompt does **not** instruct the judge to prefer majority or minority answers — it asks for a "meta-conclusion," leaving the judge free to weigh agreement, reasoning quality, and novelty as it sees fit. The resulting prompt is intentionally large: on the order of **30k--80k input tokens**, making long-context frontier models a practical requirement for the judge step.

**Synthesis.** The holistic judge is also permitted to propose a **novel solution not identical to any candidate output**, effectively recombining correct subcomponents of multiple flawed candidates. This matters on tasks where no single candidate fully solves the problem but multiple candidates contain partial truths. Synthesized solutions are output as raw grids (not executable code), which means they do not benefit from programmatic verification and are susceptible to arithmetic or grid-construction errors.

**Aggregation.** Each judge outputs a ranked pair of solutions (first choice and second choice). The system assigns **2 points** to each judge's first choice and **1 point** to each judge's second choice, then sums points across judges for each distinct output grid. The two grids with the highest total score become the solver's pass@2 guesses. When judges agree on their top pick, that solution accumulates up to 6 points; when they disagree, the scoring naturally surfaces the most broadly supported candidates. A known limitation is that candidate traces are concatenated in a fixed order without shuffling between judge runs, which may interact with LLM position biases [@zheng2023judging]; shuffling candidate order across runs is a natural improvement.

---
