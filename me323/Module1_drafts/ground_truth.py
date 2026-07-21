"""
STAFF-ONLY frozen class results for ME 323 Module 1.

Policy (2026-07-06, re-frozen 2026-07-20): synthetic queries return the frozen
ground-truth GP central prediction, noiseless, and the two class-wide designs
are FROZEN. The GP models a log response, so exponentiating its latent mean
gives a posterior median on the response scale, not an arithmetic mean. The
values below are hardcoded into the student notebooks (Pre-lab 2 and
Submission 1), so this module exists only as the staff record of where those
numbers came from. Students never import or query anything; they cannot
re-roll or cheat.

Provenance: ground-truth model = the leave-one-location-out winner on all 85
usable tests (44-beam campaign + follow-up batch + support experiment +
2026-07-16 proper-supports recalibration batch; one censored LTB test
excluded). Before down-selection, the same three-parameter junction-shear model
used in Pre-lab 1 was calibrated on the full GT training pool:
(sigma_y, k, tau_i) = (65.242 MPa, 0.424578, 21.056 MPa). The winner is a
Matern GP on log(strength/P_phys), where
P_phys = min(P_bend, P_sep, P_LTB): gpr_str_matern_cal. Requested full-data-
precalibrated LOLO RMSE = 2.494 N/g; leak-free nested-calibration LOLO RMSE =
2.368 N/g, and the same formulation wins both calibration-first tables. The
legacy fixed-physics feature model reruns at 2.216 N/g, but its response-derived
tau_i is held fixed across folds; the fold-calibrated feature analogue scores
3.087 N/g. This re-freeze implements the calibration-first policy and does not
claim a proven absolute accuracy gain over that legacy feature map. Pre-lab 1 separately
calibrates (sigma_y, k, tau_i) = (66.8 MPa, 0.377, 16.76 MPa) on the 15-beam
handout. Derivation: analysis notebooks 15-20 + the faculty GT and shear
notebooks; student-flow regeneration in run13. Class rules: the
ground-truth query returns real proper-support test means where a design has been
printed, else the GT mean; since 2026-07-20 there is NO tested-design
exclusion rule -- in the widened box the locked recipe picks an untested
point on its own.

2026-07-20 re-freeze: design box widened to b in [1.0, 7.0] (was [1.25, 7.0]);
the real b = 1.0 follow-up test ((1.0, 12.5), 475.0 N, flange-web separation)
joined the handout as beam 15. Handout = ridge_blind14 (print orders 4, 6, 20,
25, 27, 31, 33, 34, 35, 37, 39, 40, 41, 44) + that seed beam, i.e.
student_beams_B10_L150.csv (15 rows). Flow: equation design from the class
calibration above (grid arange(1.0, 7.001, 0.05) x arange(5.0, 16.001, 0.05)),
queried and added as beam 16; then the vanilla GP (ARD-RBF, 3% noise, MUI
psi=1, grid linspace(1.0, 7.0, 63) x linspace(5.0, 16.0, 60), no exclusion)
design, queried and added as beam 17. At the locked settings EI picks the
same b = 1.0 edge but a higher web, H = 14.88, than MUI psi=1.

2026-07-21 re-freeze after full-data physics calibration: the equation and
locked-GP coordinates remain (1.10, 13.25) and (1.00, 13.39), respectively.
Their GT responses change to 475.7 N = 37.48 N/g and 445.8 N = 36.65 N/g.
The Pre-lab 2 noise sensitivity also changes: 1% noise recommends
(1.58, 14.88), whereas 3% and 10% recommend (1.00, 13.39).

Keep this file and the full-campaign data out of anything students receive.
"""

FROZEN = {
    "equation": {"b": 1.10, "H_web": 13.25, "str_to_weight": 37.48,
                 "strength_N": 475.7, "mass_basis": "estimated geometry"},
    "gp":       {"b": 1.00, "H_web": 13.39, "str_to_weight": 36.65,
                 "strength_N": 445.8, "mass_basis": "estimated geometry"},
}
# NOTE: no physical print sits within 0.2 mm of either frozen design; the
# nearest tests are single old-support prints at (1.10, 12.50) and
# (1.00, 12.50). Add exact-coordinate grounding prints (b_1.1_H_13.25,
# b_1.0_H_13.39) to the next test batch.
# Superseded 2026-07-17 freeze (pre-widening): equation (1.25, 13.20) ->
# 515.6 N = 39.09 N/g; gp (1.44, 13.20) -> 533.1 N = 38.90 N/g.


def query_truth(which):
    """Frozen class result for one of the two class-wide designs.

    Deterministic by construction: these are frozen GT-GP central predictions,
    rounded as they appear in the student materials.
    """
    if which not in FROZEN:
        raise ValueError(f"Only {list(FROZEN)} exist. Got {which!r}.")
    return {"design": which, **FROZEN[which]}


if __name__ == "__main__":
    for k in FROZEN:
        print(query_truth(k))
