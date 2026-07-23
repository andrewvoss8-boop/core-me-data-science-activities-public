# Grade report — student1 (Fable agent), Module 1 Submission-1 stage

Graded 2026-07-23 against `Module1_drafts/ME323_Module1_Rubric.md` by a Claude
Fable 5 grader agent. Submission 2 is not yet filed, so this covers the four
dimensions assessable at the Submission-1 stage (80% of the module grade).
Detailed per-artifact reviews are in the `grader_comments_*.md` files; the GT
scoring of the design is in `gt_design_evaluation.md`.

## Dimension scores

| Dimension | Weight | Score | Assessment |
|---|---|---|---|
| Physics model and assumptions | 20% | 19/20 | Excellent |
| Data/ML model and validation | 20% | 19/20 | Excellent |
| Synthesis and the design decision | 25% | 24/25 | Excellent |
| Preregistration and experimental plan | 15% | 15/15 | Excellent |
| **Stage total** | **80%** | **77/80 (96%)** | |

## Physics — 19/20

All fill-ins run and hit every checkpoint exactly (calibration lands on
σ_y = 66.8 MPa, k = 0.377, τᵢ = 16.76 MPa; equation design (1.10, 13.25) at
48.7 N/g). The memo takes a defended per-parameter position on
correction-vs-measurement: σ_y as an effective strength rather than a coupon
value, k as a fixture property identified from essentially one beam (and
therefore non-transferable), τᵢ as an unlisted property averaging a drifting
bond. The mode label is read as "all three mechanisms active," and the beam-9
judgment call is argued with trace numbers the grader verified against the raw
CSV — the answer conditions the data point's treatment on the model's purpose
(fixture-specific objective vs material capacity), which exceeds the key.

Deductions: a beam-ID mix-up in the mass-delta memo answer (cites beams 4 and
12; the extremes are actually beams 13 and 1 — magnitudes and spread correct),
and knife-edge/contact fragility is never named among the validity limits.

## Data/ML — 19/20

All code matches the key and every checkpoint reproduces. The memo uses
posterior median, epistemic σ, aleatory noise, and total σ each for its own
job throughout, and exceeds the key in two places: a mechanistic explanation
of why EI behaves as an aggressive explorer here (the incumbent 37.48 N/g sits
above the posterior median almost everywhere, so the σ term dominates), and
the conditioning argument that two models fed the same 16 points agreeing is
much weaker than independent convergence.

Deductions (minor): the 4.4% noise case is argued by bracketing rather than
the literal rerun the template invites (the Submission-1 sweep does include
4.4% rows), and the median-vs-mean-in-log-space distinction is used correctly
throughout but never stated in the student's own words.

## Synthesis — 24/25

The submission's best work. Physics (46.8 N/g) and GP (36.65 N/g) are put side
by side at the candidate; the disagreement is traced to a measured local bias
(beams 16 and 17, 0.3–0.4 mm away, came in 21–23% below calibrated physics),
and the card explicitly refuses to average the two numbers. The rejected
alternative is the strongest available — the LOO winner's own recommended
point — dismantled with four quantified reasons. The risk posture and veto are
stated in the notebook before the constrained pick is computed. The
sensitivity claims asserted in the memo were all independently reproduced by
the grader, including the non-obvious (1.29, 13.95) pick at 4.4% noise with
the RBF kernel, so the reruns were genuinely performed. Three figures are
named as the rubric requires.

Deductions: the "0.5 mm lane-D H length scale" cited in card rows 4 and 9 is
actually lane A's length scale — lane D's is ~1.0 mm (the anti-extrapolation
argument survives at the true value, but at half strength); and "moves one
grid notch" understates the 4.4% RBF case, which moves 0.75 mm in H (the
stated 13.2–14.0 band does hold).

## Preregistration — 15/15

Sharp and two-sided: an interval with a stated z ([461, 536] N at z = 2 on
σ_total = 0.038), a specific expected morphology plus named not-expected
morphologies, the assumption most likely to break (3% independent noise
together with the 3.4 mm b length scale), and falsifiers with concrete
consequences (≤ 455 N or clean separation morphology sends the next design to
b ≥ 2). Filed before printing, alongside Submission 1.

## Integrity check

Clean. The knob sweep uses the student-facing noise grid (1/3/4.4/10 vs the
faculty 1/3/5/10), carries full float precision where the faculty CSV is
rounded, lacks all faculty-only columns, and no GT-only numbers appear
anywhere in the submission. Matching picks on shared knob combinations are
expected from the deterministic pipeline (fixed random_state), and the CSV's
top-pick counts match the notebook's own printed groupby.

## The three decisive questions (rubric)

1. **Why this beam instead of the next-best alternative?** Answered
   quantitatively for both rivals: the b = 1.0 wall (near-replicate, edge,
   separation family) and lane D's (1.39, 11.71) (25% cross-model
   disagreement larger than the promised gain, traced to a specific
   correction-factor extrapolation artifact).
2. **What evidence would have changed the choice before printing?** The veto
   sensitivity: had the pick not held across kernels and 1–10% noise under
   the veto, the card says the neighborhood would have been abandoned; the
   preregistered falsifiers extend this past the print.
3. **What changed after testing?** Not yet assessable (Submission 2 pending).
   See `gt_design_evaluation.md` for what the GT says a strong Submission 2
   would have to confront — notably that the rejected lane D point scores
   higher than the committed design, and that the preregistered "step thinner
   along the ridge" update rule points away from the GT optimum.

## Feedback returned to the student

1. Card rows 4/9: the 0.5 mm H length scale you cite for lane D is lane A's;
   lane D's fitted value is ~1.0 mm. Your argument survives, weakened.
2. Pre-lab 1 mass answer: the mass-delta extremes are beams 13 and 1, not 4
   and 12.
