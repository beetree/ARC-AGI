1. Fix the chart: Multiple key data tables (such as Table 1 and Table 2) in the currently provided text are incomplete, seriously
affecting reading and must be corrected.

Response to #1: Thank you for pointing this out. We corrected the PDF formatting issue that caused some content to render poorly in the two-column IEEE layout. Specifically, the source/prompt text blocks were previously overflowing the column and truncating at the column boundary, which made the affected sections appear incomplete and difficult to read. We revised the template so these blocks now wrap correctly and appear as shaded listings, and we verified the corrected rendering in the revised PDF.

2. Deepen cost analysis: Based on existing data, further analyze the "marginal benefits" of different modalities or candidate
quantities, providing more specific basis for optimizing adaptive routing in the future.

Response to #2: Thank you for this suggestion. Using the existing public-evaluation run data, we added a new post hoc cost/marginal-return analysis to the paper. This includes a staged candidate-family table on the 130-instance complete-coverage subset: Text only = 84/130 oracle-solvable, Text + Image = 101/130, and Text + Image + Code = 108/130. Based on these results, we now make the narrower claim that additional candidate families are not equally valuable and that the existing data support modality-aware staged routing. We also clarify that this is an oracle-based lower-bound analysis rather than a matched end-to-end routing ablation.

3. Highlight the significance of the "synthesis" mechanism: Although the synthesis function only solved one instance, this case
was "zero candidate correct, and the correct answer was obtained by recombining some insights", demonstrating the advanced
potential of the method for creative combination, and its qualitative value should be emphasized.

Response to #3: Thank you for this comment. The paper now states more explicitly that the synthesis case is qualitatively different from the +7 minority recoveries. In the solved synthesis instance (`21897d95:2`), none of the 29 candidates was correct; instead, the correct answer was produced by recombining complementary partial insights from multiple failed candidates. We revised the discussion to frame this as evidence of compositional repair: rather than merely selecting among existing hypotheses, the architecture can sometimes construct a new correct solution by recombining partial insights. We also updated the conclusion to note that, although synthesis appeared only once in this run, the case is qualitatively important because it demonstrates the potential value of recombination across failed candidates.

4. Cautious statement of generality: When discussing the general potential of this architecture in the conclusion, it should be
more explicitly stated that its current evaluation is limited to the ARC-AGI-2 task and analyzed which components may be
more universal.

Response to #4: Thank you for this comment. The conclusion now makes clear that the current evidence is limited to ARC-AGI-2 and does not establish cross-benchmark generality. We also narrowed broader claims in the introduction and conclusion so that they are framed as ARC-AGI-2 findings rather than universal claims about abstract reasoning. In addition, we added a paragraph distinguishing components that may be more broadly portable, such as diverse candidate generation across multiple representations, holistic comparison of full candidate traces, and synthesis as a possible repair mechanism, from components that are more ARC-specific, including the ARC grid encodings, the particular image-rendering setup, the 29-candidate budget, and the pass@2 aggregation rule.
