## Discussion and Conclusion

This paper demonstrates that strong ARC-AGI-2 performance can be achieved by treating **modalities as search operators** and pairing diverse candidate generation with context-preserving selection: generate candidates independently across heterogeneous reasoning channels (text, image, code), then select using holistic judging over full traces.

### Limitations

**Cost and scalability.** The system spends $19.69--$38.99 per task --- orders of magnitude more expensive than a single model call. Much of the cost is spent on candidates that contribute nothing to the final answer. A production system would need adaptive routing, but no such mechanism has been developed here.

**Single-run results.** The headline numbers each come from a single evaluation run. No confidence intervals are reported because repeated full-pipeline runs were not performed (each costing ~$2,400). The true expected accuracy could be meaningfully higher or lower than the reported figures.

**Incomplete ablation coverage.** The component attribution claims are based on post-hoc analysis of a single run rather than controlled experiments. Several important ablations have not been performed due to cost constraints (see the appendix).

**Reproducibility fragility.** The system depends on specific proprietary model snapshots that may change or become unavailable over time. Full source code and raw data are released^[Anonymized for review.] to maximize reproducibility, but exact replication is not guaranteed.

**No learning across tasks.** The system treats each task independently --- no information is carried from one task to the next, unlike a human solver who would build intuitions across tasks.

**Narrow evaluation domain.** Results are demonstrated on a single benchmark (ARC-AGI-2). While the architectural pattern is domain-general in principle, this paper provides no evidence of transfer to other domains.

### Future work

- **Adaptive routing:** allocate expensive modalities only when uncertainty is high.
- **Judge compression:** reduce context size while retaining the benefits of joint context.
- **Synthesis gating and amplification:** decide *when* synthesis is likely to help, and invoke additional synthesis attempts with varied prompting when high potential is identified.
- **Image representation tuning:** systematic study of rendering parameters and their interaction with different vision-language models.
- **Formal diversity quantification:** richer diversity measures (pairwise disagreement rates, embedding-space distances) to enable principled decisions about generator selection.
- **Domain transfer:** validate the "diverse generation + holistic judging" pattern on non-ARC benchmarks.
- **Further ablations:** the unperformed ablations listed in the appendix would substantially strengthen the paper's claims.

### Conclusion

ARC-AGI-2 progress is moving quickly, and the benchmark is explicitly designed to push beyond what scaling alone yields. This work demonstrates that treating modalities as search operators and selecting via context-preserving holistic judging can substantially exceed the performance of the strongest commercially available LLMs --- achieving 72.9% versus 54.2% for the best single-model baseline, a +18.7 percentage-point improvement. The architectural pattern is simple: **search across modalities, judge in full context.** The results suggest that orchestrating diverse reasoning channels with principled selection is a powerful lever for abstract reasoning, complementary to and currently ahead of gains from scaling individual models alone.

\subsubsection*{Ethics Statement}

This work uses publicly available benchmarks (ARC-AGI-2) and commercial LLM APIs. No human subjects, personal data, or sensitive information are involved. The system's sole purpose is solving abstract reasoning tasks on a research benchmark. The computational cost of this approach (approximately \$2,400 per full evaluation run) is disclosed throughout the paper. All foundation models are accessed via their standard commercial APIs under their respective terms of service.

\subsubsection*{Reproducibility Statement}

The full source code --- including all prompts, tool schemas, candidate generation configurations, and judging logic --- is publicly available.^[Anonymized for review.] The complete public-evaluation run data --- including all API parameters, model versions, and raw logs (prompts, responses, reasoning traces, intermediate artifacts, and judge transcripts; over 7 million lines) --- is also publicly available.^[Anonymized for review.] The semi-private evaluation was executed by the ARC Prize verification infrastructure; the authors do not control that environment and cannot release those logs. Because the system depends on specific proprietary model snapshots (GPT-5.2, Gemini 3 Preview, Opus 4.5) that may change over time, exact numerical replication is not guaranteed even with identical code and parameters.
