# GT evaluation — committed design (1.85, 12.15), a physics-margin gap pick

STAFF-ONLY. Scores the submission's committed design on the frozen synthetic
ground-truth model (`gpr_str_matern_cal`: Matérn GP on log(strength/P_phys),
refit on all 85 usable tests with the full-pool physics calibration
σ_y = 65.242 MPa, k = 0.424578, τᵢ = 21.056 MPa — reproduced exactly by
`gt_eval_script.py`, matching the 2026-07-21 re-freeze). Evaluation run
2026-07-27 by the grader agent.

## Headline

| Point | (b, H_web) | GT str/w | GT strength | Mass |
|---|---|---|---|---|
| **Committed design** | (1.85, 12.15) | **41.08 N/g** | **680.2 N** | 16.56 g |
| Rival: incumbent replicate (rejected) | (1.10, 13.25) | 37.48 | 475.7 N | 12.69 g |
| Rival: own lane's unfiltered pick (rejected) | (1.39, 11.71) | 40.83 | 661.1 N | 16.19 g |
| Frozen GP query (beam 17) | (1.00, 13.39) | 36.65 | 445.8 N | 12.17 g |
| student1's pick (cross-example) | (1.39, 13.20) | 38.74 | 525.6 N | 13.57 g |
| GT optimum (fine grid) | (1.425, 12.10) | 42.18 | — | — |

- **The design lands inside its preregistered interval.** GT mean 680.2 N vs
  preregistered z = 1.96 interval [555, 716] N; +1.17σ above the predicted
  median of 630.4 N (38.07 N/g — the GP underpredicted by 7.9%). Neither
  preregistered falsifier triggers: the strength floor (≤ 555 N) is cleared by
  125 N, and the GT governing mode at these coordinates is bending under both
  calibrations, consistent with the preregistered morphology (vertical
  fracture, no separation, no roll) as far as a strength-surface model can
  speak to morphology at all.
- **Best GT result of the three examples, by a wide margin.** 41.08 N/g tops
  student1's 38.74 and student2's 37.48, and beats the class incumbent by
  3.6 N/g. At 680.2 N it falls 20 N short of the 700 N threshold (relevant
  later to the Submission 2 challenge framing, not to this stage).
- **Regret vs the GT optimum: 1.10 N/g (2.6%)**; the pick beats **99.6%** of
  the design box by GT mean. This is the closest any example submission has
  come to the frozen optimum.

## The mechanism-specific-bias argument was right

The card's central claim (row 7): the calibrated physics is not globally
optimistic — it degrades where the governing branch runs out of margin, so at
a point with +42% separation margin and Mcr/My = 1.16 the physics deserves
more trust than the GP's thin-web knockdown implies. The GT agrees to a
degree the student could not have known:

- At the committed point, the student's Pre-lab-1 physics says 720.8 N
  (43.5 N/g); GT truth is 680.2 N — a measured/physics ratio of **0.944**,
  i.e. a ~6% knockdown where the triple-point beams took 22–23%.
- At the rejected unfiltered pick (1.39, 11.71), where the student's own
  filter flagged a 0.7% separation margin, the ratio is **0.90** — a knockdown
  twice as large, exactly the direction the margin argument predicts, though
  far milder than the "20%+" the card feared.
- The GT truth (41.08) splits the student's physics (43.5) and GP (38.07)
  numbers rather than confirming either — the card's refusal to average was
  philosophically right but the truth, this once, sat near the midpoint.

## The veto: value-neutral on the scoreboard, correct in expectation

The unfiltered lane-D pick the card rejected scores 40.83 N/g — only
0.25 N/g below the committed design. The feared 20% collapse at the 1%
separation margin did not materialize on the GT strength surface, so the veto
bought almost nothing in outcome. But it cost nothing either (the filtered
pick actually scored *higher*), and the 0.90-vs-0.944 ratio gradient confirms
the mechanism it was guarding against is real, just smaller than priced. Note
for grader calibration: this is the first example where both the committed
design *and* its rejected rival beat every previously scored design.

## Hindsight for Submission 2 (grade-neutral now; memo material later)

1. **The feasibility filter excluded the GT optimum.** (1.425, 12.10) has a
   separation margin of only +8.7% under the student's calibration — far
   below their 35% floor — and Mcr/My = 1.150, a hair under their 1.15 line.
   The entire 1.10 N/g regret is the price of the filter; the surface the
   filter distrusts is exactly where the truth peaks. A Submission 2 that
   relaxes the margin floor in the light of a 680 N result at 42% margin
   would be following the evidence.
2. **The precommitted update rule points the class slightly wrong.** Row 11
   says a result "near 43 N/g" sends the class to b ∈ [1.6, 2.2]; the GT
   optimum sits at b = 1.425 — the direction their *rejected* pick pointed,
   not their committed one. The observed 41.1 lands between the two
   precommitted readings (43 = mechanism-specific, 36 = broad bias), closer
   to the first; the honest Submission 2 reading is "mechanism-specific bias
   confirmed, magnitude ~6% not 0%, search between the pick and the rival."
3. **The lane disagreement the card flagged was high-stakes, and the student
   picked the right corner.** Scoring the three lane corners the card named:
   lane A's b = 1.0 wall (1.00, 13.39) → 36.65 N/g; lane C's (2.06, 13.58) →
   36.04; lane D's (1.39, 11.71) → 40.83. The three "corners of the same
   neighborhood" span 5 N/g on the truth surface — following lane A or C
   would have cost ~4.5 N/g. The LOO-plus-extrapolation-shape case for lane D
   (card row 4) is what put this submission on the winning side of that
   split, and it deserves the grading weight the synthesis dimension gives
   it.
