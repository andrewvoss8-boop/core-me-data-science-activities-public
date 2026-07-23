# GT evaluation — committed design (1.39, 13.20)

STAFF-ONLY. Scores the submission's committed design on the frozen synthetic
ground-truth model (`gpr_str_matern_cal`: Matérn GP on log(strength/P_phys),
refit on all 85 usable tests with the full-pool physics calibration
σ_y = 65.242 MPa, k = 0.424578, τᵢ = 21.056 MPa — reproduced exactly by
`gt_eval_script.py`, matching the 2026-07-21 re-freeze). Evaluation run
2026-07-23 by the grader agent.

## Headline

| Point | (b, H_web) | GT str/w | GT strength | Mass |
|---|---|---|---|---|
| **Committed design** | (1.39, 13.20) | **38.74 N/g** | **525.6 N** | 13.57 g |
| Frozen equation query (beam 16) | (1.10, 13.25) | 37.48 | 475.7 N | 12.69 g |
| Frozen GP query (beam 17) | (1.00, 13.39) | 36.65 | 445.8 N | 12.17 g |
| Rival: unconstrained acquisition | (1.00, 13.20) | 36.47 | 456.4 N | 12.52 g |
| Rival: lane D pick | (1.39, 11.71) | 40.83 | 661.1 N | 16.19 g |
| GT optimum (fine grid) | (1.425, 12.10) | 42.18 | — | — |

- **The design lands inside its preregistered interval.** GT mean 525.6 N vs
  preregistered z = 2 interval [461, 536] N; +1.5σ above the predicted median
  of 497 N (GP underpredicted by ~6%). Neither preregistered falsifier
  triggers.
- **It would top the class leaderboard**: 38.74 N/g beats the best beam ever
  tested (37.48) and both frozen class queries. At GT mean it qualifies for
  the strongest-str/w bonus; it does not clear 700 N.
- **Regret vs the GT optimum: 3.44 N/g (8.1%)**; the pick beats 96.1% of the
  design box by GT mean.

## The physics-vs-GP call was right

At the committed point, the GT-calibrated physics gives 531.3 N
(LTB-governed: P_bend 620.5 / P_sep 1003.7 / P_LTB 531.3) — remarkably close
to the GT GP's 525.6 N. The submission's Pre-lab-1-calibrated physics said
635 N. Card row 7 sided with the GP's 497 over the physics' 635 on the ground
that the 21–23% physics overprediction was measured at beams 16 and 17; the
GT confirms that judgment: truth sits within 6% of the GP and 17% below the
student's calibrated physics.

## Hindsight for Submission 2 (grade-neutral now; memo material later)

1. **The rejected rival was actually better.** Lane D's (1.39, 11.71) scores
   40.83 N/g on GT — above the committed 38.74. Lane D's promise of 42.5 was
   only ~4% high; lane A's 33.0 counter-prediction there — the card's core
   reason for rejecting — was ~19% low. Per the rubric this costs nothing at
   Submission 1 (the rejection was well-evidenced given one print), but a
   strong Submission 2 should confront it.
2. **The preregistered update rule points the wrong way.** "≥ 510 N: next
   design steps thinner along the ridge (b toward 1.2)" fires at GT truth
   (525.6 N), but the GT optimum sits at slightly *thicker* b and *lower* H
   (1.425, 12.10). Watch whether the Submission 2 refit catches this.
