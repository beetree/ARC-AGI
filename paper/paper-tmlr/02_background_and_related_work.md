## Background and Related Work

### ARC-AGI as a benchmark for abstraction

The Abstraction and Reasoning Corpus (ARC) was introduced by @chollet2019measure as part of a broader argument for measuring intelligence as **skill-acquisition efficiency**. ARC tasks are framed as **few-shot input--output induction**: given a handful of training demonstrations (pairs of grids), the solver must infer an underlying transformation rule and apply it to a held-out test input. The hallmark difficulty is **underspecification**: multiple hypotheses can explain the training pairs, but only a subset will transfer to the test instance. An illustrative task example is provided in the appendix.

ARC-AGI-2 [@arcprize2024report] is a second-generation benchmark with calibrated public, semi-private, and private evaluation splits (120 tasks each), designed to reduce susceptibility to brute-force program search and provide a wider useful range of scores. Evaluation uses **pass@2** scoring (two guesses permitted per test instance), and ARC Prize emphasizes not just raw accuracy but also **efficiency** (cost per task).

### Related work

**Classical ARC solvers** treat tasks as latent programs composed from a hand-designed DSL, relying on enumerative search over transformation chains [@ferre2021arc]. These systems established that search can compensate for weak learned priors, and motivated ARC-AGI-2's design to be "less brute-forcible."

**Learned and hybrid approaches** include transduction-based methods (directly predicting test outputs) and induction-based methods (inferring latent programs). @li2024induction show that combining induction and transduction can approach human-level performance on the original ARC under their experimental setup. Other notable approaches include latent program search [@bonnet2024latent], neurally-guided program induction [@ouellette2024neurally], small transformer models [@fletcherhill2024miniarc], and 2D nGPT architectures [@puget2024nGPT]. Benchmark extensions such as ConceptARC [@moskvichev2023conceptarc], ARC-GEN [@moffitt2025arcgen], and Re-ARC [@hodel2024rearc] address data limitations.

**Test-time compute scaling** has become a major theme in ARC solving. Chain-of-thought prompting [@wei2022chain] showed that eliciting step-by-step reasoning improves performance on complex tasks. @snell2024scaling show that optimally allocating test-time compute can be more effective than scaling model parameters. @akyurek2024surprising demonstrate that updating model parameters at test time yields strong gains on ARC-like reasoning. Self-consistency [@wang2022selfconsistency] demonstrated that sampling multiple reasoning paths and selecting the most consistent answer outperforms single-trace inference. Tree of Thoughts [@yao2023tree] and Graph of Thoughts [@besta2024graph] reframe inference as explicit search over intermediate reasoning units.

**Tool-augmented reasoning** --- ReAct [@yao2022react], PAL [@gao2023pal], Toolformer [@schick2023toolformer] --- is directly relevant to ARC, where code synthesis serves both as a hypothesis generator and as a source of structured intermediate artifacts for downstream selection. Iterative refinement methods (Self-Refine [@madaan2023selfrefine], Reflexion [@shinn2023reflexion]) trade tokens for improved outputs but risk anchoring to early hypotheses.

**LLM-as-a-judge** paradigms [@zheng2023judging] delegate selection to LLM evaluators, showing strong correlation with human preferences alongside systematic biases (position, verbosity). For ARC in particular, selection is unusually difficult because many hypotheses fit the demonstrations yet fail on the test instance.

### Positioning of this work

This approach combines three trends: (1) **hypothesis generation as explicit search** across *multiple reasoning modalities* rather than a single representation, (2) **tool-mediated reasoning** producing richer intermediate artifacts for downstream selection, and (3) **judge-based selection** adapted for ARC's specific challenge of judging *generalization under underspecification*. The distinctive element is combining heterogeneous candidate generators with context-preserving comparison over full traces, rather than scalar scoring or consensus compression.

