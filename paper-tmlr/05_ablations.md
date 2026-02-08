## Ablation Studies

Each full-pipeline run costs approximately $2,400 in API spend (Table 5), making extensive ablation prohibitively expensive. This paper relies primarily on **post-hoc analysis of the single public evaluation run**, extracting what can be measured from existing data rather than running dedicated ablation experiments. This approach cannot capture interaction effects between components; the ablations reported here should be read with this constraint in mind.

### Measured ablations

| Component | Ablation / control | Net uplift (instances) |
| --- | --- | --- |
| Holistic selection | vs. majority-vote baseline | +7 (all minority recoveries) |
| Judge synthesis | Enabled vs. disabled | +1 |

: Measured judge ablations on the public evaluation run.

The +7 holistic selection uplift comes entirely from minority recoveries --- instances where the correct answer was not the most frequent candidate output. The +1 synthesis uplift comes from a task where no single candidate was correct, but the judge recombined partial insights.

### Cost attribution

| Phase | Total ($) | Avg $/instance | % of total |
| --- | --- | --- | --- |
| Candidate generation | 2081.37 | 12.46 | 87.1% |
| Judging | 308.91 | 1.85 | 12.9% |
| **Total** | **2390.28** | **14.31** | **100%** |

: Cost attribution per test instance (n = 167).^[A strict roll-up of $2,390.28 / 120 tasks = $19.92/task differs slightly from the reported $19.69/task; the discrepancy is due to accumulated floating-point rounding in the cost-accounting script.]

Candidate generation dominates overall cost at 87% of spend. Given that judging contributes +7 solved instances (holistic selection) and +1 (synthesis) at only 13% of total cost, the judging phase is highly cost-effective relative to its accuracy contribution. A per-modality cost breakdown is provided in the appendix.

### Modality ablations (oracle-level only)

On the complete-coverage subset (n = 130), exclusive oracle solvability counts are: Text only = 2, Image only = 6, Code only = 7 (Table 3). These imply that removing any single modality would reduce candidate-oracle coverage. However, oracle-level analysis does not capture end-to-end effects of modality removal on judge behavior. The proper ablation --- running the full pipeline with one modality family removed --- has not been performed; the oracle-level numbers should be interpreted as a lower bound on each modality's contribution.

### Unperformed ablations

A detailed list of ablations that would strengthen the paper's claims --- including end-to-end modality removal, candidate budget scaling, judge ensemble sizing, trace content ablation, and early stopping threshold tuning --- is provided in the appendix. These have not been run due to cost constraints (~$7,200+ for the minimum set).

