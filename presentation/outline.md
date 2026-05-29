# ICAIBD Presentation Outline — Modality-Driven Search for ARC-AGI-2

**Speaker:** Johan Land
**Length:** 15 min slot → ~13 min talk + ~2 min Q&A buffer
**Audience:** ICAIBD general AI/big-data attendees, mostly unfamiliar with ARC-AGI
**Single takeaway the audience should leave with:** *Reasoning modalities (text, image, code) function as distinct search operators — orchestrating their diversity beats scaling any one frontier model.*

---

## Time budget

| # | Slide | Time | Cumulative |
|---|---|---|---|
| 1 | Title + hook | 0:30 | 0:30 |
| 2 | ARC-AGI-2: brief history (5-beat timeline) + two example problems | 1:20 | 1:50 |
| 3 | What is ARC-AGI-2? (one worked task + pass@2 + cost note) | 1:00 | 2:50 |
| 4 | The headline result (leaderboard table) | 0:45 | 3:35 |
| 5 | Why the problem is *selection*, not generation | 1:30 | 5:05 |
| 6 | Core idea: modalities as search operators | 1:30 | 6:35 |
| 7 | Pipeline overview | 1:00 | 7:35 |
| 8 | Candidate generation in practice | 1:00 | 8:35 |
| 9 | Holistic judging vs. majority voting | 1:30 | 10:05 |
| 10 | End-to-end task walkthrough | 2:30 | 12:35 |
| 11 | Modality complementarity (the evidence) | 1:00 | 13:35 |
| 12 | Negative results worth knowing | 1:00 | 14:35 |
| 13 | Takeaways + Q&A prompt | 0:30 | 15:05 |

Slides 14–16 are *backup* (cost breakdown, failure decomposition, why-three-judges) — only pulled out if asked in Q&A.

*Total budget is 5s over the 15-min limit; if you sense drift, the slide most worth trimming is the demo (slide 10).*

---

## Slide 1 — Title & hook (0:30)

**Headline:** Modality-Driven Search with Holistic Trace Judging for ARC-AGI-2
**Subhead:** 72.9% verified result, beating frontier models by ~20%
**Visual:** Title card, your name, affiliation, paper QR code

**Speaker notes**
- Open with one sentence that frames the talk: "Today I want to convince you that on hard reasoning tasks, *how you search across hypotheses* matters more than which model produces them."
- Don't read the abstract. The next slide does the motivation.

---

## Slide 2 — ARC-AGI-2: a brief history + two examples (1:20)

**Headline:** ARC-AGI-2 — a brief history, and two example problems
**Visual layout (two columns):**
  - **Left (~62%):** `presentation/figures/tasks_three_examples.png` — ARC-AGI Example 1 (`e3721c99`) and ARC-AGI Example 2 (`cbebaa4b`) side by side, each with their training pairs and test row (output marked **?**)
  - **Right (~38%):** Bulleted "History of ARC-AGI" with 5 beats (LaTeX/markdown — easy to edit)
**History bullets (right column)**
1. **2019** — ARC introduced (Chollet); top models <5%
2. **2020** — Kaggle: DSL & program synthesis win; LLMs fail
3. **Dec 2024** — o3 ~87% on ARC-AGI-1, but $thousands/task
4. **2025** — ARC-AGI-2 launches; pass@2 + cost-weighted; top models ~50%
5. **May 2026** — **This work: 72.9%**, first verified >70%

**Speaker notes**
- Start with the examples (left). 5 seconds each, just enough to characterize the rule ("color the gray shapes from the legend"; "repair or complete the objects"). Don't try to solve them live.
- Then walk down the right-column bullets top-to-bottom with the laser pointer. Don't dwell on beats 1–2; the audience just needs them as setup.
- The pivot is the o3 → ARC-AGI-2 transition: brute-force compute saturated ARC-AGI-1, so the benchmark was redesigned to make that strategy uncompetitive. This is the framing that makes the rest of the talk feel inevitable.
- Deliver the May 2026 bullet slowly: "the leaderboard sat in the 50s for months — until this work, the first verified result above 70%, at 72.9%."
- Total budget: ~1:20. The history bullets can easily swallow 2 minutes if you elaborate on each beat — resist.

---

## Slide 3 — What is ARC-AGI-2? (1:00)

**Headline:** A few-shot visual reasoning benchmark designed to be easy for humans, hard for AI
**Visual:** `paper/paper-ICAIBD/figures/task_example.png` (task `3dc255db` — the "spaceships" task)
**Bullets**
- Given 3–4 input/output training pairs, infer the transformation rule
- Apply it to a held-out test input — graded **pass@2** (two guesses allowed)
- Scored on both **accuracy** and **cost** ($/task), making efficiency a first-class metric
- Humans solve nearly all of these; the best standalone frontier models hit ~54%

**Speaker notes**
- This is the slide that earns the rest. Spend a full 90 seconds walking the audience through *one* task — point at the input pairs, say what your eye picks up ("spaceships with exhaust particles"), then reveal the rule ("particles move from tail to nose").
- Land the punchline: *you* just did the task in 30 seconds. Frontier LLMs still fail on this one. That gap is what ARC-AGI-2 measures.
- Mention pass@2 explicitly — it matters for the judging architecture later.

---

## Slide 4 — The headline result (0:45)

**Headline:** 72.9% on the ARC Prize Verified leaderboard — +18.7 points over the strongest single model
**Visual:** Simplified version of Table II (top 5 rows only — your system, GPT-5.2 Pro, Gemini 3 Pro, GPT-5.2 X-High, Gemini 3 Deep Think)
**Bullets**
- Private (official): **72.9%** at $38.99/task
- Public eval (self-measured): **76.1%** at $19.69/task
- Best standalone frontier model: GPT-5.2 Pro at 54.2%
- Gap to human panel: still ~27 points — plenty of headroom

**Speaker notes**
- Anchor early. Audience now knows there's a real result to back up the method talk.
- Be honest about cost: "Yes, this spends more than a single model call. The contribution is the architectural pattern, not the absolute number — leaderboards move fast."
- Pivot to the question: *how* does an orchestration system beat a frontier model by 18 points?

---

## Slide 5 — The real problem is selection, not generation (1:30)

**Headline:** On hard tasks, the correct answer is usually a *minority* hypothesis
**Visual:** Schematic — three "clusters" of candidate outputs, the small cluster circled as "correct"
**Bullets**
- LLMs produce fluent, internally coherent reasoning traces — and are still confidently wrong
- On the hardest tasks, models **cluster around the same wrong interpretation**
- ⇒ Majority voting / self-consistency *amplifies* the wrong answer
- The hard problem isn't generating a correct candidate; it's **recognizing** one when most others disagree

**Speaker notes**
- This is the reframe that unlocks the architecture. If you take only one point home before the method, take this one.
- Concrete number: out of the 39 failures, only 21 are genuine generation failures — 17 are *selection* failures where a correct candidate exists in the pool but is not chosen.
- Set up the next slide: "If the correct answer is rare, we need to (a) make sure we generate it, and (b) recognize it without majority-counting."

---

## Slide 6 — Core idea: modalities as search operators (1:30)

**Headline:** Text, image, and code activate structurally different reasoning pathways
**Visual:** Three columns — TEXT (model reads grid as numbers/strings) / IMAGE (model sees rendered PNG of the grid) / CODE (model writes Python to transform the grid)
**Bullets**
- Same task, three different representations → three different hypothesis distributions
- Each modality solves tasks the others miss (Table III in the paper)
- Generate **independently** across modalities — don't pool prompts, don't share scaffolding
- Diversity at *representation* level, not just temperature

**Speaker notes**
- This is the slide the audience should remember. Slow down. Use the word "operator" deliberately — frame it like classic AI search: each modality expands a different part of the hypothesis space.
- The intuition is concrete: a model reading grids as numbers may notice arithmetic patterns a vision-based pass misses; a code-writing pass forces a *constructive* rule the others can leave implicit.
- Lead-in to the demo later: "I'll show you a task where this matters in slide 10."

---

## Slide 7 — Pipeline overview (1:00)

**Headline:** Generate broadly → judge holistically → vote weighted
**Visual:** `paper/paper-ICAIBD/figures/pipeline.png`
**Bullets**
1. **Candidate generation** — up to 29 candidates across Text / Image / Code families, three frontier models
2. **Holistic judging** — 3 judges read *all* traces in one long-context prompt; each picks top 2 (or synthesizes)
3. **Weighted scoring** — judge first-pick = 2 pts, second = 1 pt; top 2 grids become the pass@2 guesses
- Adaptive early-stop: 37/167 instances stopped after the first 8-candidate probe; **36 of 37 correct (97%)**

**Speaker notes**
- One pass through the diagram, no more than 50 seconds. The audience just needs the shape.
- Highlight the long-context point: judges see *full* reasoning traces, not just final answers. This is what enables minority recovery.
- Mention adaptive early-stop to head off the obvious cost objection.

---

## Slide 8 — Candidate generation in practice (1:00)

**Headline:** 29 candidates × 3 modality families × 3 frontier models
**Visual:** Compact version of Table I — modality family × model × count
**Bullets**
- Models: **GPT-5.2** (x-high reasoning), **Gemini 3 Preview** (high), **Claude Opus 4.5** (long context)
- Families: Text (end-to-end reasoning), Image (rendered PNG input), Code (Python with sandbox tools)
- Deliberately **minimal prompts** in each lane — see slide 12 for why scaffolding hurts
- Sandbox tool-use for code candidates (REPL, iterative debugging within a candidate)

**Speaker notes**
- Don't list every configuration. The point is the *structure*: three families crossed with three families of model behavior.
- The "minimal prompts" bullet is a callback you'll cash in on slide 12.

---

## Slide 9 — Holistic judging vs. majority voting (1:30)

**Headline:** Reading all 29 traces in one prompt recovers correct minority hypotheses
**Visual:** Side-by-side: LEFT = "majority vote picks the cluster of 12" (wrong) / RIGHT = "judge reads all traces, picks the lone correct one"
**Bullets**
- Concatenate every candidate's reasoning trace into a single long-context judge prompt
- Judge identifies top 2 *and* explains why other clusters are wrong
- Net uplift vs. majority-vote baseline: **+7 instances** — all minority recoveries
- **+1 synthesis** instance (`21897d95:2`): zero correct candidates, judge recombines partial insights into a novel correct output

**Speaker notes**
- The +7 number is the empirical payoff of the architectural choice on the previous slide. Say it slowly.
- The synthesis case is *qualitatively* different: it shows the system can sometimes *construct* a correct answer rather than just *select* one. This is rare (n=1) but it's a proof-of-possibility for compositional repair — flag it as such.
- Optional one-liner of judge rationale from `dfadab01:1` if time allows: "*Some solvers assume a stamp must fit fully. Others assume stamps are clipped at the border…*" — shows the judge reasoning about disagreement.

---

## Slide 10 — End-to-end walkthrough on one task (2:30)

**Headline:** `d35bdbdc` — from 29 candidates to two guesses
**Visual:** `paper/paper-ICAIBD/figures/d35bdbdc_1_step_5_common.png` plus a 2-column layout:
- LEFT: the task (training pairs + test input)
- RIGHT: a stack of 4–5 candidate outputs labeled by modality, with the judge's pick circled

**Walkthrough script** (~2:30)
1. (0:30) Show the task — let the audience attempt it mentally
2. (0:30) Show what the **Text** candidates produce — note the dominant (wrong) interpretation
3. (0:30) Show the **Image** candidates — note where they diverge from Text
4. (0:30) Show the **Code** candidates — note any structurally different hypothesis
5. (0:30) Reveal the judge's reasoning: which cluster it rejected, which minority it elevated, why pass@2 lets it hedge

**Speaker notes**
- This is the pedagogical heart of the talk. It earns the abstract claims. Resist the urge to rush.
- If you're tight on time, drop the Image step (step 3) and go Text → Code → Judge — the contrast is sharpest there.
- End with: "This is what 'modalities as search operators' looks like in practice — three representations of the same grid, three different hypothesis distributions, judge reads all of them."

---

## Slide 11 — Modality complementarity (1:00)

**Headline:** Each modality solves tasks the others miss
**Visual:** `paper/paper-ICAIBD/figures/methodology_matrix.png` (the per-instance correctness grid)
**Bullets**
- Pairwise non-overlap (n=130, complete-coverage instances): Code solves 18 that Text doesn't, Image solves 13 that Text doesn't, etc.
- Exclusive solves: 2 Text-only, 6 Image-only, 7 Code-only
- ⇒ Modalities are **not redundant copies** of the same reasoning process — they are distinct search operators
- Candidate-oracle accuracy: **86.2%** (at least one correct candidate exists for 144/167 instances)

**Speaker notes**
- The oracle number (86.2%) is the most honest framing of the system's ceiling — it tells you generation is in good shape and selection is the next frontier.
- Tie back to slide 5: "Of our 39 failures, 17 are selection — that's where most of the future headroom is."

---

## Slide 12 — Negative results worth knowing (1:00)

**Headline:** Two things that *don't* work — and shaped the design
**Bullets**
- **Prescriptive prompting degrades performance.** Structured templates, CoT scaffolding, domain heuristics all hurt on the hardest tasks. Mechanism: a "compliance tax" on reasoning — models spend test-time compute following the template, not exploring hypotheses
- **Iterative refinement reduces diversity.** Refining candidates against each other collapses them onto the same wrong cluster — the exact failure mode we're trying to escape
- ⇒ Final system uses **deliberately minimal prompts** + **independent generation**

**Speaker notes**
- These are the most counter-intuitive findings in the paper. Audiences love negative results because they save them time.
- Frame it as a design constraint we discovered the hard way: every time we added "helpful" structure, scores dropped on the tasks that mattered.

---

## Slide 13 — Takeaways + Q&A (0:30)

**Headline:** Orchestrate modalities; judge holistically; resist the urge to scaffold
**Three bullets, large**
1. **Modalities are search operators.** Text, image, code activate different hypothesis distributions — exploit that.
2. **Holistic judging > majority voting.** On hard tasks the truth is a minority hypothesis; let a long-context judge read full traces and pick.
3. **Less prompt structure, more representational diversity.** Prescriptive scaffolding suppresses the creative leaps these tasks reward.

**Closing line**
> "Code is open-sourced — github.com/beetree/ARC-AGI — and I'm here all conference if you want to dig in. Happy to take questions."

---

## Backup slides (only if asked)

### B1 — Cost breakdown
- Public-eval $19.69/task is the representative number; private $38.99 inflated by GPT-5.2 API instability (84% failure rate, 2,216/14,106 attempts succeeded)
- Tool-integrated code generation is the largest line item; ZDR mode disables it, hence the public/private gap
- ARC-AGI-1 with the same system: 94.5% at $11.40/task — easier tasks early-exit cheaply

### B2 — Failure decomposition (167 instances)
- 128 solved (76.6%)
- 21 generation failures (no correct candidate in pool)
- 1 early-stop failure (`dbff022c:1` — extreme groupthink on a legend-to-color ambiguity)
- 17 selection failures (correct candidate exists, judge picked wrong)
- 1 synthesis success (`21897d95:2` — judge recombined partial insights with no correct candidate present)

### B3 — Why three judges?
- Single judge is biased toward its own prior
- 3 parallel judges + weighted scoring (2 pts first, 1 pt second) hedges within the judging step
- Pass@2 format lets the final output also hedge across two interpretations when judges disagree

---

## Rehearsal checklist

- [ ] Time slides 3 and 10 specifically — both have a natural tendency to overrun
- [ ] Have task `3dc255db` (spaceships) loaded as a clean image — this is slide 3, the slide that hooks the audience
- [ ] Pre-write the *exact* sentence you'll use to define "modality as search operator" on slide 6
- [ ] Confirm the conference allows backup slides past the official deck (some don't)
- [ ] Bring a printed copy of slide 4's leaderboard table in case the projector mis-renders the small font
