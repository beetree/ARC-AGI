## Experiments and Results

### Evaluation Protocol

ARC-AGI-2 provides public, semi-private, and private evaluation sets, all calibrated and scored under **pass@2** [@arcprize2024report]. ARC Prize Verified results are reported on the semi-private evaluation set via an official verification process and leaderboard. The solver was iteratively developed using the 1,000-task training set and the 120-task public evaluation split; the semi-private evaluation was run on held-out tasks unseen during development, and the ~3 percentage-point gap between public and semi-private scores suggests limited overfitting.

### Headline Results

The solver was submitted to the ARC Prize foundation on December 15, 2025, with official results announced on February 3, 2026. The leaderboard snapshot in Table II reflects the state at the time of announcement.

On the **semi-private evaluation set**, the solver achieves **72.9% solved** at **$38.99/task** -- the highest score on the ARC Prize Verified leaderboard at the time of writing. On the **public evaluation set**, it achieves **76.11% solved** at **$19.69/task** (self-measured). For the per-instance analyses below, the public evaluation split contains 120 task IDs with 167 test instances (75 tasks with 1 test instance, 43 with 2, and 2 with 3).

The ~3 percentage-point gap between public (76.11%) and semi-private (72.9%) likely reflects three factors: (i) natural generalization loss to a held-out task distribution, (ii) the semi-private verification uses OpenAI's zero-data-retention (ZDR) API mode, which disables function/tool calling, and (iii) the semi-private run coincided with a period of known instability in OpenAI's API. Under ZDR, the tool-integrated code generation candidates (Section III-B) were replaced with one-shot code generation without iterative sandbox execution. Code candidates were still produced, but without the iterative debugging loop that makes tool-integrated generation more robust on complex tasks. Since tool-integrated code generation accounts for the bulk of the Code family's cost (Table VI), the ZDR constraint both reduced accuracy and changed the cost profile of the semi-private run relative to the public run.

\begin{table}[htbp]
\caption{Leaderboard snapshot and reference systems.}
\begin{center}
\scriptsize
\setlength{\tabcolsep}{2pt}
\renewcommand{\arraystretch}{1.1}
\begin{tabular}{|>{\raggedright\arraybackslash}p{0.17\columnwidth}|>{\raggedright\arraybackslash}p{0.12\columnwidth}|>{\centering\arraybackslash}p{0.12\columnwidth}|>{\centering\arraybackslash}p{0.12\columnwidth}|>{\raggedright\arraybackslash}p{0.21\columnwidth}|}
\hline
\textbf{AI System} & \textbf{Author} & \textbf{ARC-AGI-2} & \textbf{Cost/Task} & \textbf{Comment} \\
\hline
Human Panel & Human & 100.00\% & \$17.00 & At least two humans out of \textasciitilde400 solved it \\
This paper & Johan Land & 72.90\% & \$38.99 & Semi-private (official) \\
This paper & Johan Land & 76.11\% & \$19.69 & Public eval \\
GPT-5.2 Pro (High) & OpenAI & 54.20\% & \$15.72 & \\
Gemini 3 Pro (Refine.) & Poetiq & 54.00\% & \$30.57 & \\
GPT-5.2 (X-High) & OpenAI & 52.90\% & \$1.90 & \\
Gemini 3 Deep Think (Preview) & Google & 45.10\% & \$77.16 & \\
GPT-5.2 (High) & OpenAI & 43.30\% & \$1.39 & \\
GPT-5.2 Pro (Medium) & OpenAI & 38.50\% & \$8.99 & \\
Opus 4.5 (Thinking, 64K) & Anthropic & 37.60\% & \$2.40 & \\
Gemini 3 Flash Preview (High) & Google & 33.60\% & \$0.23 & \\
\hline
\multicolumn{5}{|p{0.78\columnwidth}|}{\scriptsize Source: \url{https://arcprize.org/leaderboard}. Semi-private results are as reported on the ARC Prize Verified leaderboard at the time of the official results announcement (February 3, 2026); the public-evaluation row is self-measured.} \\
\hline
\end{tabular}
\end{center}
\end{table}

The system achieves +18.7 percentage points over the strongest commercial baselines at higher cost, reflecting additional test-time compute spent on multi-candidate search. The remaining gap to the human panel (100.0% at $17/task) indicates substantial headroom. As the leaderboard evolves rapidly, the contribution is the **architectural pattern** rather than the specific accuracy numbers.

### Efficiency

ARC-AGI-2 explicitly evaluates efficiency [@arcprize2024report]. The roughly 2x cost difference between the semi-private and public runs ($38.99 vs. $19.69) is largely attributable to API-level unreliability: on the public-eval run, only 2,216 of 14,106 GPT-5.2 API attempts succeeded (84% failure rate due to rate limits, timeouts, and server errors). The public-eval cost of $19.69/task is a more representative measure; at this cost, the solver is comparable to GPT-5.2 Pro ($15.72/task) while achieving a +21.9 percentage-point accuracy gain, and is both cheaper and more accurate than Gemini 3 Pro ($30.57/task at 54.0%). A detailed cost breakdown is provided in Section V.

### Modality Contribution

The final modality mix was selected based on both raw solve contribution and diversity contribution (uniquely solved tasks that other modalities fail). GPT dominates code generation, Gemini adds meaningful diversity, and Gemini/GPT image reasoning behave differently enough to be complementary; Opus remains unusually strong for end-to-end text reasoning and is the sole solver for several text-only successes. Over the 167 public-evaluation test instances, the final system solves 128/167 = 76.65% at the instance level (pass@2), while the candidate pool contains at least one correct output for 144/167 = 86.23% (candidate-oracle accuracy). The remaining 39 instances decompose into 21 generation failures where no candidate in the pool is correct (with full 29-candidate coverage), 1 early-stopping failure, and 17 selection failures where at least one correct candidate exists but is not chosen by the judge. Generation failures tend to involve long chains of dependent reasoning steps, while selection failures cluster around tasks where the test case introduces a mechanic not fully disambiguated by training examples. One additional instance (`21897d95:2`) is solved by judge synthesis despite **zero** candidates matching ground truth; this occurs via judge synthesis rather than candidate selection.

![Methodology matrix over public evaluation instances. Green = correct candidate; red = incorrect candidate; white = candidate not produced due to early stopping.](figures/methodology_matrix.png)

### Modality Complementarity (Public Eval)

To quantify complementarity between candidate-generation methodologies, I evaluate each candidate output against ground truth and record a per-instance correctness matrix. To avoid conflating uniqueness with conditional execution (the system uses adaptive early stopping for easy tasks), the analysis is restricted to the 130 instances with complete candidate coverage (all 29 candidates generated).

\begin{table}[htbp]
\caption{Pairwise non-overlap between modality families (n = 130).}
\begin{center}
\footnotesize
\begin{tabular}{|l|c|c|c|}
\hline
 & \textbf{Text} & \textbf{Image} & \textbf{Code} \\
\hline
\textbf{Text} & NA & 13 & 7 \\
\textbf{Image} & 17 & NA & 11 \\
\textbf{Code} & 18 & 18 & NA \\
\hline
\end{tabular}
\end{center}
\end{table}

Each cell reads "row solves, column does not": the entry counts instances with at least one PASS in the row family and zero PASS in the column family. The table is not symmetric.

Each family covers a non-trivial set of instances that are not covered by at least one other family. At the exclusive level, 2 instances are solved only by Text, 6 only by Image, and 7 only by Code. This confirms that modalities function as distinct search operators rather than redundant copies of the same reasoning process, and supports treating each modality as a separate exploration channel in the candidate-generation phase.

### Judging and Synthesis (Public Eval)

Holistic judging (excluding synthesis) yielded a net uplift of **+7 solved instances** relative to a majority-vote baseline that selects the most common candidate output. All 7 are minority recoveries -- cases where the correct answer was not the most frequent candidate output and the holistic judge identified it by reasoning over full traces rather than counting votes. This directly validates the anti-consistency motivation: on these tasks the majority cluster was wrong, and the judge's ability to read and compare reasoning traces was the deciding factor. One illustrative case is `dfadab01:1`, where 12 candidates converge on one incorrect output and 8 on another, but the judge identifies the lone correct candidate. The judge rationale shows explicit anti-consistency reasoning:

```text
Most candidate solvers correctly identify the core stamp
mechanic ... The only remaining ambiguity is edge handling
(not clearly disambiguated by the training set):
- Some solvers assume a stamp must fit fully.
- Others assume stamps are clipped at the border.
So the two most plausible outputs (same mechanic,
differing only in border handling)
```

Rather than committing both guesses to the majority interpretation, the judge uses the pass@2 format to hedge across the two edge-handling interpretations — reasoning that majority voting cannot perform.

Synthesis -- where the judge produces a novel output not identical to any candidate -- yielded **+1 additional solved instance** (`21897d95:2`), a task where none of the 29 candidates were correct but the judge recombined partial insights (correct room parsing from some candidates, correct arrow semantics from others) into a novel correct output.

Although the measured count is only one instance, this case is qualitatively different from the +7 minority recoveries above. Holistic selection succeeds by identifying a rare correct candidate that already exists in the pool; synthesis succeeds when **no correct candidate exists at all**, but complementary partial truths are distributed across multiple failed candidates. In that sense, `21897d95:2` should be read as a proof-of-possibility for **compositional repair**: the architecture can sometimes do more than rank hypotheses and can instead construct a correct answer by recombining partial insights.

---
