---
title: "Modality-Driven Search with Holistic Trace Judging for ARC-AGI-2"
subtitle: "72.9% verified result, beating frontier models by ~20%"
author: "Johan Land"
date: "ICAIBD 2026"
aspectratio: 169
theme: Boadilla
colortheme: dolphin
fontsize: 11pt
header-includes: |
  \usepackage{fontspec}
  \setsansfont{Helvetica}
  \setmonofont[Scale=0.92]{Menlo}
  \renewcommand{\familydefault}{\sfdefault}
  \usefonttheme{professionalfonts}
  \usepackage{xcolor}
  \usepackage{framed}
  \definecolor{accent}{HTML}{0F3D7C}
  \definecolor{accentmid}{HTML}{3B6FB0}
  \definecolor{accentlight}{HTML}{E5ECF6}
  \definecolor{successdark}{HTML}{1F6B3F}
  \definecolor{successlight}{HTML}{E0F0E2}
  \definecolor{warnlight}{HTML}{FCE4E4}
  \definecolor{warndark}{HTML}{B33A3A}
  \definecolor{inktext}{HTML}{1A1A1A}
  \colorlet{shadecolor}{accentlight}
  \setbeamercolor{structure}{fg=accent}
  \setbeamercolor{frametitle}{fg=accent,bg=}
  \setbeamercolor{title}{fg=accent}
  \setbeamercolor{subtitle}{fg=accentmid}
  \setbeamercolor{author}{fg=inktext}
  \setbeamercolor{date}{fg=inktext}
  \setbeamercolor{institute}{fg=inktext}
  \setbeamercolor{normal text}{fg=inktext}
  \setbeamercolor{itemize item}{fg=accent}
  \setbeamercolor{itemize subitem}{fg=accentmid}
  \setbeamercolor{enumerate item}{fg=accent}
  \setbeamercolor{block title}{fg=white,bg=accent}
  \setbeamercolor{block body}{bg=accentlight}
  \setbeamertemplate{navigation symbols}{}
  \setbeamertemplate{footline}{}
  \setbeamertemplate{frametitle}{%
    \vspace{0.3em}\hspace{0.6em}{\large\bfseries\color{accent}\insertframetitle}%
    \par\nointerlineskip\vspace{0.1em}%
    \hspace*{0.6em}{\color{accent}\rule{0.97\paperwidth}{0.4pt}}%
    \vspace{-0.4em}}
  \makeatletter
  \setbeamertemplate{title page}{%
    \vbox{}\vfill
    \begingroup
      \centering
      {\color{accent}\rule{0.3\paperwidth}{2pt}}\par
      \vspace{1.2em}
      {\usebeamerfont{title}\usebeamercolor[fg]{title}\bfseries\inserttitle\par}%
      \ifx\insertsubtitle\@empty\else
        \vspace{0.8em}
        {\usebeamerfont{subtitle}\usebeamercolor[fg]{subtitle}\insertsubtitle\par}%
      \fi
      \vspace{2.2em}
      {\usebeamerfont{author}\usebeamercolor[fg]{author}\insertauthor\par}%
      \vspace{0.4em}
      {\usebeamerfont{date}\usebeamercolor[fg]{date}\insertdate\par}%
      \vspace{1.2em}
      {\color{accent}\rule{0.3\paperwidth}{2pt}}\par
    \endgroup
    \vfill}
  \makeatother
---

# ARC-AGI-2 --- a brief history, and two example problems

\begin{columns}[c]
\begin{column}{0.32\textwidth}
\scriptsize
\begin{itemize}\setlength\itemsep{0em}\setlength\leftmargini{0.8em}\setlength\topsep{0em}\setlength\parskip{0em}
\item \textbf{2019} --- ARC-AGI-1 introduced (Chollet); trivial for humans, impossible for AI at the time
\item \textbf{2020--2023} --- Program synthesis era; top scores reach $\sim$20\% on ARC-AGI-1
\item \textbf{Dec 2024} --- o3 saturates ARC-AGI-1 ($\sim$76\% at \$200/task), but only $\sim$3\% on ARC-AGI-2
\item \textbf{2025} --- Focus shifts to ARC-AGI-2; top scores climb to $\sim$50\% (GPT-5.2, Opus 4.5)
\item \textbf{Dec 2025} --- \textbf{This work: 72.9\% on ARC-AGI-2}, first verified >70\%
\item \textbf{2026} --- Frontier models leapfrog to $\sim$80\%+ (GPT-5.5, Gemini 3.1 Deep Think, Opus 4.7); ARC-AGI-3 launches (<1\%)
\end{itemize}
\end{column}
\begin{column}{0.68\textwidth}
\centering
\includegraphics[width=\linewidth,height=0.82\textheight,keepaspectratio]{figures/tasks_three_examples.png}
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
\begin{shaded}
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
\end{shaded}

\normalsize
\textbf{What the model returns:}

\scriptsize
\begin{shaded}
\begin{verbatim}
[[0,1,0],[1,0,1],[0,1,0]]
\end{verbatim}
\end{shaded}
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
\textbf{This work (private)} & \textbf{72.9\%} & \$38.99 \\
\textbf{This work (public eval)} & \textbf{76.1\%} & \$19.69 \\
GPT-5.2 Pro (High) & 54.2\% & \$15.72 \\
Opus 4.5 (Thinking, 64K) & 37.6\% & \$2.40 \\
Gemini 3 Pro & 31.1\% & \$0.81 \\
\hline
\end{tabular}
\end{center}

\bigskip

\begin{center}
\fcolorbox{accent}{accentlight}{\parbox{0.7\linewidth}{\centering\large\bfseries\color{accent}+18.7 points over the strongest standalone frontier model}}
\end{center}

::: notes
Anchor early — audience now knows there's a real result behind the method talk. Be honest about cost: this spends more than a single model call. The contribution is the architectural pattern, not the absolute leaderboard number — those move weekly. Pivot to the next slide with the question: how does an orchestration system beat a frontier model by 18 points?
:::

---

# Two problems: break groupthink, then recognize the outlier

\Large
- LLMs produce fluent, internally coherent traces --- and are still **confidently wrong**
- On hard tasks, models **cluster around the same wrong interpretation**
- $\Rightarrow$ majority voting / self-consistency *amplifies* the error
- \textbf{(1) Break the groupthink} --- diversify so some candidate reaches the correct answer
- \textbf{(2) Recognize the rare-correct} --- pick it out when most others disagree

\bigskip
\centering
\footnotesize\textcolor{gray!70}{Roadmap: \textbf{(1)} next two slides $\cdot$ \textbf{(2)} after that $\cdot$ then both wired together $\cdot$ then on a real task}

::: notes
The architecture has to solve two problems, not one. First: counter the groupthink --- left to themselves, frontier models cluster on the same wrong interpretation, so the system has to deliberately diversify generation. Second: even when a correct candidate does exist in the pool, majority voting will discard it as an outlier --- so selection has to read the reasoning, not just count votes. Concrete number to drop: of our 39 failure instances, 21 are genuine generation failures and 17 are *selection* failures where a correct candidate exists in the pool but is not chosen. The two failure modes are roughly the same size --- neither dominates.
:::

---

# (1) Break the groupthink --- modalities as search operators

\begin{columns}[t]
\begin{column}{0.32\textwidth}
\centering
{\Large\bfseries\color{accent}TEXT}\\[0.4em]
\footnotesize Model reads the grid as numbers / strings
\end{column}
\begin{column}{0.32\textwidth}
\centering
{\Large\bfseries\color{accent}IMAGE}\\[0.4em]
\footnotesize Model sees a rendered PNG of the grid
\end{column}
\begin{column}{0.32\textwidth}
\centering
{\Large\bfseries\color{accent}CODE}\\[0.4em]
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

# (1) Break the groupthink --- candidate generation in practice

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

# (2) Recognize the rare-correct --- holistic judging vs. majority voting

\Large

- Concatenate all 29 reasoning traces into one long-context judge prompt
- Each judge picks top-2 candidates *and* explains why other clusters are wrong
- Weighted vote across 3 judges $\rightarrow$ pass@2 guesses

\bigskip

\begin{center}
\fcolorbox{accent}{accentlight}{\parbox{0.85\linewidth}{\centering\large\bfseries\color{accent}Net uplift vs. majority-vote baseline: +7 instances\\[0.2em]\normalsize\normalfont\color{inktext}\emph{All 7 are minority recoveries --- the correct answer wasn't the most common candidate.}}}
\end{center}

\bigskip

\footnotesize
Plus \textbf{+1 synthesis} instance (\texttt{21897d95:2}): zero correct candidates --- judge recombined partial insights into a novel correct output.

::: notes
The +7 number is the empirical payoff of the architecture. Say it slowly. The synthesis case is *qualitatively* different --- it shows the system can sometimes *construct* a correct answer rather than just *select* one. Rare (n=1) but a proof-of-possibility for compositional repair. If time allows, quote the judge rationale from dfadab01:1: "Some solvers assume a stamp must fit fully. Others assume stamps are clipped at the border..." --- shows the judge reasoning about disagreement explicitly.
:::

---

# (1) + (2) wired together --- pipeline overview

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

# (1) + (2) on a real task --- 28 of 29 candidates wrong, judges picked the right one {.fragile}

\begin{columns}[c]
\begin{column}{0.40\textwidth}
\centering
\includegraphics[width=\linewidth,height=0.82\textheight,keepaspectratio]{figures/task_2d0172a1.png}
\end{column}
\begin{column}{0.58\textwidth}
\footnotesize
\textbf{Public eval task \texttt{2d0172a1:1}} --- candidate pool $n = 29$

\smallskip

\begin{tabular}{lcc}
\hline
\textbf{Modality family} & \textbf{Correct} & \textbf{Wrong} \\
\hline
Text (8 candidates)  & 0   & 8 \\
Image (10 candidates) & \textbf{1} & 9 \\
Code (11 candidates) & 0   & 11 \\
\hline
\textbf{Total} & \textbf{1} & \textbf{28} \\
\hline
\end{tabular}

\smallskip

\begin{center}
\fcolorbox{successdark}{successlight}{\parbox{0.92\linewidth}{\centering\textbf{Submission verdict: SOLVED} --- holistic judges selected the lone correct candidate}}
\end{center}

\smallskip

\begin{itemize}\setlength\itemsep{0.15em}
\item One image candidate produced the correct nested-frame output; 28 of 29 were wrong
\item Majority voting would collapse onto the wrong cluster
\item \textbf{Our judges recovered the minority-correct candidate}
\end{itemize}
\end{column}
\end{columns}

::: notes
Empirical anchor following the trace excerpt --- and a success story to lean into. **This is a task the submission got right**: 28 of 29 candidates wrong, but the holistic judges identified the one correct image-prompt candidate and that's what was submitted. Walk through the task on the left --- four very different-looking training pairs, all reducing to a nested-frame output that depends on the topology of the winding path in the input. Then point at the table: 28 of 29 candidates wrong; the single correct candidate came from image prompting (a GPT image-modality config); zero correct from text or code. Land the punchline: the architecture's selection layer found it --- exactly what majority voting cannot do. This is one of the +7 minority recoveries from the holistic-judging ablation; the paper lists 2d0172a1:1 as uniquely solved by image prompting.
:::

---

# (2) Recognize the rare-correct --- what the judges actually read (`2d0172a1:1`) {.fragile}

\centering
\footnotesize This task produced \textbf{31{,}208 lines} of reasoning traces / logs.

\smallskip

\begin{columns}[T]
\begin{column}{0.49\textwidth}
\centering\textbf{\small Winning candidate}\\[0.1em]
{\scriptsize \textcolor{gray!70}{GPT-5.2 x-high, image modality}}

\smallskip

\fcolorbox{accent}{accentlight}{\parbox{0.95\linewidth}{\ttfamily\fontsize{5pt}{5.8pt}\selectfont\raggedright%
\textcolor{gray!60}{// logs/2026-01-04\_22-09-54\_2d0172a1\_1\_step\_5.json}\\
\{\\
\hspace*{0.6em}"image": \{\\
\hspace*{1.2em}...\\
\hspace*{1.2em}"gpt-5.2-xhigh\_13\_step\_5\_image\_...": \{\\
\hspace*{1.8em}"actual\_model": "gpt-5.2-xhigh",\\
\hspace*{1.8em}"input\_tokens": 21188,\\
\hspace*{1.8em}"output\_tokens": 59323,\\
\hspace*{1.8em}"Full raw LLM response":\\
"\#\#\# What the examples show\\[0.3em]
In every example, the foreground pixels form\\
several **separate components** of two types:\\[0.3em]
1. **Frames (loops):** ... every such component\\
\hspace*{0.6em}becomes a **perfect axis-aligned\\
\hspace*{0.6em}rectangular border** (thickness 1).\\
2. **Markers (solid small components):** ...\\
\hspace*{0.6em}each marker is reduced to a\\
\hspace*{0.6em}**single foreground cell**.\\
...\\
\#\#\# Applying to the test input\\
- Background color = **7**, foreground = **9**.\\
- One **outer loop frame**, one **inner loop\\
\hspace*{0.6em}frame** inside it, ... two **markers**\\
\hspace*{0.6em}inside, side-by-side $\Rightarrow$ **horizontal**.\\
... outer size **9 rows $\times$ 13 columns**.",\\
\hspace*{1.8em}"Extracted grid": [...]\\
\hspace*{1.2em}\}, ...\\
\hspace*{0.6em}\}, ... \}
}}
\end{column}
\begin{column}{0.49\textwidth}
\centering\textbf{\small Judge's selection rationale}\\[0.1em]
{\scriptsize \textcolor{gray!70}{GPT-5.2 x-high $\times$ 3; all 3 picked correctly}}

\smallskip

\fcolorbox{successdark}{successlight}{\parbox{0.95\linewidth}{\ttfamily\fontsize{5pt}{5.8pt}\selectfont\raggedright%
\textcolor{gray!60}{// logs/2026-01-04\_22-09-54\_2d0172a1\_1\_step\_finish.json}\\
\{\\
\hspace*{0.6em}...\\
\hspace*{0.6em}"selection\_details": \{\\
\hspace*{1.2em}"judges": \{\\
\hspace*{1.8em}"duo\_pick\_council": [\\
\hspace*{2.4em}..., \{\\
\hspace*{3.0em}"model": "gpt-5.2-xhigh",\\
\hspace*{3.0em}"response":\\
"Across the four solved examples, the\\
consistent mechanic is **topological\\
normalization**:\\
- Each **loop** becomes a **perfect 1-cell-\\
\hspace*{0.6em}thick rectangular frame**.\\
- Each **solid component** becomes a\\
\hspace*{0.6em}**single foreground cell (a dot)**.\\
...\\
The two that best match the examples *and*\\
the apparent test structure are:\\
- **Solution 10**: outer frame contains an\\
\hspace*{0.6em}inner frame **plus an extra dot to the\\
\hspace*{0.6em}right** (matching the extra small\\
\hspace*{0.6em}disconnected 9-component at cols\\
\hspace*{0.6em}\textasciitilde{}20--21 in the test input) ...\\
- **Solution 6/7**: the same, but **without**\\
\hspace*{0.6em}the extra right-side dot.\\
\#\#\# Candidate 1 (most likely): Solution 10",\\
\hspace*{3.0em}"picked\_grids": [...]\\
\hspace*{2.4em}\}, ...\\
\hspace*{1.8em}]\\
\hspace*{1.2em}\}\\
\hspace*{0.6em}\},\\
\hspace*{0.6em}"result": "PASS" \}
}}
\end{column}
\end{columns}

\smallskip
\centering
\footnotesize Raw JSON from the public-eval logs; \texttt{"..."} marks elided fields. Judges read \emph{full reasoning} of all 29 candidates $\Rightarrow$ minority recovery.

::: notes
This is the payoff slide for the judging architecture. Show that the trace and the judge response are real artifacts — verbatim excerpts from the logged run. Two beats. Left: the winning image candidate reasoned about "frames vs markers" and "topological normalization" — note that the language is the model's, not a template we forced. Right: the judge independently arrived at the same mechanic and named the rare-correct candidate as "Solution 10" while keeping "Solution 6/7" as the safer pass@2 fallback. Three independent judges all picked the correct grid as their #1 — full alignment. The pedagogical point: the judge does not vote on outputs, it reads the reasoning of all 29 candidates and selects the trace whose argument is most coherent against the training pairs. This is what makes minority recovery possible.
:::

---

# (1) + (2) across 130 tasks --- modality contributions and judges' verdicts {.fragile}

\begin{columns}[T]
\begin{column}{0.36\textwidth}
\centering
\includegraphics[width=\linewidth,height=0.86\textheight,keepaspectratio]{figures/methodology_matrix.png}
\end{column}
\begin{column}{0.62\textwidth}
\footnotesize

\textbf{How to read} (one row = one of \textbf{130 instances} with full 29-candidate coverage):
\begin{itemize}\setlength\itemsep{0em}\setlength\topsep{0em}
\item \textbf{Judges column} (leftmost): the system's final pass@2 verdict --- did the holistic judges submit a correct answer?
\item Other columns grouped by modality family --- \textbf{Text} $\cdot$ \textbf{Image} $\cdot$ \textbf{Code} --- each sub-column = one model/config candidate
\item \colorbox{successlight}{\textcolor{successdark}{\textbf{green}}} = correct $\cdot$ \colorbox{warnlight}{\textcolor{warndark}{\textbf{red}}} = wrong
\item Rows sorted by difficulty: hardest tasks top, easiest bottom
\end{itemize}

\smallskip

\textbf{Three bands tell the story}:
\begin{itemize}\setlength\itemsep{0em}\setlength\topsep{0em}
\item \textbf{Top:} all-red rows --- generation failures (no modality solved them)
\item \textbf{Middle:} \emph{scattered green cells in mostly-red rows} $\Rightarrow$ different modalities catch different problems
\item \textbf{Bottom:} mostly green --- the easy tasks (many modalities solve)
\end{itemize}

\smallskip

\textbf{Edge case --- Judges green, all candidates red}: a \emph{judge-synthesis} solve. Happens on \texttt{21897d95:2}: zero candidates correct, but a judge \textbf{recombined partial insights} across failed candidates into a novel correct output.

\smallskip

\textbf{What the numbers say} ($n{=}130$):
\begin{itemize}\setlength\itemsep{0em}\setlength\topsep{0em}
\item Exclusive solves: \textbf{2 Text-only} $\cdot$ \textbf{6 Image-only} $\cdot$ \textbf{7 Code-only}
\item Pairwise non-overlap: Code solves \textbf{+18} over Text $\cdot$ Image solves \textbf{+13} over Text
\item \textbf{Candidate-oracle: 86.2\%} --- a correct candidate exists for 144/167 instances overall
\item Modalities are \textbf{not redundant copies} of each other
\end{itemize}
\end{column}
\end{columns}

::: notes
The chart is dense --- spend the first 20s teaching the audience how to read it. Point at the top band ("look at these rows: green across the board --- easy tasks"), then the middle band ("but \emph{here} --- mostly red rows with only one or two green cells. That's modality diversity doing the work"), then the bottom ("and these are the generation failures --- no modality solved them"). The 86.2\% oracle number is the most honest framing of the system's ceiling: generation is in good shape; selection is the next frontier. Tie back: of the 39 failures, 17 are \emph{selection} --- that's where the headroom is.
:::

---

# Negative results worth knowing

\footnotesize

\textbf{\large 1. Prescriptive prompting degrades performance.}\\
Templates, CoT scaffolding, domain heuristics --- all hurt on the hardest tasks. Mechanism: a \emph{compliance tax on reasoning} (budget spent following the template instead of solving the problem).

\smallskip

\textbf{\large 2. Iterative refinement reduces diversity.}\\
Refining candidates against each other collapses them onto the same wrong cluster --- the exact failure mode we're trying to escape. Same effect from hint-then-solve pipelines.

\smallskip

\textbf{\large 3. Pipeline decomposition (objects $\rightarrow$ transformations $\rightarrow$ solver) hurts.}\\
Brittle handoffs between stages. Both verbose and terse handovers regress toward the mean rather than expand the hypothesis space.

\smallskip

\textbf{\large 4. Strict JSON outputs underperform CSV.}\\
Forcing API-level response-format schemas consistently lost to CSV + robust regex parsing. Strict schemas appear to constrain reasoning quality, not just output shape.

\smallskip

\textbf{\large 5. Pixel-perfect image renderings hurt.}\\
\emph{Slightly distorted} renders beat pixel-perfect ones for image-modality candidates. Clean renders push the model into cell-by-cell numerical reasoning; intentional imprecision forces engagement with shapes, symmetries, and spatial relationships --- which is the point of image prompting.

\bigskip
\centering
$\Rightarrow$ \textbf{Final system: deliberately minimal prompts, independent generation, no decomposition, CSV I/O, deliberately fuzzy image renders.}

::: notes
Most counter-intuitive findings in the paper --- audiences love negative results because they save them time. Frame these as design constraints we discovered the hard way: every time we added "helpful" structure, scores dropped on the tasks that mattered. (1) and (2) are the big two --- spend more time there. (3) is a useful counterpoint to anyone who's spent six months building a multi-stage agent. (4) will surprise the LLM-engineering audience used to JSON-mode being a default. (5) is the most visually intuitive --- mention that we render the grids with intentional jitter, like a hand-drawn sketch, because pixel-perfect renderings made the model treat the image as a lossless encoding and fall back on numerical reasoning instead of visual.
:::

---

# Takeaways

\textbf{(1) Generate broadly} --- different modalities (text, image, code) and different frontier models, generated \emph{independently}. The hypothesis space matters more than the model.

\medskip

\textbf{(2) Judge holistically} --- a long-context judge reads the \emph{full reasoning}, not just final answers. Majority voting discards the rare-correct; trace-aware judging recovers it (and occasionally synthesizes a new one).

\medskip

\textbf{Where this generalizes:} any hard problem where the \emph{reasoning} signals correctness --- even when the answer itself can't be verified directly. As in ARC: the judges never see the test output; they assess the \textbf{credibility of each trace} against the training pairs. Math contests, code review, legal arguments, scientific hypotheses --- wherever a careful reader can tell sound reasoning from rationalization.

\bigskip
\centering
\footnotesize Code: \texttt{github.com/beetree/ARC-AGI} $\cdot$ Paper QR on title slide

::: notes
Close strong on the generalization claim. Pause on the headline and let it land. Recap (1) and (2). The key clarification on "where this generalizes": this is \emph{not} only for problems with checkable answers (like math or formal proofs). It also works whenever the reasoning itself carries credible signal --- as in ARC, where the judges never see the test output and instead assess each trace's coherence against the training pairs. So the audience should think about applying this anywhere a careful reader could tell sound reasoning from rationalization: code review, legal arguments, scientific hypotheses, design critiques. The closing number reminds them this isn't speculative: verified result, almost 20 points over the best standalone model. Then invite questions. If asked about cost, jump to backup slide. If asked about failure modes, jump to failure-decomposition backup. If asked why three judges, jump to the third backup.
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

# Backup: cost breakdown

\footnotesize

- **Public-eval cost is the representative number: $19.69/task**
- Private $38.99/task inflated by GPT-5.2 API instability (84% failure rate, 2,216/14,106 attempts succeeded)
- Tool-integrated code generation is the largest line item
- ZDR mode used in private verification disables tool calls $\rightarrow$ both lower accuracy and altered cost profile
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
