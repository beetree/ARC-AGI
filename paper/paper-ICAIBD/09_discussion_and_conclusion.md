## Discussion and Conclusion

This paper demonstrates that strong ARC-AGI-2 performance can be achieved by treating **modalities as search operators** -- generating candidates independently across heterogeneous reasoning channels (text, image, code) to maximize hypothesis diversity, then selecting using holistic judging over full traces. At the time of writing, this approach achieves the highest score on the ARC Prize Verified leaderboard (72.9%), surpassing the best-performing standalone frontier models -- GPT-5.2 Pro (54.2%) and Gemini 3 Pro (54.0%) -- by +18.7 percentage points. This substantial margin suggests that orchestrating diverse reasoning modalities with principled selection is a more effective strategy for abstract reasoning than scaling any single model alone.

The system's core contributions are architectural rather than model-specific. First, multi-modal candidate generation exploits the observation that text, image, and code representations activate different reasoning pathways -- each modality exclusively solves tasks inaccessible to the others (Table 3). Second, holistic judging over full reasoning traces recovers minority-correct solutions that majority voting discards, yielding +7 instances of uplift. Third, judge synthesis enables the construction of novel correct outputs from complementary partial insights when no single candidate is fully correct. These mechanisms are complementary: diverse generation expands the hypothesis space, while context-preserving selection navigates it.

### Limitations

**Cost and practical scalability.** The system spends $19.69--$38.99 per task -- orders of magnitude more expensive than a single model call. ARC Prize explicitly treats efficiency as a first-class metric [@arcprize2024report], and the current system is far from efficient. The brute-force strategy of generating 29 candidates across three models and three modalities, then running three separate judge passes, is effective but wasteful; a production system would need adaptive routing that allocates expensive modalities only when uncertainty is high, but no such mechanism has been developed here.

**Single-run results.** The headline numbers (76.11% public, 72.9% semi-private) each come from a single evaluation run. LLM outputs are stochastic, and the system's reliance on sampling diversity means that results will vary across runs; no confidence intervals are reported because repeated full-pipeline runs were not performed (each costing ~$2,400).

**No learning across tasks.** The system treats each task independently — no information is carried from one task to the next, unlike a human solver who would build intuitions across tasks.

**Narrow evaluation domain.** The system has been evaluated exclusively on ARC-AGI-2; whether the architectural pattern — modality-driven search with holistic judging — generalizes to other abstract reasoning benchmarks or broader AI tasks is unknown.

**Reproducibility fragility.** The system depends on specific proprietary model snapshots (GPT-5.2, Gemini 3 Preview, Opus 4.5) and vendor-specific reasoning settings that may change or become unavailable over time. Results may not be exactly reproducible even with identical prompts and parameters if the underlying model versions drift.^[Source code: https://github.com/beetree/ARC-AGI. Complete raw data for the public evaluation run (prompts, responses, reasoning traces, judge transcripts; over 7 million lines): https://www.kaggle.com/code/johanland/johan-land-solver-v7-public/comments?scriptVersionId=290052212.]

### Future Directions

Two directions appear most promising. **Adaptive routing** would allocate expensive modalities only when early-stage candidates show low agreement, reducing cost without sacrificing accuracy on hard tasks; the early-stopping heuristic already demonstrates the principle (97.3% accuracy on easy tasks at reduced cost), but a more principled uncertainty-driven routing mechanism could extend this to the full difficulty spectrum. **Synthesis gating** would trigger judge synthesis only when candidate agreement is low or when multiple candidates contain complementary partial solutions, potentially amplifying the +1 instance uplift observed in this work on harder tasks where the recombination mechanism has the most potential.

### Acknowledgments

Thank you to the ARC-AGI Discord community for valuable discussion and shared insights throughout the development of this work, and to Greg Kamradt at ARC Prize for conducting the official semi-private evaluation.
