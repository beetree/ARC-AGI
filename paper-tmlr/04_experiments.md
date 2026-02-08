## Experiments and Results

### Evaluation setup

ARC-AGI-2 provides multiple evaluation sets evaluated under **pass@2** [@arcprize2024report]. ARC Prize Verified results are reported on the **semi-private evaluation set** via an official verification process. The solver was iteratively designed using the training set and public evaluation set; the semi-private evaluation was run on held-out tasks unseen during development. The same system also achieved 94.5% on ARC-AGI-1's semi-private evaluation with no ARC-AGI-1 exposure during design.^[ARC-AGI-1 result verified via the ARC Prize evaluation infrastructure: https://arcprize.org/leaderboard]

**Metrics.** (i) **Accuracy (pass@2)**: the mean per-task solve rate, where each task's rate is the fraction of its test instances answered correctly within two guesses. (ii) **Cost per task**: total runtime API cost divided by number of tasks.

### Headline results

The solver was submitted on December 15, 2025, with results announced February 3, 2026.

- **Semi-private (official):** 72.9% at $38.99/task.
- **Public eval (self-measured):** 76.11% at $19.69/task.

| AI System | ARC-AGI-2 | Cost/Task |
| --- | --- | --- |
| Human Panel | 100.00% | $17.00 |
| This paper | 72.90% | $38.99 |
| This paper (public eval) | 76.11% | $19.69 |
| GPT-5.2 Pro (High) | 54.20% | $15.72 |
| Gemini 3 Pro (Refine.) | 54.00% | $30.57 |
| GPT-5.2 (X-High) | 52.90% | $1.90 |
| Gemini 3 Deep Think | 45.10% | $77.16 |

: Leaderboard snapshot and reference systems. Semi-private results are from the ARC Prize Verified leaderboard at the time of announcement.

At the time of submission, this was the **highest score on the ARC-AGI-2 Verified leaderboard**, exceeding the next-best entry (GPT-5.2 Pro at 54.2%) by +18.7 percentage points. This indicates that modality-driven candidate generation combined with long-context judging can substantially move the frontier beyond what individual commercial systems achieve. The ~3 pp gap between public (76.11%) and semi-private (72.9%) likely reflects several compounding factors: natural generalization loss to held-out tasks, the ZDR API constraint disabling tool calls (forcing one-shot code generation), API instability during the semi-private run (84% GPT-5.2 failure rate reducing candidate coverage), and potentially fewer early-stopping triggers on harder tasks (reducing the cost savings that lower the per-task average on easier distributions).

**Temporal nature of results.** The ARC-AGI-2 leaderboard is evolving rapidly. Foundation models are improving at a pace where single-model performance can increase substantially between model generations. The contribution of this paper is the **architectural pattern** --- modality-driven search paired with context-preserving selection --- rather than the specific accuracy numbers, which are a product of the models available at the time of submission.

### Efficiency

- **Semi-private:** $38.99/task at 72.9%; **Public eval:** $19.69/task at 76.11%.
- At $19.69/task, the solver is comparable to GPT-5.2 Pro ($15.72) while achieving +21.9 pp accuracy (76.11% vs. 54.2%), and is cheaper and substantially more accurate than Gemini 3 Pro ($30.57 at 54.0%).
- The 2x cost difference between semi-private and public runs is primarily caused by API-level unreliability during the semi-private run: only 2,216 of 14,106 GPT-5.2 API attempts succeeded.

### Modality complementarity (public eval)

The public evaluation split contains 120 tasks with 167 test instances. Of these, the system solves **128/167 = 76.65%** at the instance level. The candidate pool contains at least one correct output for **144/167 = 86.23%** of instances (candidate-oracle accuracy). The 39 unsolved instances decompose into 21 generation failures (no correct candidate exists), 17 selection failures (correct candidate exists but is not selected), and 1 early-stopping failure.

![Methodology matrix over public evaluation instances. Green = correct; red = incorrect; white = not produced.](figures/methodology_matrix.png)

The solver uses adaptive early stopping: 37 instances were stopped after 8 candidates, with **36/37 solved correctly** (97.3%). To avoid conflating uniqueness with conditional execution, the modality analysis below uses the 130 instances with complete candidate coverage (29/29 candidates).

| | Text | Image | Code |
| --- | --- | --- | --- |
| Text | NA | 13 | 7 |
| Image | 17 | NA | 11 |
| Code | 18 | 18 | NA |

: Pairwise non-overlap between modality families (n = 130). Each cell reads "row solves, column does not." The table is not symmetric.

| Family | Count |
| --- | --- |
| Text only | 2 |
| Image only | 6 |
| Code only | 7 |

: Exclusive coverage (n = 130).

Tables 2--3 indicate substantial complementarity: each family covers instances that others miss. Instance-level heterogeneity is pronounced --- some tasks are solved reliably by one family while being largely unsolved by others (see the appendix for additional examples).

### Judging and synthesis

**Judge-based selection** yields a net uplift of **+7** instances over a majority-vote baseline. All 7 are **minority recoveries** --- cases where the correct answer was not the majority output. This validates the "anti-consistency" motivation: on these tasks, the majority cluster was wrong, and the judge's trace-level reasoning was the deciding factor (see the appendix for a detailed example).

**Judge synthesis** was invoked 17 times total across all three judges, yielding **+1** additional solved instance --- a task where none of the 29 candidates produced a correct output, but the judge recombined partial insights from multiple flawed candidates to produce a novel correct output (see the appendix for the judge's synthesis rationale).

### Failure analysis

Of the 39 unsolved instances (full task lists in the appendix):

- **21 generation failures** tend to require long chains of dependent reasoning steps where models collapse or shortcut the chain rather than faithfully executing all steps.
- **17 selection failures** often involve test instances that introduce a new mechanic not fully disambiguated by training examples, creating genuine ambiguity that the judge resolves incorrectly by favoring the majority interpretation.
- **1 early-stopping failure** (`dbff022c:1`) is a case of extreme groupthink where all 8 early candidates converge on the same wrong interpretation.

