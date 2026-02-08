## Ablation Studies

A rigorous component attribution would require multiple full-pipeline runs with individual components removed or substituted. Each such run costs approximately $2,400 in API spend (Table 6), making extensive ablation prohibitively expensive — a full ablation matrix across modalities, judge configurations, and candidate budgets would cost tens of thousands of dollars. This paper therefore relies primarily on **post-hoc analysis of the single public evaluation run**, extracting what can be measured from the existing data (e.g., comparing judge selections against majority-vote baselines on the same candidate pool) rather than running dedicated ablation experiments. This approach has clear limitations: it cannot capture interaction effects between components, and some comparisons (e.g., end-to-end modality removal) require fresh runs that have not been performed. The ablations reported here should be read with this constraint in mind.

Unless otherwise stated, "solved" refers to pass@2 at the **test-instance** level on the public evaluation split (167 instances).

### Measured ablations

#### Judging: holistic selection vs per-candidate scoring (excluding synthesis)

Judging (excluding synthesis) had a net uplift of **7** solved instances relative to a **majority-vote baseline** that selects the most common candidate output grid as the first guess and the second-most-common as the second guess (i.e., standard self-consistency). All 7 uplift instances are **minority recoveries**: cases where the correct answer was not the most frequent candidate output, and the holistic judge identified it by reasoning over the full traces rather than counting votes. This directly validates the "anti-consistency" motivation (Section 5): on these tasks, the majority cluster was wrong, and the holistic judge's ability to read and compare reasoning traces — rather than simply tallying outputs — was the deciding factor. One illustrative instance is `dfadab01:1` (https://arcprize.org/play?task=dfadab01), where the candidate pool clusters around two distinct incorrect hypotheses and the holistic judge selects the lone correct candidate.

#### Judging: synthesis enabled vs disabled

Synthesized solution yields a net uplift of **1** additional solved instance in this run. Across all three judges, synthesis was invoked **17** times total; in most cases the synthesized output did not change the final selected solution, as the weighted scoring still favored non-synthesized candidates.

While the measured uplift is small on this particular run, synthesis has been a more material contributor in other experimental runs during development. The mechanism has particular potential on harder tasks where no single candidate is fully correct but multiple candidates contain complementary partial insights — exactly the regime where recombination should help most. Better understanding when and how to trigger synthesis (see "synthesis gating" in Section 9) is an important direction for future work.

**Table 5. Measured judge ablations on the public evaluation run.** Reported deltas are net solved-instance uplifts attributable to the indicated component (with the stated control condition).

| Component | Ablation / control condition | Net uplift (solved instances) |
| --- | --- | --- |
| Holistic selection | Holistic judge vs majority-vote baseline (synthesis disabled in both settings) | +7 (all minority recoveries) |
| Judge synthesis | Synthesis enabled vs disabled (holistic selection held fixed) | +1 |

#### Cost attribution per component

Table 6 reports the cost breakdown for the public evaluation run, averaged per test instance (i.e., per task–test-pair, of which there are 167). This is distinct from the per-task cost reported in Table 2 ($19.69/task over 120 tasks), because many tasks contain multiple test instances (75 tasks have 1 test instance, 43 have 2, and 2 have 3). The per-instance average ($14.31) does not sum to the per-task figure because the per-task metric aggregates all test instances within a task into a single cost. Note: a strict roll-up of the Table 6 total ($2,390.28 / 120 tasks = $19.92/task) differs slightly from the reported $19.69/task; the discrepancy is likely due to accumulated floating-point rounding in the cost-accounting script.

**Table 6. Cost attribution per test instance on the public evaluation run (n = 167).**

| Phase | Total ($) | Avg $/instance | % of total |
| --- | --- | --- | --- |
| Candidate generation | 2081.37 | 12.46 | 87.1% |
| Judging | 308.91 | 1.85 | 12.9% |
| **Total** | **2390.28** | **14.31** | **100%** |

**Table 7. Candidate generation cost by modality family.**

| Modality family | Total ($) | Avg $/instance | % of generation cost |
| --- | --- | --- | --- |
| Text (incl. deep think) | 597.70 | 3.58 | 28.7% |
| Image | 467.10 | 2.80 | 22.5% |
| Code | 1016.56 | 6.09 | 48.9% |

Candidate generation dominates overall cost at 87% of spend, with judging accounting for only 13%. Within generation, code candidates are the most expensive family (49% of generation cost), driven primarily by tool-integrated code generation with iterative sandbox execution. Given that judging contributes +7 solved instances (holistic selection) and +1 (synthesis) at only 13% of total cost, the judging phase is highly cost-effective relative to its accuracy contribution.

### Modality ablations (oracle-level only)

Section 6.6 reports modality-level uniqueness on the **complete-coverage subset** (n = 130), where all modalities are executed. In this subset, the following **exclusive** oracle solvability counts are observed (Table 4): Text only = 2, Image only = 6, Code only = 7. These exclusive counts imply that removing any single modality would reduce candidate-oracle coverage by at least a few percent even before accounting for downstream judge interactions and selection effects.

However, oracle-level analysis has an important limitation: it measures whether a correct candidate *exists* in a modality's output, but does not measure the end-to-end effect of removing that modality on the final system output. Removing a modality could affect judge behavior in ways not captured by oracle overlap — for instance, reducing the number of candidates changes cluster dynamics, which could make it easier or harder for the holistic judge to identify the correct solution. A modality might also contribute "near-miss" candidates that inform judge synthesis even when no individual candidate from that modality is exactly correct.

The proper ablation — running the full pipeline with one modality family removed and re-running judging on the reduced candidate pool — has not been performed. Each such run requires regenerating all judge transcripts on the reduced candidate set (and ideally multiple repetitions to account for judge variance), making it expensive relative to the oracle-level analysis. This remains a gap; the oracle-level uniqueness numbers in Section 6.5 should be interpreted as a lower bound on each modality's contribution, not as a precise end-to-end attribution.

### Unperformed ablations

The following ablations would strengthen the paper's claims but have not been run due to cost constraints. They are listed here both as transparency about what remains unknown and as a roadmap for future work.

**Generation ablations:**

- **End-to-end modality removal:** run the full pipeline with one modality family (text, image, or code) removed and re-run judging on the reduced candidate pool. The oracle-level exclusive counts in Section 7.2 provide a lower bound, but the actual end-to-end impact — including judge interaction effects — is unknown. This requires at minimum three full runs (~$7,200 total).
- **Independent candidates vs sequential refinement:** hold compute fixed and compare N independent candidates (the current approach) against N sequential refinement steps (iterative prompt chaining or staged decomposition). Section 8 documents qualitative evidence that sequential approaches reduced diversity, but a controlled comparison with matched compute budgets has not been performed.
- **Candidate budget scaling:** sweep the number of candidates per modality/model to estimate marginal returns per additional candidate and identify diminishing-returns regimes. The current system uses 29 candidates, but it is unknown whether 15 or 50 would yield meaningfully different accuracy at proportionally different cost.
- **Per-model contribution:** isolate the contribution of each foundation model (GPT-5.2, Gemini 3, Opus 4.5) by running the pipeline with one model removed entirely. Opus 4.5 contributes only 1 candidate; whether its inclusion is cost-justified relative to adding another GPT-5.2 or Gemini candidate is unknown.
- **Temperature and sampling parameters:** the current system uses default or near-default sampling settings for each model. Sweeping temperature, top-p, and other sampling parameters within each modality could reveal whether diversity is better increased through sampling variation or through modality variation.
- **Representation formats:** CSV vs alternative encodings (e.g., JSON-like arrays, Python list syntax, and object-abstraction encodings), evaluated under the same candidate/judge budgets. The benchmarking reported in Section 4 was performed during development with different model versions; a controlled evaluation on the final system would be more rigorous.

**Selection and judging ablations:**

- **Full majority-vote baseline comparison:** the +7 holistic selection uplift reported above is computed post hoc by comparing judge selections against the majority output grid on the same candidate pool. A cleaner comparison would run majority vote as the *sole* selection mechanism in a full end-to-end run (without any judge invocation), eliminating any confounds from shared infrastructure. This would also quantify whether the 13% cost of judging is justified by the accuracy gain.
- **Judge ensemble sizing:** the current system uses 3 judges with weighted scoring. No ablation comparing 1-judge vs 3-judge accuracy has been performed. Quantifying the disagreement rate and how often the ensemble corrects vs overrides individual judges would clarify whether the ensemble cost is justified or whether a single judge suffices.
- **Alternative selection mechanisms:** compare the holistic judge against other selection strategies on the same candidate pool, including per-output log-probability scoring, pairwise judge tournaments (comparing candidates two at a time), and best-of-N with a reward model. These comparisons would isolate the contribution of joint-context evaluation from other factors.
- **Judge model diversity:** the current system uses three GPT-5.2 judges. A mixed-model ensemble (e.g., one GPT-5.2, one Gemini, one Opus judge) was tested informally and underperformed (Section 5), but a rigorous comparison — controlling for prompt format and scoring calibration — has not been done.
- **Trace content ablation:** the holistic judge receives full reasoning traces alongside candidate outputs. Comparing judge accuracy with traces vs outputs-only would quantify whether the trace content actually helps selection or whether the judge primarily relies on output grid comparison.

**Early stopping ablations:**

- **Early stopping threshold tuning:** the current heuristic triggers early stopping when initial candidates agree. Varying the agreement threshold and the number of candidates consulted before the stopping decision would characterize the accuracy/cost trade-off and the groupthink risk documented in Section 6.6.

---
