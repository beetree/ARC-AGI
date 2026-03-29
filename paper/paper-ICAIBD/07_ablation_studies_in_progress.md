## Ablation Studies

Rigorous component attribution would require multiple full-pipeline reruns, each costing about $2,400 in API spend (Table V). This section therefore relies on **post-hoc analysis of the single public evaluation run**, which is informative but cannot capture all interaction effects. Unless otherwise stated, "solved" refers to pass@2 at the **test-instance** level on the 167-instance public evaluation split.

### Measured Ablations

\begin{table}[htbp]
\caption{Measured judge ablations on the public evaluation run.}
\begin{center}
\scriptsize
\setlength{\tabcolsep}{2pt}
\renewcommand{\arraystretch}{1.1}
\begin{tabular}{|>{\raggedright\arraybackslash}p{0.17\columnwidth}|>{\raggedright\arraybackslash}p{0.43\columnwidth}|>{\raggedright\arraybackslash}p{0.16\columnwidth}|}
\hline
\textbf{Component} & \textbf{Ablation / control condition} & \textbf{Net uplift (solved instances)} \\
\hline
Holistic selection & Holistic judge vs majority-vote baseline (synthesis disabled in both) & +7 (all minority recoveries) \\
Judge synthesis & Synthesis enabled vs disabled (holistic selection held fixed) & +1 \\
\hline
\end{tabular}
\end{center}
\end{table}

Reported deltas are net solved-instance uplifts attributable to the indicated component.

The +7 holistic-selection uplift consists entirely of minority recoveries where the correct answer was not the most frequent candidate output. Synthesis adds +1 more instance by recombining complementary partial insights when no candidate is fully correct. While the measured synthesis count is small in this run, the mechanism is most relevant on harder tasks where no single candidate fully solves the problem.

### Cost Attribution

\begin{table}[htbp]
\caption{Cost attribution per test instance on the public evaluation run (n = 167).}
\begin{center}
\footnotesize
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Phase} & \textbf{Total (\$)} & \textbf{Avg \$/instance} & \textbf{\% of total} \\
\hline
Candidate generation & 2081.37 & 12.46 & 87.1\% \\
Judging & 308.91 & 1.85 & 12.9\% \\
\hline
\textbf{Total} & \textbf{2390.28} & \textbf{14.31} & \textbf{100\%} \\
\hline
\end{tabular}
\end{center}
\end{table}

\begin{table}[htbp]
\caption{Candidate generation cost by modality family.}
\begin{center}
\scriptsize
\setlength{\tabcolsep}{2pt}
\renewcommand{\arraystretch}{1.1}
\begin{tabular}{|>{\raggedright\arraybackslash}p{0.28\columnwidth}|>{\centering\arraybackslash}p{0.12\columnwidth}|>{\centering\arraybackslash}p{0.16\columnwidth}|>{\centering\arraybackslash}p{0.18\columnwidth}|}
\hline
\textbf{Modality family} & \textbf{Total (\$)} & \textbf{Avg \$/instance} & \textbf{\% of generation cost} \\
\hline
Text (incl. deep think) & 597.70 & 3.58 & 28.7\% \\
Image & 467.10 & 2.80 & 22.5\% \\
Code & 1016.56 & 6.09 & 48.9\% \\
\hline
\end{tabular}
\end{center}
\end{table}

Candidate generation dominates at 87% of spend; code is the most expensive family because of iterative sandbox execution. Judging contributes +7 solved instances from holistic selection and +1 from synthesis at only 13% of total cost.

\begin{table}[htbp]
\caption{Post-hoc marginal oracle coverage on the complete-coverage subset (n = 130).}
\begin{center}
\scriptsize
\setlength{\tabcolsep}{2pt}
\renewcommand{\arraystretch}{1.1}
\begin{tabular}{|>{\raggedright\arraybackslash}p{0.17\columnwidth}|>{\raggedright\arraybackslash}p{0.22\columnwidth}|>{\raggedright\arraybackslash}p{0.21\columnwidth}|>{\raggedright\arraybackslash}p{0.18\columnwidth}|}
\hline
\textbf{Candidate budget} & \textbf{Families included} & \textbf{Oracle-solvable instances} & \textbf{Marginal gain vs previous stage} \\
\hline
8 candidates & Text only & 84 / 130 (64.6\%) & -- \\
18 candidates & Text + Image & 101 / 130 (77.7\%) & +17 \\
29 candidates & Text + Image + Code & 108 / 130 (83.1\%) & +7 \\
\hline
\end{tabular}
\end{center}
\end{table}

This oracle-only analysis uses the 130 instances where all 29 candidates were produced. It estimates lower-bound generation gains under a hypothetical staged family expansion; judges are not re-run on reduced pools.

The main takeaway is modest but useful: on the hard-instance subset, additional candidate families are **not equally valuable**, and staged expansion can recover meaningful oracle coverage beyond a cheap base. Because this is a post-hoc oracle analysis under one ordering, it should be read only as evidence for **modality-aware adaptive routing**. This complements the early-stopping result: 37/167 instances terminated after the initial 8-candidate probe, and 36 of those 37 were solved correctly.

### Unperformed Ablations

The following ablations would strengthen the paper's claims but have not been run due to cost constraints (~$2,400 per full run):

- **End-to-end modality removal:** run the full pipeline with one modality family removed and re-run judging on the reduced candidate pool, capturing interaction effects not visible in oracle-level analysis.
- **Matched candidate budget scaling:** rerun the full pipeline at multiple budget points and with multiple routing orders to estimate marginal returns under controlled conditions. Table VII provides only a post-hoc oracle lower bound, not a full end-to-end scaling curve.
- **Trace content ablation:** compare judge accuracy with full reasoning traces vs output grids only, to quantify whether trace content actually helps selection or whether the judge primarily relies on output comparison.

---
