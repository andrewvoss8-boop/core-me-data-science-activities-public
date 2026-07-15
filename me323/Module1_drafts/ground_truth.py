"""
STAFF-ONLY frozen class results for ME 323 Module 1.

Policy (2026-07-06): synthetic queries return the frozen ground-truth GP
central prediction, noiseless, and the two class-wide designs are FROZEN. The
GP models a log response, so exponentiating its latent mean gives a posterior
median on the response scale, not an arithmetic mean. The values below are
hardcoded into the student notebooks (Pre-lab 2 and Submission 1), so this
module exists only as the staff record of where those numbers came from.
Students never import or query anything; they cannot re-roll or cheat.

Provenance: ground-truth model = the leave-one-location-out winner on all 63
tests (44-beam campaign + 2026-07-08 follow-up batch incl. repeats and the
thin-web frontier): GP on physics features, Matern kernel, str/w target
(gpf_sw_matern). Derivation in me323/ibeam150_analysis/ notebooks 15-16, dry
run in notebook 12. Class rule added 2026-07-08: the vanilla-GP query excludes
already-tested designs (otherwise it re-prints the equation beam). Handout = ridge_blind14
(print orders 4, 6, 20, 25, 27, 31, 33, 34, 35, 37, 39, 40, 41, 44), i.e.
student_beams_B10_L150.csv. Flow: equation design from the class calibration
(sigma_y = 66.5 MPa, k = 0.377, c_s = 2.25), tested and added; then the
vanilla GP (3% noise, MUI psi=1) design, tested and added.

Keep this file and the full-campaign data out of anything students receive.
"""

FROZEN = {
    "equation": {"b": 1.25, "H_web": 13.40, "str_to_weight": 37.64,
                 "strength_N": 483.0, "mass_basis": "estimated geometry"},
    "gp":       {"b": 1.44, "H_web": 13.39, "str_to_weight": 38.12,
                 "strength_N": 509.7, "mass_basis": "estimated geometry"},
}


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
