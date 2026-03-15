## Discussion and Conclusion

This paper demonstrates that strong ARC-AGI-2 performance can be achieved by treating **modalities as search operators** and selecting with holistic judging over full traces. At the time of writing, the approach achieves 72.9% on the ARC Prize Verified leaderboard, exceeding the best standalone frontier models -- GPT-5.2 Pro (54.2%) and Gemini 3 Pro (54.0%) -- by +18.7 points. Within ARC-AGI-2, this suggests that orchestrating diverse reasoning modalities is more effective than scaling any single model alone.

The system's core contributions are architectural rather than model-specific. First, multi-modal candidate generation exploits the fact that text, image, and code representations activate different reasoning pathways, and each modality family contributes unique solves (Table 3). Second, holistic judging over full reasoning traces recovers minority-correct solutions that majority voting discards, yielding +7 instances of uplift. Third, judge synthesis can produce a novel correct output from complementary partial insights when no candidate is fully correct. Although synthesis appears only once in this run, that case is qualitatively important: it shows the architecture can sometimes **recombine partial evidence into a new correct solution**. These mechanisms are complementary: diverse generation expands the hypothesis space, while context-preserving selection navigates it and, in rare cases, repairs it compositionally.

Any claim of broader generality should be stated cautiously. The current evidence comes only from ARC-AGI-2, so cross-benchmark transfer is unproven. The most plausibly portable components are the high-level ideas: diverse hypothesis generation across representations, joint comparison of full candidate traces, and selective synthesis when partial truths are distributed across candidates. ARC-specific elements such as the grid encodings, the image-rendering setup, the 29-candidate budget, and the pass@2 aggregation rule should be viewed as task-tuned choices rather than universal prescriptions.

### Limitations

**Cost and practical scalability.** The system spends $19.69--$38.99 per task -- far more than a single model call. ARC Prize explicitly treats efficiency as a first-class metric, and the current 29-candidate, three-judge pipeline is effective but wasteful; a practical system would need adaptive routing that allocates expensive modalities only when uncertainty is high.

**Single-run results.** The headline numbers (76.11% public, 72.9% semi-private) each come from a single evaluation run. Because outputs are stochastic, results will vary across runs; no confidence intervals are reported because repeated full-pipeline runs were not performed.

**No learning across tasks.** The system treats each task independently; no information is carried from one task to the next.

**Narrow evaluation domain.** The system has been evaluated only on ARC-AGI-2. Whether the architectural pattern generalizes to other benchmarks or broader AI tasks is unknown.

**Reproducibility fragility.** The system depends on proprietary model snapshots (GPT-5.2, Gemini 3 Preview, Opus 4.5) and vendor-specific reasoning settings that may change or become unavailable over time. Source code and complete public-run artifacts are released, but results may not be exactly reproducible if the underlying model versions drift.^[Source code: https://github.com/beetree/ARC-AGI. Public-evaluation run data: https://www.kaggle.com/code/johanland/johan-land-solver-v7-public/comments?scriptVersionId=290052212.]

### Future Directions

Two directions appear most promising. **Adaptive routing** would allocate expensive modalities only when early-stage candidates show low agreement, reducing cost without sacrificing accuracy on hard tasks. The current early-stopping heuristic already works well on easy tasks, and the post-hoc analysis in Section V suggests that later candidate families should be added in stages rather than treated as equally valuable. **Synthesis gating** would trigger judge synthesis only when candidate agreement is low or when multiple candidates contain complementary partial solutions, potentially amplifying the +1 instance uplift observed here.

### Acknowledgments

Thank you to the ARC-AGI Discord community for valuable discussion and shared insights throughout the development of this work, and to Greg Kamradt at ARC Prize for conducting the official semi-private evaluation.
