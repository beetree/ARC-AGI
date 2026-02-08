## Negative Results and Discarded Approaches

This section documents explored approaches that were ultimately discarded, often because they reduced diversity, increased brittleness, or forced premature abstraction.

### Hint generation → solver (discarded)

This approach is structurally similar to iterative self-improvement methods such as Self-Refine [@madaan2023selfrefine] and Reflexion [@shinn2023reflexion], where an initial pass generates feedback that informs a subsequent attempt.

Motivation:
- doubling the reasoning budget across two turns (hint then solve).

Observed drawback:
- the hint stage often **limits creativity** and collapses candidate diversity into a narrower space, which is counterproductive when trying to break new ground.

### Object identification → transformation identification → solver (discarded)

Motivation:
- structured decomposition to “force” abstraction.

Failure mode:
- brittle handoff between stages. Both verbose and overly terse handovers caused confusion and reduced diversity, often regressing toward the mean rather than expanding the hypothesis space.

### Opus codegen and Opus image reasoning (discarded from final mix)

In the final system, Opus contributes only a single text-reasoning candidate. Opus codegen and image reasoning were tested but contributed less uniquely relative to the GPT/Gemini configurations, and were dropped from the final candidate mix.

### Grid representations and output constraints (discarded variants)

Key findings:

- **CSV-style** encoding outperformed many alternatives, especially as grids grow and representation consumes a large share of the reasoning budget.
- Forcing strict outputs (e.g., **requiring JSON** via API-level response formats) underperformed. This is important because strict schemas are a common LLM engineering practice, but appear to reduce model effectiveness on this domain.

Engineering trade-off:
- removing constraints increases output noise; robust parsing (regex + validation) becomes necessary, but was worth it for accuracy.

### Synthetic data augmentation for code candidates (discarded)

Motivation:
- generate additional training examples (e.g., via color permutation, rotation, or mirroring of the provided pairs) to give code-generation candidates more test cases to validate against, potentially improving program correctness.

Reasons for discarding:
- **Surface-level augmentations add little signal.** Color permutations produce nominally distinct examples but do not test new structural properties of the transformation; a program that overfits to the original examples will typically also pass color-permuted variants.
- **Geometric transforms break semantics.** Rotation and mirroring alter the meaning of tasks that depend on absolute orientation — for example, gravity-based tasks (where "down" matters) or tasks where spatial relationships across training pairs encode the rule (e.g., map reconstruction). Applying these transforms indiscriminately would introduce incorrect training signal.
- **Meaningful augmentation requires solving the task first.** Generating genuinely informative synthetic examples (new inputs paired with correct outputs) requires knowing the transformation rule — which is the problem the solver is trying to solve. This makes meaningful augmentation infeasible in a private-dataset evaluation setting where ground-truth transformations are unavailable.

### Extensive prompt engineering (discarded)

This is perhaps the most counterintuitive finding in the paper, and it directly contradicts standard LLM engineering practice.

The conventional approach to LLM integration treats the model as a programmable API: the more precisely you specify the desired behavior — step-by-step instructions, prescribed reasoning templates, output schemas, chain-of-thought scaffolding — the better the results. This works well for structured tasks like data extraction, classification, or format conversion, where the solution space is well-defined and the model's job is to comply with a specification.

On ARC-AGI, this approach consistently degraded performance. During development, I tested numerous prompt engineering strategies including:

- **Prescribed reasoning templates:** instructing the model to first identify objects, then describe transformations, then apply them step by step.
- **Structured output requirements:** requiring specific output formats (e.g., JSON grids via API-level response format constraints).
- **Detailed chain-of-thought scaffolding:** breaking the reasoning into named stages ("Step 1: Identify the pattern. Step 2: Describe the rule. Step 3: Apply to test input.").
- **Domain-specific heuristics in the prompt:** suggesting the model look for symmetry, rotation, color mapping, or other common ARC patterns.
- **Iterative prompt refinement:** tuning prompt wording based on failure analysis of specific tasks.

In every case, the more prescriptive the prompt, the worse the system performed on the hardest tasks. The final system uses a deliberately minimal prompt (Section 4) that provides only the task data, a brief context sentence, and a request to explain reasoning — with no prescribed structure, no step-by-step template, and no domain heuristics.

The mechanism appears to be a **compliance tax on reasoning**: when the model is given detailed instructions about *how* to think, it allocates a significant portion of its reasoning budget to following those instructions rather than to actually solving the problem. On easy tasks — where the transformation is simple enough that any reasonable approach works — this overhead is harmless. On hard tasks — where the model needs to make creative leaps, entertain unusual hypotheses, or reason about structures it has never seen — the overhead is fatal. The model dutifully follows the prescribed template, produces a well-formatted but wrong answer, and never explores the unstructured reasoning path that might have led to the correct solution.

This also interacts with diversity: a prescriptive prompt narrows the hypothesis space across candidates. When all N candidates follow the same reasoning template, they tend to converge on the same (possibly wrong) answer. A minimal prompt allows different candidates to approach the problem from genuinely different angles, increasing the probability that at least one candidate finds the correct transformation.

The implication is that for novel reasoning tasks — where the solution is not known in advance and the model must discover it — **the best prompt is often the least prescriptive one**. The engineer's job shifts from programming the model's behavior to removing obstacles to the model's reasoning. This is uncomfortable for systems engineers accustomed to treating prompts as specifications, but on this benchmark, letting the model think freely and tolerating noisy outputs (with robust downstream parsing) consistently outperformed carefully engineered prompts.

---

