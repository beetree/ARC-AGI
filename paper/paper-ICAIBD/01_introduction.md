## Introduction

A central challenge in applying LLMs to abstract reasoning is not just producing candidate solutions, but **knowing what is right and what is wrong** in a setting where models can be confidently incorrect---even when they provide detailed, plausible reasoning traces.

ARC-AGI-2 was designed to be *easy for humans and hard for AI*, and---critically---to measure both **capability** and **efficiency** (cost). Progress on ARC-style benchmarks has been rapid: ARC Prize reports significant year-over-year improvements driven by frontier reasoning systems and application-layer refinement harnesses [@arcprize2024report].

This paper describes an approach that treats **modalities as search operators** and uses **judging as the final selection mechanism**: generate diverse candidate solutions across independent reasoning channels, then select among them using context-preserving holistic judging.^[An extended version of this paper with complete failure analysis, task-level breakdowns, judge rationale transcripts, and additional ablation details is available as a preprint [@land2026modality].]

### Contributions

- **A modality-driven search solver** that generates candidates independently across text, image, and code reasoning channels.
- **A context-preserving holistic judge** that reads all candidate traces jointly to select the best outputs, identifying correct *minority* hypotheses---yielding +7 solved instances over majority vote at only 13% of total system cost (Section V).
- **Verified ARC-AGI-2 semi-private performance:** 72.9% at $38.99/task on the ARC Prize Verified leaderboard^[https://arcprize.org/leaderboard]---the highest score on the leaderboard at the time of writing, exceeding the best standalone frontier models (GPT-5.2 Pro at 54.2%, Gemini 3 Pro at 54.0%) by +18.7 percentage points.
- **Public eval performance:** 76.11% at $19.69/task (self-measured).
- **Open-source release** of the full source code^[https://github.com/beetree/ARC-AGI] plus detailed negative results. The complete public-evaluation run data---over 7 million lines of prompts, responses, reasoning traces, and judge transcripts---is also released^[https://www.kaggle.com/code/johanland/johan-land-solver-v7-public/comments?scriptVersionId=290052212] to support future research.

---
