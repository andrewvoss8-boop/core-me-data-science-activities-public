# GT evaluation — committed design (1.10, 13.25), a deliberate replicate

STAFF-ONLY. Scores the submission's committed design on the frozen synthetic
ground-truth model (`gpr_str_matern_cal`: Matérn GP on log(strength/P_phys),
refit on all 85 usable tests with the full-pool physics calibration
σ_y = 65.242 MPa, k = 0.424578, τᵢ = 21.056 MPa — reproduced exactly by
`gt_eval_script.py`, matching the 2026-07-21 re-freeze). Evaluation run
2026-07-24 by the grader agent.

## Headline

| Point | (b, H_web) | GT str/w | GT strength | Mass |
|---|---|---|---|---|
| **Committed design (= beam 16 replicate)** | (1.10, 13.25) | **37.48 N/g** | **475.7 N** | 12.69 g |
| Frozen GP query (beam 17) | (1.00, 13.39) | 36.65 | 445.8 N | 12.17 g |
| Acquisition pick before the veto | (1.00, 13.20) | 36.47 | 456.4 N | 12.52 g |
| Rival: rejected explore candidate | (1.39, 14.88) | 33.07 | 350.9 N | 10.61 g |
| student1's pick (cross-example) | (1.39, 13.20) | 38.74 | 525.6 N | 13.57 g |
| GT optimum (fine grid) | (1.425, 12.10) | 42.18 | — | — |

- **The design lands inside its preregistered interval.** GT mean 475.7 N vs
  preregistered z = 2 interval [433, 502] N; +0.5σ above the predicted median
  of 466.6 N (GP underpredicted by ~2%). Neither preregistered falsifier
  (peak < 430 N; twist-off before material damage) triggers.
- **By construction the score is the number already on the board.** The
  committed design replicates beam 16 exactly, so its GT mean is the frozen
  query value 37.48 N/g. Scored deterministically, the replicate buys zero
  leaderboard movement; in a live class the print would draw a new noisy
  observation around 475.7 N, and the payoff the card actually argues for —
  repeatability and failure morphology at the incumbent — is real but
  invisible to this scalar scoring.
- **Leaderboard: ties the best observed, wins nothing new.** 37.48 N/g equals
  the class incumbent (its own target) and sits below student1's committed
  38.74. It does not clear 700 N.
- **Regret vs the GT optimum: 4.70 N/g (11.1%)**; the pick beats 91.9% of the
  design box by GT mean.

## The physics-vs-GP call was right

At the committed point, the student's Pre-lab-1-calibrated physics says
617.0 N (48.60 N/g, LTB by 0.6% over bending — the knife edge the card
flags). The GT-calibrated physics gives 514.3 N (LTB: P_bend 606.0 /
P_sep 782.6 / P_LTB 514.3), and GT truth is 475.7 N. Card rows 3 and 7 sided
with the GP's 466.6 N on the ground that the observed query already
contradicted calibrated physics by 23% at this exact point; the GT confirms
that judgment emphatically — truth sits within 2% of the GP and 23% below the
student's calibrated physics.

## The rejection was vindicated

Unlike student1's case (where the rejected lane-D rival outscored the
committed design), the explore candidate this card rejected — (1.39, 14.88),
lane-A median ~35.77 N/g with σ_epi ≈ 0.0507 — scores only **33.07 N/g** on
GT, 4.4 N/g below the committed design and below both frozen queries. The
card's stated reasons (lower expected value, LTB/fixture risk near beam 9's
twist-off) point the right way, and even the GP's optimistic median there was
2.7 N/g too high.

## Hindsight for Submission 2 (grade-neutral now; memo material later)

1. **Pure exploitation of a known point learns nothing the GT scoreboard can
   see.** MUI with ψ = 0 plus a veto to the incumbent is the maximally
   conservative move; its defense (morphology + repeatability evidence) is
   physically sound but means Submission 2 starts with no new information
   about the rest of the design box. A strong Submission 2 must show what the
   replicate's morphology actually purchased.
2. **The GT optimum is off the thin-web ridge the card commits to.** The
   card's whole neighborhood argument lives at b ≈ 1.0–1.5, H ≈ 13.2–13.4;
   the GT optimum sits at (1.425, 12.10) — thicker wall, *lower* web. The
   preregistered update rule only fires on failure (< 430 N or twist-off),
   which the GT says won't happen, so nothing in the plan ever pushes the
   next design toward lower H. Watch whether the Submission 2 refit escapes
   the ridge.
