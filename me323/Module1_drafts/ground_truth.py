"""
STAFF-ONLY frozen class results for ME 323 Module 1.

Policy (2026-07-06): synthetic queries return the frozen ground-truth GP
central prediction, noiseless, and the two class-wide designs are FROZEN. The
GP models a log response, so exponentiating its latent mean gives a posterior
median on the response scale, not an arithmetic mean. The values below are
hardcoded into the student notebooks (Pre-lab 2 and Submission 1), so this
module exists only as the staff record of where those numbers came from.
Students never import or query anything; they cannot re-roll or cheat.

Provenance: ground-truth model = the leave-one-location-out winner on all 85
usable tests (44-beam campaign + follow-up batch + support experiment +
2026-07-16 proper-supports recalibration batch; one censored LTB test
excluded): GP on JUNCTION-SHEAR physics features (P_sep = 2 tau_i Ix t_w/Q_f,
tau_i = 17.45 MPa, per the faculty shear-model selection), Matern kernel,
str/w target (gpf_sw_matern_sep; LOLO 2.216 N/g). Class physics layer
likewise teaches the junction model; Pre-lab 1 calibrates (sigma_y, k, tau_i)
= (66.8 MPa, 0.377, 17.91 MPa) on the handout. Derivation: analysis notebooks
15-20 + the faculty shear notebook; dry run in notebook 12. Class rules: the
vanilla-GP query excludes already-tested designs; the oracle returns real
proper-support test means where a design has been printed, else the GT mean.
Handout = ridge_blind14 (print orders 4, 6, 20, 25, 27, 31, 33, 34, 35, 37,
39, 40, 41, 44), i.e. student_beams_B10_L150.csv. Flow: equation design from
the class calibration above, queried and added; then the vanilla GP (3% noise,
MUI psi=1, tested-designs excluded) design, queried and added.

Keep this file and the full-campaign data out of anything students receive.
"""

FROZEN = {
    "equation": {"b": 1.25, "H_web": 13.20, "str_to_weight": 39.09,
                 "strength_N": 515.6, "mass_basis": "estimated geometry"},
    "gp":       {"b": 1.44, "H_web": 13.20, "str_to_weight": 38.90,
                 "strength_N": 533.1, "mass_basis": "estimated geometry"},
}
# NOTE: both frozen designs are GT means informed by the adjacent (13.39-13.40)
# proper-support prints 0.2 mm away; add exact-coordinate grounding prints
# (b_1.25_H_13.2, b_1.44_H_13.2) to the next test batch.


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
