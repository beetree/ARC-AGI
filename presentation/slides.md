---
title: "Modality-Driven Search with Holistic Trace Judging for ARC-AGI-2"
subtitle: "72.9% on ARC Prize Verified --- built on three frontier models, not one"
author: "Johan Land"
date: "ICAIBD 2026"
aspectratio: 169
theme: Madrid
colortheme: seahorse
fontsize: 11pt
header-includes: |
  \setbeamertemplate{navigation symbols}{}
  \setbeamertemplate{footline}{}
---

# ARC-AGI-2 --- a brief history, and two example problems

\begin{columns}[c]
\begin{column}{0.32\textwidth}
\textbf{\normalsize History of ARC-AGI}

\smallskip

\scriptsize
\begin{itemize}\setlength\itemsep{0.3em}
\item \textbf{2019} --- ARC-AGI-1 introduced (Chollet)
\item \textbf{2020--2023} --- Program synthesis era (Icecuber et al.); top scores creep up to $\sim$20\% on ARC-AGI-1
\item \textbf{Dec 2024} --- OpenAI o3 saturates ARC-AGI-1: $\sim$76\% at \$200/task
\item \textbf{2025} --- ARC-AGI-2 launches: harder + cost-weighted; top frontier models $\sim$50\%
\item \textbf{Dec 2025} --- \textbf{This work submitted: 72.9\% on ARC-AGI-2}, first verified >70\%
\item \textbf{2026} --- Frontier models leapfrog to $\sim$80\%+ on ARC-AGI-2 (GPT-5.5, Gemini 3 Deep Think); ARC-AGI-3 launched (top scores still <1\%)
\end{itemize}
\end{column}
\begin{column}{0.68\textwidth}
\centering
\includegraphics[width=\linewidth,height=0.92\textheight,keepaspectratio]{figures/tasks_three_examples.png}
\end{column}
\end{columns}

::: notes
A sampler — three additional ARC-AGI-2 tasks so the audience sees that the benchmark is not one trick. Don't try to solve any of these out loud — that eats too much time. Point at each in turn (~5 seconds each) and characterize them briefly: "shapes colored by a legend," "objects completed or repaired," "objects aligned across backgrounds." Land the punchline: every task has a fresh rule the model has never seen. ~40 seconds total before moving on to the formal definition.
:::

---

# What is ARC-AGI-2? --- format and evaluation {.fragile}

\begin{columns}[T]
\begin{column}{0.52\textwidth}
\textbf{What the model sees (JSON):}

\scriptsize
\begin{verbatim}
{
  "train": [
    {"input":  [[0,1,0],[1,0,1],[0,1,0]],
     "output": [[1,0,1],[0,1,0],[1,0,1]]},
    {"input":  [...], "output": [...]},
    ...
  ],
  "test": [
    {"input":  [[1,0,1],[0,1,0],[1,0,1]]}
  ]
}
\end{verbatim}

\normalsize
\textbf{What the model returns:}

\scriptsize
\begin{verbatim}
[[0,1,0],[1,0,1],[0,1,0]]
\end{verbatim}
\end{column}
\begin{column}{0.48\textwidth}
\footnotesize
\begin{itemize}\setlength\itemsep{0.7em}
\item \textbf{pass@2:} the model is allowed \emph{two guesses} per test input --- it scores if either matches the ground truth exactly
\item \textbf{Public eval} for development; the \textbf{private eval} is the official scoring --- run end-to-end by the ARC Prize foundation on tasks the developer never sees
\item \textbf{Cost per task} (USD) is graded alongside accuracy --- efficiency is a first-class metric
\end{itemize}
\end{column}
\end{columns}

::: notes
This slide formalizes the protocol. The JSON example shows the audience exactly what the model receives — a list of train pairs and a test input — and what it returns (a grid). Don't read the JSON line-by-line; just point at it. The right column carries the load: pass@2, the public-vs-private split, and cost-as-metric. Emphasize that the official scoring is done end-to-end by the foundation on tasks the developer never sees — this is what makes the benchmark hard to game.
:::

---

# The headline result

\begin{center}
\begin{tabular}{lcc}
\hline
\textbf{System} & \textbf{ARC-AGI-2} & \textbf{Cost/Task} \\
\hline
Human Panel & 100.0\% & \$17.00 \\
\textbf{This work (semi-private)} & \textbf{72.9\%} & \$38.99 \\
\textbf{This work (public eval)} & \textbf{76.1\%} & \$19.69 \\
GPT-5.2 Pro (High) & 54.2\% & \$15.72 \\
Gemini 3 Pro (Refine.) & 54.0\% & \$30.57 \\
Opus 4.5 (Thinking, 64K) & 37.6\% & \$2.40 \\
\hline
\end{tabular}
\end{center}

\bigskip

\centering
**+18.7 points over the strongest standalone frontier model**

::: notes
Anchor early — audience now knows there's a real result behind the method talk. Be honest about cost: this spends more than a single model call. The contribution is the architectural pattern, not the absolute leaderboard number — those move weekly. Pivot to the next slide with the question: how does an orchestration system beat a frontier model by 18 points?
:::

---

# The real problem is selection, not generation

\Large
- LLMs produce fluent, internally coherent traces --- and are still **confidently wrong**
- On hard tasks, models **cluster around the same wrong interpretation**
- $\Rightarrow$ majority voting / self-consistency *amplifies* the error
- The hard problem isn't generating a correct candidate
- It's **recognizing** one when most others disagree

::: notes
This is the reframe that unlocks the whole architecture. If they take only one thing home before the method, take this one. Concrete number to drop: of our 39 failure instances, only 21 are genuine generation failures — 17 are *selection* failures where a correct candidate exists in the pool but is not chosen. Set up the next slide: if the correct answer is rare, we need to (a) make sure we generate it, and (b) recognize it without majority-counting.
:::

---

# Core idea: modalities as search operators

\begin{columns}[t]
\begin{column}{0.32\textwidth}
\centering
\textbf{TEXT}\\[0.3em]
\footnotesize Model reads the grid as numbers / strings
\end{column}
\begin{column}{0.32\textwidth}
\centering
\textbf{IMAGE}\\[0.3em]
\footnotesize Model sees a rendered PNG of the grid
\end{column}
\begin{column}{0.32\textwidth}
\centering
\textbf{CODE}\\[0.3em]
\footnotesize Model writes Python to transform the grid
\end{column}
\end{columns}

\bigskip
\bigskip

- Same task, three representations $\rightarrow$ three different hypothesis distributions
- Each modality solves tasks the others miss
- Generate **independently** --- don't pool prompts, don't share scaffolding
- Diversity at the *representation* level, not just temperature

::: notes
This is the slide the audience should remember. Slow down. Use the word "operator" deliberately — frame it like classic AI search: each modality expands a different part of the hypothesis space. Concrete intuition: a model reading grids as numbers may notice arithmetic patterns vision misses; a code-writing pass forces a constructive rule the others can leave implicit. Promise the demo on slide 8.
:::

---

# Pipeline overview

\begin{columns}
\begin{column}{0.45\textwidth}
\centering
\includegraphics[width=\linewidth,height=0.78\textheight,keepaspectratio]{figures/pipeline.png}
\end{column}
\begin{column}{0.55\textwidth}
\textbf{Generate broadly} $\rightarrow$ \textbf{judge holistically} $\rightarrow$ \textbf{vote weighted}

\smallskip

\footnotesize
\begin{itemize}
\item Up to 29 candidates across Text / Image / Code, 3 frontier models
\item 3 parallel judges read \emph{all} traces in one long-context prompt
\item Adaptive early-stop: 37/167 stopped after first probe; \textbf{36 correct (97\%)}
\end{itemize}
\end{column}
\end{columns}

::: notes
One pass through the diagram, max 50 seconds. Audience just needs the shape. Highlight: judges see *full reasoning traces*, not just final answers — this is what enables minority recovery. Mention early-stop to pre-empt the obvious cost objection.
:::

---

# Candidate generation in practice

\Large

- **3 models:** GPT-5.2 (x-high), Gemini 3 Preview (high), Claude Opus 4.5 (long-context)
- **3 modality families:** Text, Image, Code
- **29 candidates per task** across families × configurations
- **Deliberately minimal prompts** in every lane *(see slide 10)*
- Code candidates use a sandbox REPL for iterative debugging

::: notes
Don't list every configuration — the point is the structure: three families crossed with three models. The "minimal prompts" bullet is a callback you'll cash in on the negative-results slide.
:::

---

# Holistic judging vs. majority voting

\Large

- Concatenate all 29 reasoning traces into one long-context judge prompt
- Each judge picks top-2 candidates *and* explains why other clusters are wrong
- Weighted vote across 3 judges $\rightarrow$ pass@2 guesses

\bigskip

\centering
\Large
**Net uplift vs. majority-vote baseline: +7 instances**

\normalsize
*All 7 are minority recoveries --- the correct answer wasn't the most common candidate.*

\bigskip
\raggedright
\footnotesize
Plus **+1 synthesis** instance (`21897d95:2`): zero correct candidates --- judge recombined partial insights into a novel correct output.

::: notes
The +7 number is the empirical payoff of the architecture. Say it slowly. The synthesis case is *qualitatively* different — it shows the system can sometimes *construct* a correct answer rather than just *select* one. Rare (n=1) but a proof-of-possibility for compositional repair. If time allows, quote the judge rationale from dfadab01:1: "Some solvers assume a stamp must fit fully. Others assume stamps are clipped at the border…" — shows the judge reasoning about disagreement explicitly.
:::

---

# End-to-end walkthrough: `d35bdbdc`

\centering
\includegraphics[width=0.95\linewidth,height=0.80\textheight,keepaspectratio]{figures/d35bdbdc_1_step_5_common.png}

\raggedright
\footnotesize
From 29 candidates $\rightarrow$ 2 guesses

::: notes
This is the pedagogical heart of the talk. Don't rush. Budget 2:30.

Script:
(0:30) Show the task; let the audience attempt it mentally.
(0:30) Show what TEXT candidates produce — note the dominant (wrong) interpretation.
(0:30) Show what IMAGE candidates produce — note where they diverge from Text.
(0:30) Show what CODE candidates produce — note any structurally different hypothesis.
(0:30) Reveal the judge's reasoning: which cluster it rejected, which minority it elevated, why pass@2 lets it hedge.

If tight on time, drop the IMAGE step and go Text → Code → Judge — the contrast is sharpest there. End with: "This is what 'modalities as search operators' looks like in practice."
:::

---

# Modality complementarity

\begin{columns}
\begin{column}{0.30\textwidth}
\centering
\includegraphics[width=\linewidth,height=0.80\textheight,keepaspectratio]{figures/methodology_matrix.png}
\end{column}
\begin{column}{0.70\textwidth}
\footnotesize
\begin{itemize}
\item Pairwise non-overlap (n=130): Code solves 18 that Text misses; Image solves 13 that Text misses
\item Exclusive solves: \textbf{2 Text-only}, \textbf{6 Image-only}, \textbf{7 Code-only}
\item Modalities are \textbf{not redundant copies} of the same reasoning process
\item Candidate-oracle accuracy: \textbf{86.2\%} (a correct candidate exists for 144/167)
\end{itemize}
\end{column}
\end{columns}

::: notes
The oracle number (86.2%) is the most honest framing of the system's ceiling: it says generation is in good shape and selection is the next frontier. Tie back: of the 39 failures, 17 are selection — that's where the headroom is.
:::

---

# Negative results worth knowing

\Large

**Prescriptive prompting degrades performance**

\normalsize
Structured templates, CoT scaffolding, domain heuristics --- all hurt on the hardest tasks. Mechanism: a *compliance tax on reasoning*.

\bigskip

\Large
**Iterative refinement reduces diversity**

\normalsize
Refining candidates against each other collapses them onto the same wrong cluster --- the exact failure mode we're trying to escape.

\bigskip
\centering
$\Rightarrow$ **Final system: deliberately minimal prompts + independent generation**

::: notes
Most counter-intuitive findings in the paper — audiences love negative results because they save them time. Frame these as design constraints we discovered the hard way: every time we added "helpful" structure, scores dropped on the tasks that mattered.
:::

---

# Takeaways

\Large

1. **Modalities are search operators.**\
   Text, image, code activate different hypothesis distributions --- exploit that.

\medskip

2. **Holistic judging $>$ majority voting.**\
   On hard tasks the truth is a minority hypothesis; let a long-context judge read full traces.

\medskip

3. **Less prompt structure, more representational diversity.**\
   Prescriptive scaffolding suppresses the creative leaps these tasks reward.

\bigskip
\bigskip

\centering
\normalsize
Code: \texttt{github.com/beetree/ARC-AGI} \quad $\bullet$ \quad Paper QR on title slide

::: notes
Close on the three-bullet recap. Then invite questions. If asked about cost, jump to backup slide on cost breakdown. If asked about failure modes, jump to backup slide on failure decomposition. If asked why three judges, jump to the third backup slide.
:::

---

# Backup: cost breakdown

\footnotesize

- **Public-eval cost is the representative number: $19.69/task**
- Semi-private $38.99/task inflated by GPT-5.2 API instability (84% failure rate, 2,216/14,106 attempts succeeded)
- Tool-integrated code generation is the largest line item
- ZDR mode used in semi-private verification disables tool calls $\rightarrow$ both lower accuracy and altered cost profile
- ARC-AGI-1 on the same system: 94.5% at $11.40/task --- easier tasks early-exit cheaply

::: notes
Backup only. Skip unless asked.
:::

---

# Backup: failure decomposition (167 instances)

\Large

- **128 solved (76.6%)**
- 21 generation failures (no correct candidate in pool)
- 1 early-stop failure (`dbff022c:1` --- extreme groupthink on a legend ambiguity)
- 17 **selection** failures (correct candidate exists, judge missed it)
- 1 synthesis success (`21897d95:2`)

\bigskip
\normalsize
*Most future headroom is in selection, not generation.*

::: notes
Backup only. Skip unless asked.
:::

---

# Backup: why three judges?

\Large

- Single judge is biased toward its own prior
- 3 parallel judges + weighted scoring (2 pts first, 1 pt second) hedges *within* the judging step
- Pass@2 format lets the final output also hedge across two interpretations when judges disagree

::: notes
Backup only. Skip unless asked.
:::
