# Grade report — student3 (Opus agent), Module 1 Submission-1 stage

Graded 2026-07-27 against `Module1_drafts/ME323_Module1_Rubric.md` by a Claude
Fable 5 grader agent. The "student" here was a Claude Opus agent working under
student conditions (handout data only; package delivered as
`solutions_opus5`). Submission 2 is not yet filed, so this covers the four
dimensions assessable at the Submission-1 stage (80% of the module grade).
Detailed per-artifact reviews are in the `grader_comments_*.md` files; the GT
scoring of the design is in `gt_design_evaluation.md`.

## Dimension scores

| Dimension | Weight | Score | Assessment |
|---|---|---|---|
| Physics model and assumptions | 20% | 18/20 | Strong-plus |
| Data/ML model and validation | 20% | 18/20 | Strong-plus |
| Synthesis and the design decision | 25% | 22/25 | Strong, with a transparency defect |
| Preregistration and experimental plan | 15% | 15/15 | Exemplary |
| **Stage total** | **80%** | **73/80 (91%)** | |

## Physics — 18/20

All fill-ins run and hit every checkpoint exactly (calibration lands on
σ_y = 66.8 MPa, k = 0.377, τᵢ = 16.76 MPa; equation design (1.10, 13.25) at
48.7 N/g), and the memo sits *above* the key on Q1–Q4 with every cited
number independently verified — including two non-obvious structural claims
that checked out exactly: at the bulk τᵢ guess the separation branch governs
nowhere in the 26,741-point design box ("the model was structurally
incapable of predicting the one mechanism three of fifteen beams
exhibited"), and the triple-point robustness argument whose predicted
consequence is the observed 23.0% query shortfall. The beam-9 treatment
(0.0% residual as a fitting identity; "weak" vs "unstable on this stand" as
different design instructions) exceeds the key's target. Card rows 2 and 6
verify exactly (capacities to 0.1 N, all support distances and morphology
quotes).

Deductions: the Q5 trace-shape reading is contradicted by the raw traces —
beam 14 is the sharpest post-peak cliff in the set (not a progressive peel)
and beam 13 sheds gradually (not a near-vertical drop) — the same
template-primed inversion the student2 example made, mitigated here because
this submission verifiably worked from the pre-fix template whose given
prose asserted the error; plus a factual slip (beam 9 called the lowest
thin-beam str/w; beam 12 is, at 28.10 vs 30.96), and knife-edge/
support-contact fragility never named among the validity limits (the same
omission as both precedents).

## Data/ML — 18/20

Pre-lab 2 is the best of the three examples: all checkpoints reproduce
exactly, and the two hardest memo claims survive adversarial recomputation —
the raw-vs-log null contrast (36.81 vs 36.78, location unchanged: precisely
the claim the student2 precedent got wrong, here correct and used to
identify the load-bearing knob) and the beam-16-removal counterfactual
(refit without beam 16 moves the GP's peak to (3.23, 14.70), out of the
thin-b strip entirely — the conditioning argument stated as a checkable
prediction that checks out). Q4 nails the key's central point in the
student's own image: the equation beam's result "is one shared data point
wearing two hats." On the submission side, the LOO table matches the key,
and the memo's region-split LOO (D's advantage entirely in thick-web beams,
1.76 vs 2.72; all lanes within ~0.4 N/g in the thin-web family) reproduces
exactly and is the module's intended lesson — the LOO table chose the model,
not the design — discovered unprompted.

Deductions: the §5 stress test claims the unfiltered lane-D argmax moves to
(1.35, 11.90) under RBF; it moves to (1.40, 11.60) — the H direction is
wrong; the §2 citation of lane A's 0.48 mm ARD length scale silently uses
the class RBF/3% fit rather than the student's stated Matérn/4.4% knobs
(0.73 mm); plus pre-lab small-caliber looseness ("17 beams" in a 16-beam
notebook, a "falls" for a rises-then-falls sequence, EI labeled a "pure
uncertainty maximizer" one sentence after correctly stating the mechanism
that contradicts the label).

## Synthesis — 22/25

The most ambitious synthesis of the three examples, and the best-vindicated
by the frozen GT. The card's central argument — the calibrated physics is
not globally biased; it degrades where the governing branch runs out of
margin, so a point with +42% separation margin and 1.16 LTB reserve deserves
the physics' 43.5 N/g more than the GP's thin-web knockdown — is original,
quantified (the sorted measured/physics ratio table reproduces exactly:
1.23/0.93/0.88/0.79/0.77, thick-web beams 0.90–1.09 with "no pattern left
over" confirmed), and staked rather than hedged: "we do not average the two
numbers." Two rejected alternatives are named and priced — the incumbent
replicate (a deliberate, argued inversion of the student2 strategy: "a print
there confirms a number we already have and explains nothing") and the
lane's own unfiltered argmax, given up for a 2.3 N/g cut to buy a 42%
margin. The 200-row knob sweep reproduces to the row, and its reading — "the
point is not robust; the neighborhood is" — is the honest version of a
result most memos would overclaim. GT scoring (`gt_design_evaluation.md`):
680.2 N = 41.08 N/g, inside the preregistered interval at +1.2σ, the best GT
result of the three examples, 2.6% regret vs the GT optimum, and the
lane-corner scoring shows the lane-D case put this submission on the right
side of a 5 N/g split.

Deductions, one point each. **(1) The cell-14 override:** the notebook
computes a fine-grid filtered argmax and silently overwrites it with
(1.85, 12.15) under the comment "printable rounding of the argmax"; the
actual argmax is (1.84, 11.81) — a +0.34 mm manual move in H_web, never
printed, never disclosed, never defended. The procedure the card defends is
not the procedure that ran, and in a rubric that grades decision quality,
an undisclosed hand adjustment at the single decisive step is the
submission's most serious defect. **(2) Card row 8:** three of its claims
fail verification — σ_epi at beam 16 is 0.0267, not the asserted 0.022
(reproducible under no setting tried); "no lane's posterior median reaches
37.47 anywhere" is contradicted by the card's own rows 3 and 9 (lane D:
38.07, 40.4); and the EI-collapses-to-σ-ranking diagnosis, offered as the
grounds for rejecting EI "on diagnosis rather than taste," is false for the
student's own lane (lane-D EI picks the same point as their MUI,
median-driven). **(3) Accumulated precision slips:** 43.6 N/g and 2.93 mm
against the notebook's own printed 43.5/2.92, "0.02 mm" for a 0.013 mm
distance, RBF/3% numbers cited where the card implies the student's own
knobs, and memo §6's "none inside the feasible region" colliding with card
row 4's "exactly one" (reconcilable only under a charitable parse; the one
feasible sweep pick — A-plain/RBF/10%/EI at (7.00, 13.58) — is disclosed
nowhere).

## Preregistration — 15/15

The sharpest preregistration of the three examples, and the first to earn
full marks. Interval with stated z whose bounds match the notebook printout
to 0.1 N/g (555–716 N at z = 1.96 on σ_total = 0.065); an expected
morphology written in the note-taker's own vocabulary ("complete vertical
fracture across the center," possibly "not completely through") with the two
excluded mechanisms named; an assumption-most-likely-to-break row that names
the *rival explanation* for the observed physics bias (thinness-scaling
rather than margin-scaling — the one hypothesis that would make both models
wrong in the same direction) instead of a generic worry; falsifiers in both
directions with different stated consequences — a strength floor equal to
the interval bound exactly (fixing the 430-vs-433 defect student2 was
deducted for), a morphology trigger at any load explicitly ranked as *more*
damaging than a low number, an upside trigger (> 700 N redirects the class
search), and a weaker-signal tier (twist-before-fracture → k); and row-11
readings pre-committed to three outcome bands before the test. Every
threshold on the row (τᵢ < 11.8 MPa, k +11%) verifies exactly.

## Integrity check

Clean across all four artifacts. The notebook executes top to bottom with
every printed output byte-identical to the grader's fresh run; the 200-row
knob sweep regenerates deterministically and is structurally independent of
the faculty CSV (different noise grid, different schema, student-added
feasibility columns, all faculty-only columns absent); greps across the
package for every faculty/GT-only value (GT calibration, GT optimum,
41.08/680.2, prior examples' 38.74/525.6) return zero hits outside base64
image bytes. The Pre-lab 1 memo's reference to the 23% query shortfall is
Pre-lab 2 information, legitimate at turn-in time (pre-labs are filed with
Submission 1) but noted for staff: the memos were written or revised with
downstream knowledge.

## The three decisive questions (rubric)

1. **Why this beam instead of the next-best alternative?** Answered twice
   over, on record, quantified, and verified: against the incumbent
   replicate (buys a confirmation, not a discrimination) and against the
   lane's own higher-median argmax (0.5% separation margin, 0.013 mm in web
   thickness from a beam that separated, 9.4 N/g ensemble spread — the cut
   in median priced explicitly at 2.3 N/g for a 42% margin).
2. **What evidence would have changed the choice before printing?**
   Explicit: row 10 states the τᵢ and k values that flip the argument, the
   break-assumption row names the alternative bias mechanism that would make
   the pick optimistic by 20%, and memo §5 concedes the point survives only
   as a neighborhood. Thin spot: what evidence would have *kept* the
   unfiltered argmax is never stated.
3. **What changed after testing?** Not yet assessable (Submission 2
   pending). See `gt_design_evaluation.md`: the design lands at 680.2 N
   (41.08 N/g), inside its preregistered interval, best of the three
   examples, 2.6% from the GT optimum; the mechanism-specific-bias reading
   is confirmed in direction and ordering (knockdown 6% at the pick's
   margins, 10% at the rival's, 22–23% at the triple point); the rejected
   rival scores 40.83, so the feared collapse there did not materialize;
   and the GT optimum (1.425, 12.10) fails the student's own feasibility
   filter — the 1.10 N/g regret is the price of the margin argument, and
   the precommitted "search b ∈ [1.6, 2.2] next" points slightly away from
   where the truth peaks.

## Feedback returned to the student

1. Cell 14 hard-codes (1.85, 12.15) over the computed argmax (1.84, 11.81)
   and calls it "printable rounding." A 0.34 mm move in H_web is a decision,
   not a rounding; print the pre-override argmax and write the sentence that
   defends the move — or submit the argmax. As filed, the card defends a
   procedure the notebook did not run.
2. Card row 8 needs a rewrite: σ_epi at beam 16 is 0.027, not 0.022; your
   own rows 3 and 9 quote lane-D medians above 37.47, so "no lane reaches
   the incumbent" is contradicted on the same page, and your EI diagnosis
   holds only for lanes A and C — under your own lane, EI picks your MUI
   point for the median, not the σ. Your MUI-ψ=0.5 decision survives; its
   stated grounds do not.
3. Pre-lab 1 Q5: read the traces off the plots, not the notes — beam 14 is
   the sharpest cliff in the set and beam 13 sheds gradually. The correct
   reading strengthens your own §4b: the separation events are the abrupt
   ones, which is one more reason the margin you bought matters.
4. State numbers at the precision your notebook prints: 43.5 N/g and
   2.92 mm, not 43.6 and 2.93; 0.01 mm, not 0.02; and when you cite ensemble
   members fit under other knobs (33.0/36.1, the 0.48 mm length scale), say
   so.
5. Memo §6's "none inside the feasible region" and card row 4's "exactly
   one" cannot both be read plainly; name the one feasible sweep pick
   (the b = 7.0 EI outlier) and the sentence becomes both consistent and
   stronger.

## Note for course staff (not returned to the student)

This submission was completed against the pre-`b391ee9` Pre-lab 1 template
(every given markdown cell is byte-identical to the pre-fix version), so the
Q5 trace-shape error reproduces the documented template-priming defect a
third time — the fix is confirmed necessary; ensure dry-run agents and live
students pull current templates. The Pre-lab 2 copy likewise predates the
`414b6a3` kernel-prior paragraph. Also: the shipped package omitted the
`knob_sweep.csv` the notebook writes (regenerated deterministically by the
grader, `knob_sweep_grader_rerun.csv`); a live submission checklist should
name the CSV explicitly. Finally, cell 14's editable final-assignment line
is where this cohort's one integrity-adjacent defect appeared — a template
that *prints* the filtered argmax before any manual override would make
silent overrides visible by construction.
