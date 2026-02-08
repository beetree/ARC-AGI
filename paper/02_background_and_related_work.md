## Background and Related Work

This paper sits at the intersection of (i) **abstraction-centric few-shot generalization** as instantiated by ARC-style tasks, (ii) **search-based and neuro-symbolic solvers** that treat ARC as a latent-program induction problem, and (iii) **test-time compute scaling** strategies for frontier LLMs—especially approaches that generate multiple candidate trajectories and then **select, verify, or judge** among them. This section reviews the ARC/ARC-AGI benchmark lineage, highlights major families of solver approaches, and situates “modality search + trace-preserving holistic judging” relative to the most relevant prior work.

### ARC and ARC-AGI as a benchmark for abstraction under minimal priors

The Abstraction and Reasoning Corpus (ARC) was introduced by @chollet2019measure as part of a broader argument for measuring intelligence as **skill-acquisition efficiency**—how effectively a system can acquire and apply new skills under constrained experience and priors. ARC’s design emphasizes rapid generalization from a small number of examples, with tasks intended to require only relatively elementary “core knowledge” and to discourage reliance on domain knowledge or internet-scale memorization.

ARC tasks are framed as **few-shot input–output induction**: given a handful of training demonstrations (pairs of grids), the solver must infer an underlying transformation rule and apply it to a held-out test input. The hallmark difficulty is **underspecification**: multiple hypotheses can explain the training pairs, but only a subset will transfer to the test instance, so solvers must cope with an intense “many consistent hypotheses” regime where superficial fit is not enough.

As a concrete example, Figure 1 shows all three training pairs and the test input from task `3dc255db`.^[https://arcprize.org/play?task=3dc255db] A human might interpret the shapes as "spaceships": colored particles sit inside each ship on the exhaust side, and the transformation removes them from the interior and places them on the nose, extending the ship in its direction of travel. The solver must infer this rule — identifying containment, directionality, and the interior/exterior distinction — from only three training demonstrations, then apply it to the unseen test input (bottom row). This task remains unsolved by the solver described in this paper: all 29 candidates failed, and none of GPT-5.2, Gemini 3, or Opus 4.5 produced a correct output.

![ARC-AGI-2 task `3dc255db`. A human might see "spaceships" with particles on the exhaust side. The transformation removes the particles from the interior and extends them from the nose. Three training pairs (rows 1--3) demonstrate the rule; the test input (row 4) must be solved from these examples alone. This task remains unsolved.](figures/task_example.png)

A recurring theme in ARC research is that the benchmark stresses **compositional abstraction** (e.g., combining multiple latent concepts) and **distribution shift within each task** (training vs. test), rather than data-driven interpolation across a large IID dataset. This is part of what makes ARC resistant to straightforward deep learning approaches trained on the released tasks alone, and it motivates solver families that include explicit search, symbolic representations, or test-time adaptation.

### The ARC Prize ecosystem and the evolution to ARC-AGI-2

#### ARC competitions and the “slow progress” era

After ARC’s release, the first major public competition was the Kaggle “Abstraction and Reasoning Challenge” (2020). The best-performing solutions in that era were largely **program-synthesis / DSL-search systems**, and performance improved only gradually for several years—an arc that ARC Prize reports explicitly document when motivating why new benchmark design was needed.

The ARC Prize effort expanded this ecosystem with additional competitive events and a more formalized reporting and verification posture, including an explicit policy around “ARC Prize Verified” scores to reduce confusion arising from incomparable, self-reported results.

#### ARC-AGI-2: design goals, splits, and evaluation protocol

ARC-AGI-2 was introduced as a second-generation benchmark intended to provide a more informative signal at the frontier of reasoning systems. The technical report [@arcprize2024report] highlights several goals: maintain the original ARC principles and format, reduce susceptibility to brute-force program search, incorporate **first-party human testing**, and increase “signal bandwidth” (a wider useful range of scores to track progress).

ARC-AGI-2 also formalizes dataset splits and calibration:

* **Training set**: 1000 public tasks spanning a wide range of difficulties.
* **Public evaluation set**: 120 calibrated public tasks.
* **Semi-private evaluation set**: 120 calibrated non-public tasks (used for the live leaderboard and ARC Prize leaderboard).
* **Private evaluation set**: 120 calibrated non-public tasks (used for final contest ranking).

A key protocol detail is the use of **pass@2** scoring, acknowledging that some tasks can contain genuine ambiguity; ARC Prize materials emphasize that the benchmark’s human calibration also used the same “two attempts” framing (e.g., tasks solved pass@2 by at least two humans).

Finally, ARC Prize’s public-facing evaluation culture emphasizes not just raw accuracy but also **efficiency** and comparability (including leaderboard reporting and verification norms).

### Classical ARC solvers: DSL program synthesis and enumerative search

The most historically influential “classical” ARC solver family treats tasks as **latent programs** composed from a hand-designed library of primitives (a DSL). The Kaggle 2020 top solutions are widely recognized as belonging to this category: they relied on enumerating candidate transformation chains (sometimes aggressively optimized in low-level languages) to find programs consistent with the demonstrations, and then applying the discovered program to the test input.

These approaches matter as baseline “proofs of tractability” for a subset of ARC tasks and as a reminder that **search can compensate for weak learned priors**—but they also illuminate why ARC-AGI-2 explicitly tries to be “less brute-forcible.” In particular, ARC Prize’s ARC-AGI-2 announcement and technical report describe removing or redesigning evaluation tasks that were overly susceptible to brute-force search methods.

Beyond DSL enumeration, related symbolic traditions include approaches that use **compression / minimum description length (MDL)** principles to guide search over explanations. @ferre2021arc provides a representative example: describing grids using explicit models and searching for explanations that compress the observations, illustrating an alternative axis of “prior + search” design that emphasizes interpretability and parsimony rather than only brute-force enumeration.

### Benchmark extensions and data augmentation in the ARC domain

Several efforts address limitations of the original ARC release: ConceptARC [@moskvichev2023conceptarc] introduces concept-grouped task variants to probe systematic generalization; ARC-GEN [@moffitt2025arcgen] proposes a procedural benchmark generator; and Re-ARC [@hodel2024rearc] provides a programmatic reproduction of ARC tasks frequently used for generating synthetic training variations.

### Learned approaches: transduction, induction, and hybridization

ARC has also been attacked from a purely learned perspective (e.g., treating ARC as image-to-image translation), but results historically lagged behind symbolic-search systems and humans. ARC Prize’s technical reporting explicitly notes early deep-learning baselines performing very poorly on ARC-AGI, motivating hybrid approaches and new data strategies.

Recent work has sharpened the conceptual distinction between:

* **Induction**: infer a latent function/program consistent with demonstrations, then apply it.
* **Transduction**: directly predict the test output conditioned on the demonstrations and test input, without explicitly representing a latent program.

@li2024induction study this tradeoff on ARC and find induction and transduction succeed on different problem families; importantly, they show that combining (ensembling) these paradigms can approach human-level performance on the original ARC benchmark under their experimental setup and synthetic training regime. Complementary work on small or specialized models [@fletcherhill2024miniarc; @puget2024nGPT] explores architectural inductive biases for 2D grid structure — highlighting the increasing importance of **test-time procedures** (refinement, adaptation, search) even when the base model is learned.

### Test-time adaptation and compute scaling for ARC-style tasks

A major recent shift in ARC solving is the move from purely “static” models or solvers to methods that treat each ARC task as an opportunity for **test-time learning** or **test-time search**.

@akyurek2024surprising demonstrate that updating model parameters at test time (under carefully controlled procedures) can yield surprisingly strong gains on ARC-like reasoning, reinforcing the idea that ARC is a testbed for *within-task* adaptation rather than only pretraining.

Other ARC Prize–era work explores search and induction at test time in more explicitly programmatic spaces: @bonnet2024latent combines learned representations with explicit search over programs, while @ouellette2024neurally compares neurally-guided program induction paradigms across grid, program, and transform spaces. At the systems level, competitive solvers increasingly resemble **pipelines** that integrate synthetic data, model adaptation, search components, and ensembles [@arcprize2024report].

### LLM-era reasoning: generating and coordinating multiple trajectories

Independently of ARC, the broader LLM literature has developed a family of **test-time compute** and **trajectory diversification** techniques that are directly relevant to the solver architecture in this paper. @snell2024scaling show that optimally allocating test-time compute — e.g., by generating and selecting among multiple candidate solutions — can be more effective than scaling model parameters, providing formal grounding for architectures that trade inference-time search budget for performance.

#### Chain-of-thought and sampling-based diversification

Chain-of-thought prompting [@wei2022chain] established that eliciting intermediate reasoning steps can improve performance on multi-step tasks.

Self-consistency [@wang2022selfconsistency] then proposed a simple but influential extension: sample multiple reasoning paths and select the most consistent final answer, demonstrating that *diversity + aggregation* can outperform a single greedy reasoning trace.

#### Reasoning as search over “thoughts”

Tree of Thoughts [ToT; @yao2023tree] reframes inference as explicit search over intermediate "thoughts," enabling branching, lookahead, and backtracking.
Graph of Thoughts [GoT; @besta2024graph] generalizes this idea to arbitrary graph-structured reasoning artifacts, emphasizing more flexible dependency structures across intermediate units of information.

These frameworks provide language for understanding ARC solvers that “branch” over hypotheses rather than commit early, and they motivate treating candidate generation as a search process rather than a single pass.

#### Tool use and program-aided reasoning

ReAct [@yao2022react] interleaves reasoning traces with actions (tool calls / environment interactions), highlighting how external tools can mitigate hallucination and enable more reliable task completion.

Toolformer [@schick2023toolformer] provides a training-time perspective, showing that LMs can learn to decide *when and how* to call tools via self-supervision, further legitimizing tool-augmented reasoning as a general capability axis.

PAL [Program-aided Language Models; @gao2023pal] formalizes a closely related idea: use the LM to translate problems into runnable code, then outsource exact computation to an interpreter—often improving accuracy on tasks where arithmetic/logic errors dominate.

These ideas are directly relevant to ARC, where code synthesis can serve both as a hypothesis generator and as a way to expose structured intermediate artifacts (programs, tool outputs) that may be useful during downstream selection.

#### Iterative refinement and memory-based improvement

Self-Refine [@madaan2023selfrefine] shows that a single LM can iteratively improve its output by generating feedback and revisions in a loop, without gradient updates.
Reflexion [@shinn2023reflexion] similarly aims to improve test-time performance by incorporating feedback into a memory buffer that influences subsequent attempts, framing improvement as “verbal reinforcement learning” rather than weight updates.

These methods relate to ARC attempts that “try multiple times” and learn from earlier mistakes, though they also introduce a key trade-off: iterative refinement can increase compute while risking **anchoring** to early hypotheses—an issue that becomes acute on ARC tasks where early commitments can be misleading.

### Selection, verification, and “LLM-as-a-judge” paradigms

Generating diverse candidates is only half the problem; the other half is selecting among them. In the LLM ecosystem, selection is increasingly delegated to learned or LLM-based evaluators, giving rise to the “LLM-as-a-judge” paradigm.

@zheng2023judging formalized and stress-tested LLM judging in the context of MT-Bench and Chatbot Arena, showing that strong LLM judges can correlate well with human preferences while also exhibiting systematic biases (e.g., position and verbosity biases). Subsequent work has explored structured multi-agent evaluation (judge-and-jury designs) and cautioned that judging format (pairwise vs. pointwise, aggregation schemes) materially affects robustness.

For ARC in particular, selection is unusually difficult because many hypotheses fit the demonstrations yet fail on the test instance. A good judge must reward **transfer-valid abstractions**, not merely fluent rationales or training-pair fit.

### Positioning of this work within the landscape

Relative to the above literature, the approach in this paper can be viewed as a systems-level composition of three trends:

1. **Hypothesis generation as explicit search** (a lineage shared with DSL/program-synthesis solvers and ToT/GoT-style inference [@yao2023tree; @besta2024graph]), but broadened beyond a single representation to *multiple reasoning modalities*.

2. **Tool- and program-mediated reasoning** [@yao2022react; @gao2023pal; @schick2023toolformer] used not just for execution but also as a way to produce richer intermediate artifacts that can be consumed by downstream selection.

3. **Judge-based selection** [LLM-as-a-judge; @zheng2023judging] adapted from general LLM evaluation into an in-task meta-reasoning component, with the additional complication that ARC demands judging *generalization under underspecification*, not merely surface quality.

What is relatively distinctive in the ARC context is the combination of (i) **heterogeneous candidate generators** (text, code, visual, extended deliberation) and (ii) **context-preserving comparison over full traces**, rather than scalar scoring or consensus compression—an axis that is motivated both by historical ARC solver failure modes (overfitting via brittle heuristics) and by known limitations of LLM judges under compressed, bias-prone evaluation formats.

---
