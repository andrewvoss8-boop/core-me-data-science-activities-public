# Grade report — student2 (Sol agent), Module 1 Submission-1 stage

Graded 2026-07-24 against `Module1_drafts/ME323_Module1_Rubric.md` by a Claude
Fable 5 grader agent. The "student" here was a Sol agent working under student
conditions (handout data only). Submission 2 is not yet filed, so this covers
the four dimensions assessable at the Submission-1 stage (80% of the module
grade). Detailed per-artifact reviews are in the `grader_comments_*.md` files;
the GT scoring of the design is in `gt_design_evaluation.md`.

## Dimension scores

| Dimension | Weight | Score | Assessment |
|---|---|---|---|
| Physics model and assumptions | 20% | 17/20 | Strong |
| Data/ML model and validation | 20% | 16/20 | Good |
| Synthesis and the design decision | 25% | 24/25 | Excellent |
| Preregistration and experimental plan | 15% | 14/15 | Excellent |
| **Stage total** | **80%** | **71/80 (89%)** | |

## Physics — 17/20

All fill-ins run and hit every checkpoint exactly (calibration lands on
σ_y = 66.8 MPa, k = 0.377, τᵢ = 16.76 MPa; equation design (1.10, 13.25) at
48.7 N/g). The calibration memo takes a defended per-parameter position
(σ_y an effective printed-beam strength bounded by beam 7's surviving +10.6%
residual; k a fixture property, not a material one; τᵢ "a campaign average,
not a universal interface constant"), the mode label is treated as a
three-mode knife edge, and every cited residual was verified exactly by the
grader against the raw CSVs — including the mass-delta extremes, which this
submission attributes to the right beams (13 and 1) where the student1
precedent mixed them up.

Deductions: the Q5 trace-shape reading is contradicted by the raw traces for
two of the four beams (beam 14 is the sharpest cliff in the set, not a
gradual failure; beam 13 sheds gradually, not a cliff) — the answer
pattern-matched the failure notes instead of reading the plotted curves, on a
rubric-named requirement; and knife-edge/support-contact fragility is never
named among the validity limits.

## Data/ML — 16/20

All code matches the key, executes in strict order, and every numerical
checkpoint reproduces under independent rerun. Q1 (where uncertainty changes
the action) and Q3 (MUI vs EI, with the correct mechanism for EI's
edge-seeking) meet the key cleanly, and the Q4 failure-notes synthesis —
"two models can agree on coordinates while sharing blindness to the
morphology" — is genuinely good.

Deductions: Q2's sensitivity discussion rests on two claims the student's own
cell-3 printout contradicts (the raw-str/w option has no newtons-then-divide
step and its surface *falls* toward the light corner; the unscaled fit lands
on identical physical length scales), while never citing the shared-vs-ARD
contrast that printout actually demonstrates; and Q4 gives a secondary
argument (shared morphology-blindness) where the key's conditioning argument
— the GP already contains the equation beam's own result, so agreement is not
independent convergence — is only gestured at.

## Synthesis — 24/25

The submission's best work, and a different strategy from the student1
precedent: MUI ψ = 0 plus an engineering veto to an exact replicate of the
best observed/query beam (1.10, 13.25). Physics (48.60 N/g) and GP (36.75)
are put side by side at the candidate with the observed query (37.47) as
tiebreaker; the card explicitly refuses to average and takes the GP's number
on measured-local-bias grounds. The replicate is priced rather than
sleepwalked into — repeatability of a best-in-class result under 3–4%
scatter, plus the failure morphology the staff query deliberately withheld —
and the veto is essentially free (raw exploit argmax 36.74 N/g vs 36.75 at
the replicate). The rejected alternative (1.39, 14.88) is dismantled with
three quantified reasons, all reproduced exactly by the grader, including
Matérn evaluations (35.766 N/g, σ_epi 0.0507) that appear in no notebook
cell — the asserted reruns were genuinely performed. Zero contradicted claims
across the card.

Deductions: card row 4's "overpredicted by 23%" uses the predicted-value
denominator without saying so (29.7% on the observed value), and the rejected
alternative's provenance (RBF ψ = 1 — under the student's own Matérn kernel,
ψ = 1 stays on the ridge) is blurred where naming it would have strengthened
the case.

## Preregistration — 14/15

Sharp and on record before printing: an interval with a stated z
([433, 502] N at z = 2 on σ_total = 0.0370), an expected morphology
(top-flange/web interface separation) that knowingly contradicts the physics
LTB label with reasons, the assumption most likely to break (τᵢ transfer
across print sessions), and falsifiers with concrete consequences (< 430 N or
twist-off before material damage sends the next design off the thin-web
ridge). Deduction: the 430 N falsifier sits 3 N below the interval's lower
bound with no stated reason for the buffer, and the falsifier engages only
the downside of an interval whose upside breach would equally indict the
model.

## Integrity check

Clean across all three artifacts. The knob sweep is structurally independent
of the faculty CSV (noise grid {1, 3, 10} + EI row vs faculty {1, 3, 5, 10};
different column schema at full float precision; all four faculty-only
columns absent), matching picks on shared knob combos follow from the
deterministic pipeline, and greps across the full package for every
faculty/GT-only value (GT calibration, GT optimum, 38.74 / 525.6 N) return
zero hits.

## The three decisive questions (rubric)

1. **Why this beam instead of the next-best alternative?** Answered on record
   and quantified: the replicate beats the rejected explore candidate on
   median (36.75 vs 35.77), epistemic sigma (0.0217 vs 0.0507), and adjacent
   physical evidence (beams 15/17 vs beam 9's twist-off), and it uniquely
   supplies the withheld morphology observation.
2. **What evidence would have changed the choice before printing?** Mostly
   explicit: the pick was conditioned on the A-lane exploit neighborhood
   surviving the kernel/noise sweep, and a staff-supplied failure note for
   beam 16 would have removed half the print's value. Thin spot: what would
   have made them trust lane D's higher extrapolation is never stated.
3. **What changed after testing?** Not yet assessable (Submission 2 pending).
   See `gt_design_evaluation.md`: the design lands inside its preregistered
   interval at exactly the incumbent value (37.48 N/g = 475.7 N — a replicate
   scores the number already on the board), the rejection of (1.39, 14.88)
   is vindicated (GT 33.07), but the GT optimum sits off the thin-web ridge
   at (1.425, 12.10) and the preregistered update rule only fires on a
   failure the GT says won't happen.

## Feedback returned to the student

1. Pre-lab 1 Q5: reread the four traces — beam 14 is the sharpest post-peak
   cliff in the set and beam 13 sheds load gradually; your cliff/gradual
   assignment inverts them, and the correct reading strengthens your own Q4
   distrust of the thin-b separation neighborhood.
2. Pre-lab 2 Q2: both mechanisms you assert are contradicted by your own
   cell-3 printout; the contrast that output actually shows is shared-scale
   [0.61, 1.0] mm vs ARD [3.41, 0.48] mm.
3. Card row 4: state the denominator — the 23% shortfall is on the predicted
   value; as an overprediction on the observed value it is 29.7%.
4. Your falsifier (430 N) sits below your own interval floor (433 N); either
   align them or say why the buffer exists, and consider what an *upside*
   breach (> 502 N) would tell you.

## Note for course staff (not returned to the student)

The Pre-lab 1 template's cell-6 markdown asserts "the cliff beams are the
ones whose notes say *fracture*," which the shipped trace data contradicts
(the separation beam 14 is the sharpest cliff; the partial-fracture beam 13
sheds gradually). This likely primed the student's Q5 error and should be
corrected in the KEY and student template before go-live.
