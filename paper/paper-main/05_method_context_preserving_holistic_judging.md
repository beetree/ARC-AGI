## Method: Context-Preserving Holistic Judging

### The judging problem: selecting the right needle in a noisy haystack

Given 8--29 candidates, many are plausible and internally coherent. Worse, models tend to **cluster** around the same wrong interpretation on the hardest tasks. The key difficulty is identifying a rare candidate that is correct—or close enough that it can be repaired—without reducing everything to an overly lossy score.

### Judges attempted (and why the “holistic” judge wins)

I tested three approaches:

1. **Logic judge (failed mode):** score candidates by whether their reasoning appears logically consistent.  
   Failure mode: a candidate can be “logical” yet overfit to training pairs or miss a newly introduced latent concept in the test case. Therefore logic alone is not robust.

2. **Consistency judge (partial):** look for themes that repeat across candidates.  
   Failure mode: consistency tends to reward the majority cluster. But breaking new ground requires elevating *divergent* hypotheses, because the correct solution to an unsolved task is often not the modal answer.

3. **Holistic judge (final):** provide *all traces together* and ask the judge to pick the top-2 most likely correct candidates. Run three judges in parallel and aggregate via weighted scoring (see below).
   This works because **having all context together beats abstracting traces into scores**. It lets the judge detect subtle but decisive differences between near-identical hypotheses.

The holistic judge can be understood as an **anti-consistency** mechanism. Self-consistency [@wang2022selfconsistency] selects the most common answer across samples — an effective strategy when the majority is likely correct. On ARC-AGI-2, the majority is often *wrong* on the hardest tasks (Section 6.8), making consistency-based selection a liability. The holistic judge inverts this: it is designed to identify a correct *minority* hypothesis against a confidently wrong majority, using full-trace comparison to distinguish genuine insight from plausible groupthink.

All three judges use **GPT-5.2** (x-high reasoning setting), the same model used for candidate generation but in a distinct role with a different prompt. I also tested a mixed-model judge ensemble (combining Opus, Gemini, and GPT-5.2), but three homogeneous GPT-5.2 judges outperformed the mixed configuration. Using the same model family for both generation and judging introduces a potential correlation risk (the judge may favor candidates "in its own style"), but in practice this was outweighed by GPT-5.2's stronger individual judging capability.

### Judge prompt structure

The holistic judge prompt is assembled programmatically and follows this structure (condensed; the full implementation is in the open-source release):

```text
Below is a problem that was attempted to be solved {N} times:

{training pairs + test input}

Solutions were generated {N} times, using different types of solvers.

<SOLUTION 1 START>
<CONTENT>
{full reasoning trace or extracted solver function}
</CONTENT>
<PREDICTED_GRID>
{candidate output as CSV}
</PREDICTED_GRID>
<SOLUTION 1 STOP>

... (repeated for all N solutions) ...

Your task is to understand these solutions, and assess how well they've
understood the problem, and how likely their solutions are to provide the
correct solution to the test input.

Often, new mechanics are introduced in the test example for which the
solutions do not generalize well. Please output two solutions that you
think represent the right mechanic for solving the problem.

Output your two solutions as grids (in code blocks). Explain how you
came to these two solutions being the two most likely. Study all the
provided solutions and their reasoning to come up with a meta-conclusion
about how to solve the problem.
```

Each candidate's `CONTENT` block contains the full reasoning trace — for text/image candidates this is the model's chain-of-thought response, and for code candidates it is the complete iterative tool-use trace including intermediate program drafts, execution outputs, and debugging steps. The `PREDICTED_GRID` block contains the candidate's output grid in CSV format. Candidates that produce identical output grids are listed as separate solutions (with separate traces), preserving the judge's ability to assess reasoning quality even when outputs agree. The prompt does **not** instruct the judge to prefer majority or minority answers — it asks for a "meta-conclusion," leaving the judge free to weigh agreement, reasoning quality, and novelty as it sees fit.

### Allowing synthesis (new solutions not in candidates)

The holistic judge is also permitted to propose a **novel solution not identical to any candidate output**, effectively recombining correct subcomponents of multiple flawed candidates. This matters on tasks where no single candidate "gets it," but multiple candidates contain partial truths. When synthesizing, the judge outputs a raw output grid directly (not executable code), which means synthesized solutions do not benefit from programmatic verification and are susceptible to arithmetic or grid-construction errors.

### Aggregation: from 3 judges to 2 final guesses

Each judge outputs a ranked pair of solutions (first choice and second choice). To produce the final pass@2 output, the system assigns **2 points** to each judge's first choice and **1 point** to each judge's second choice, then sums points across judges for each distinct output grid. The two grids with the highest total score become the solver's two guesses. When judges agree on their top pick, that solution accumulates up to 6 points; when they disagree, the scoring naturally surfaces the most broadly supported candidates. In practice, full three-way disagreement on the first choice is rare on easier tasks where candidates converge, but becomes common on harder tasks where the judges face the same ambiguity as the generators.

### Known limitation: judge biases

Candidate traces are concatenated into the judge prompt in a fixed order; the order is **not shuffled** between judge runs. LLMs exhibit known position biases (e.g., favoring candidates near the start or end of the context), and this ordering could systematically advantage or disadvantage certain candidates. Shuffling the candidate order across the three judge runs and measuring the effect on agreement and accuracy is a natural improvement.

Beyond position bias, the judge may also exhibit **verbosity bias** (favoring longer, more detailed reasoning traces over terse but correct ones) and **format bias** (favoring candidates whose output format more closely matches the judge's own generation patterns). These biases are well-documented in LLM-as-a-judge settings [@zheng2023judging] and could interact with the modality mix, since code candidates tend to produce structured traces while text candidates produce prose. No debiasing is applied in the current implementation.

### Feasibility and context length

The holistic judging prompt is intentionally large: on the order of **30k–80k input tokens**, because it includes full traces from many candidates.

This makes long-context frontier models a practical requirement for the judge step.

---



