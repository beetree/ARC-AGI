## Ablation Studies

A rigorous component attribution would require multiple full-pipeline runs with individual components removed or substituted. Each such run costs approximately $2,400 in API spend (Table 6), making extensive ablation prohibitively expensive. This paper therefore relies primarily on **post-hoc analysis of the single public evaluation run**, extracting what can be measured from the existing candidate pool rather than running dedicated ablation experiments. This approach has clear limitations: it cannot capture interaction effects between components, and some comparisons (e.g., end-to-end modality removal) require fresh runs that have not been performed. Unless otherwise stated, "solved" refers to pass@2 at the **test-instance** level on the public evaluation split (167 instances).

### Measured Ablations

**Table 5. Measured judge ablations on the public evaluation run.** Reported deltas are net solved-instance uplifts attributable to the indicated component.

| Component | Ablation / control condition | Net uplift (solved instances) |
| --- | --- | --- |
| Holistic selection | Holistic judge vs majority-vote baseline (synthesis disabled in both) | +7 (all minority recoveries) |
| Judge synthesis | Synthesis enabled vs disabled (holistic selection held fixed) | +1 |

The +7 holistic selection uplift directly validates the anti-consistency design: all 7 gains are minority recoveries where the correct answer was not the most frequent candidate output, and the judge's ability to read and compare full reasoning traces -- rather than simply tallying outputs -- was the deciding factor. Synthesis yielded +1 instance where no candidate was correct but the judge recombined partial insights from complementary failures into a novel correct output. While the measured synthesis uplift is small on this run, the mechanism has particular potential on harder tasks where no single candidate is fully correct but multiple candidates contain complementary partial insights.

### Cost Attribution

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

Candidate generation dominates at 87% of spend; code is the most expensive family (49% of generation cost) due to iterative sandbox execution. Judging contributes +7 solved instances (holistic selection) and +1 (synthesis) at only 13% of total cost, making it highly cost-effective.

### Unperformed Ablations

The following ablations would strengthen the paper's claims but have not been run due to cost constraints (~$2,400 per full run). They are listed as transparency about what remains unknown and as a roadmap for future work:

- **End-to-end modality removal:** run the full pipeline with one modality family removed and re-run judging on the reduced candidate pool, capturing interaction effects not visible in oracle-level analysis.
- **Candidate budget scaling:** sweep the number of candidates per modality to estimate marginal returns and identify diminishing-returns regimes.
- **Trace content ablation:** compare judge accuracy with full reasoning traces vs output grids only, to quantify whether trace content actually helps selection or whether the judge primarily relies on output comparison.

---
