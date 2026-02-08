# Cost Breakdown

- Task:Test count: 167

## Phase Breakdown (Average $/Task)

_Note: "per task" here means per Task:Test pair._

| Phase | Total ($) | Avg per Task ($) |
| --- | --- | --- |
| Candidate generation | 2081.3654 | 12.4633 |
| Judging | 308.9107 | 1.8498 |
| **Total** | 2390.2761 | 14.3130 |

## Candidate Generation Breakdown (Average $/Task)

| Category | Total ($) | Avg per Task ($) |
| --- | --- | --- |
| Text | 597.7048 | 3.5791 |
| Image | 467.1037 | 2.7970 |
| Code | 1016.5569 | 6.0872 |

Notes:
- Candidate generation costs are summed across all non-finish steps (steps 1/3/5), excluding steps 2 and 4.
- Judging costs are summed from `selection_details.judges` in the finish logs (including council runs).
- Deep/Thinking variants are included in **Text**.
