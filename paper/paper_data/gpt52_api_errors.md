# GPT-5.2 API Errors

- Dataset: `timing_breakdown` entries in non-finish steps (1/3/5) with model matching `gpt-5.2`.
- Each timing_breakdown entry represents a single request attempt (including retries).

| Metric | Count |
| --- | --- |
| Total attempts | 14106 |
| Success | 2216 |
| Failed | 11890 |

## By Error Class (logs_parser classification)

| Class | Count |
| --- | --- |
| Max token | 244 |
| Timeout | 1185 |
| Server error | 206 |
| 403 | 54 |
| Rate limit | 10152 |
| Network | 0 |
| Connection | 0 |
| Content filter | 0 |
| Other | 49 |

