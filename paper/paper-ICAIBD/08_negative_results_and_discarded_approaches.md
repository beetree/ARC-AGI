## Negative Results

Several development ideas were discarded because they reduced diversity or increased brittleness. Two findings stand out for their direct impact on the final system design.

**Prescriptive prompting degrades performance.** Reasoning templates, structured output requirements, chain-of-thought scaffolding, and domain-specific heuristics consistently hurt performance on the hardest tasks. The mechanism appears to be a **compliance tax on reasoning**: when told exactly *how* to think, models spend more of their test-time compute budget following the template and less on exploring unconventional hypotheses. On easy tasks this overhead is often harmless, but on hard tasks it suppresses the creative leaps needed to escape the main wrong-answer cluster. Prescriptive prompts also interact badly with diversity: when all candidates follow the same template, they are more likely to converge on the same flawed interpretation. The final system therefore uses deliberately minimal prompts with tolerant downstream parsing.

**Hint generation collapsed diversity.** A two-stage approach -- generate a hint, then solve conditioned on that hint, structurally similar to Self-Refine [@madaan2023selfrefine] and Reflexion [@shinn2023reflexion] -- was tested and discarded. The hint stage consistently narrowed candidate diversity into a smaller hypothesis space, which is counterproductive when the correct solution may require an unconventional reasoning path. Similarly, staged decomposition pipelines often suffered brittle handoffs, regressing candidate outputs toward the mean rather than broadening the search.

Several other approaches were also discarded: strict output schemas, synthetic code-data augmentation, and weaker generator configurations that contributed little unique coverage. The synthetic augmentations were especially weak because surface-level transforms did not create new structural challenges, and geometric transforms could even break task semantics on orientation-dependent problems.

---
