## Discussion and Conclusion

This paper demonstrates that strong ARC-AGI-2 performance can be achieved by treating **modalities as search operators** and pairing diverse candidate generation with context-preserving selection:

- generate candidates independently across heterogeneous reasoning channels (text, image, code) to maximize hypothesis diversity,
- then select using holistic judging over full traces.

At the time of writing, this approach achieves the highest score on the ARC Prize Verified leaderboard (72.9%), surpassing the best-performing standalone frontier models — GPT-5.2 Pro (54.2%) and Gemini 3 Pro (54.0%) — by +18.7 percentage points. This substantial margin suggests that orchestrating diverse reasoning modalities with principled selection is a more effective strategy for abstract reasoning than scaling any single model alone.

### Limitations

This work has several important limitations that should be weighed when interpreting the results.

**Cost and practical scalability.** The system spends $19.69 per task on the public evaluation and $38.99 per task on the semi-private set — orders of magnitude more expensive than a single model call. ARC Prize explicitly treats efficiency as a first-class metric [@arcprize2024report], and the current system is far from efficient. The brute-force strategy of generating 29 candidates across three models and three modalities, then running three separate judge passes over the full candidate pool, is effective but wasteful. Much of the cost is spent on candidates that contribute nothing to the final answer. A production system would need adaptive routing — spending heavily only on tasks that resist cheap methods — but no such routing mechanism has been developed here.

**Single-run results.** The headline numbers (76.11% public, 72.9% semi-private) each come from a single evaluation run. LLM outputs are stochastic, and the system's reliance on sampling diversity means that results will vary across runs. No confidence intervals are reported because repeated full-pipeline runs were not performed (each costing ~$2,400). The true expected accuracy could be meaningfully higher or lower than the reported figures, and the variance is unknown.

**Incomplete ablation coverage.** Section 7 reports post-hoc ablations for holistic selection (+7 instances) and synthesis (+1 instance), but these are extracted from a single run rather than from controlled experiments with matched baselines. Several ablations that would substantially strengthen the paper's claims — end-to-end modality removal, independent vs sequential generation, candidate budget scaling, judge ensemble sizing — have not been performed due to cost constraints. The component attribution claims in this paper should be understood as indicative rather than rigorous. Section 7 provides a detailed list of unperformed ablations.

**Reproducibility fragility.** The system depends on specific proprietary model snapshots (GPT-5.2, Gemini 3 Preview, Opus 4.5) and vendor-specific "reasoning settings" (e.g., OpenAI's "x-high" reasoning effort) that may change or become unavailable over time. Model providers routinely update model weights, deprecate API parameters, and alter rate limits without notice. Results may not be exactly reproducible even with identical prompts and parameters if the underlying model versions drift. To maximize reproducibility within these constraints, the full source code is open-sourced at https://github.com/beetree/ARC-AGI and the complete raw data for the public evaluation run — including all prompts, responses, reasoning traces, and judge transcripts (over 7 million lines) — is available on Kaggle at https://www.kaggle.com/code/johanland/johan-land-solver-v7-public/comments?scriptVersionId=290052212. Exact replication is nonetheless not guaranteed.

**No learning across tasks.** The system treats each task independently — no information is carried from one task to the next. A human solver would build intuitions across tasks (e.g., "tasks in this benchmark often involve symmetry" or "I've seen this color-mapping pattern before"), but the current system starts from scratch every time. This is both a limitation and a design choice: task independence simplifies the pipeline and avoids overfitting to task ordering, but it means the system cannot amortize its reasoning cost across related tasks.

**Narrow evaluation domain.** The results are demonstrated on a single benchmark (ARC-AGI-2). While the architectural pattern — diverse generation plus holistic judging — is domain-general in principle, this paper provides no evidence that the approach transfers to other domains. The specific design choices (modality mix, candidate count, judge prompt structure) were tuned for ARC and may not generalize without adaptation.

### Future work

- Adaptive routing: allocate expensive modalities only when uncertainty is high.
- Judge compression without premature abstraction: find ways to reduce context size while retaining the benefits of joint context.
- Further ablations: Section 7 lists a detailed set of unperformed ablations — including judge ensemble sizing, trace content contribution, per-model attribution, and early-stopping threshold tuning — that would strengthen component attribution claims.
- Synthesis gating and amplification: the current judge always has the option to synthesize a novel output. A gating mechanism that decides *when* synthesis is likely to help — e.g., only when candidate agreement is low or when no candidate passes a confidence threshold — could improve targeting. Conversely, when synthesis is identified as having high potential (e.g., multiple candidates contain complementary partial solutions), the system could invoke additional synthesis attempts with varied prompting to increase the probability of a correct recombination. The current single-pass synthesis yielded +1 instance (Section 7); a more aggressive, targeted synthesis strategy could yield further uplift on the hardest tasks where no single candidate is fully correct.
- Image representation tuning: the finding that intentionally imprecise grid renderings outperform pixel-perfect ones (Section 4) is suggestive but not well understood. Systematic study of rendering parameters — resolution, distortion level, color palette, annotation style — and their interaction with different vision-language models could yield further gains and clarify when and why visual prompting helps.
- Broader modality coverage: additional frontier providers and open-source models, plus parameter sweeps (temperature, etc.).
- Formal diversity quantification: the current paper measures modality complementarity via oracle overlap counts (Tables 3--4), but a richer diversity measure — e.g., pairwise output disagreement rates, embedding-space distances between reasoning traces, or information-theoretic metrics over the candidate distribution — would enable principled decisions about which generators to add, remove, or scale. A task-archetype taxonomy (classifying ARC tasks by the type of reasoning they require) could further clarify which modalities are most valuable for which problem classes.
- Domain transfer: the "diverse generation + holistic judging" pattern is not specific to ARC. Any domain where models produce confident but divergent answers — mathematical proof search, legal analysis, medical diagnosis — could benefit from context-preserving adjudication over multiple independent reasoning traces. Validating this on non-ARC benchmarks is a natural next step.

### A note on AI-assisted development

The solver was developed with AI assistance for both implementation and design (Section 3.3), with the author directing strategy and evaluating results. That this approach produced a competitive result in a solo-researcher setting suggests that AI-assisted development is a practical paradigm for complex pipelines.

### Reproducibility

The full source code for the solver is available at: https://github.com/beetree/ARC-AGI. The repository contains all prompts, tool schemas, candidate generation configurations, and judging logic.

The complete public-evaluation run — including all API parameters, model versions, and raw logs (prompts, responses, reasoning traces, intermediate artifacts, and judge transcripts; over 7 million lines) — is available as a Kaggle notebook: https://www.kaggle.com/code/johanland/johan-land-solver-v7-public/comments?scriptVersionId=290052212.

The semi-private evaluation was executed by ARC Prize's verification infrastructure; the author does not control that environment and cannot release those logs.

## Acknowledgments

Thank you to the ARC-AGI Discord community for valuable discussion and shared insights throughout the development of this work, and to Greg Kamradt at ARC Prize for conducting the official semi-private evaluation.
