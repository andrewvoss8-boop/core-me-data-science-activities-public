"""STAFF-ONLY. Score student3's (Opus-agent) committed design on the frozen GT model.

Mirrors ibeam150_analysis/run20_gt_roll_86.py exactly: same 85-test training
pool, same full-data physics calibration, same winner formulation
(gpr_str_matern_cal), refit on everything. Run from this grading/ directory
(or adjust the sys.path insert below).

Student3 committed to (1.85, 12.15) — an untested gap pick defended on a
mechanism-specific-bias argument — and named two rejected rivals on the card:
the incumbent replicate (1.10, 13.25) and its own lane's unfiltered pick
(1.39, 11.71).
"""
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, "../../../ibeam150_analysis")
from sklearn.exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=ConvergenceWarning)
from ibeam150_common import (BeamModel, calibrate_junction_physics, mass_g,
                             phys_capacity, phys_parts, OUT_DIR)

master = pd.read_csv(OUT_DIR / "ibeam150_master.csv")
camp = master.dropna(subset=["strength_resolved_N"])
prev = pd.concat([
    camp.rename(columns={"strength_resolved_N": "sN"})[["b", "H", "sN"]]
        .rename(columns={"sN": "strength_N"}).assign(source="campaign", tag=""),
    pd.read_csv(OUT_DIR / "ibeam150_additional_tests.csv")
        [["b", "H", "strength_N", "tag"]].assign(source="followup"),
], ignore_index=True)
psb = pd.read_csv(OUT_DIR / "ps_recalibration_results.csv")
censored = psb.note.str.lower().str.contains("stopped")
ps_t = psb[~censored][["b", "H", "strength_N"]].assign(source="ps_recal", tag="PS")
allt = pd.concat([prev, ps_t], ignore_index=True)
assert len(allt) == 85, f"expected 85 usable tests, got {len(allt)}"
allt["sw_true"] = allt.strength_N / mass_g(allt.b, allt.H)

cal = calibrate_junction_physics(allt)
cal_kw = {k: cal[k] for k in ("sy", "k", "tau_i")}
print(f"calibration: sy={cal['sy']/1e6:.3f} MPa, k={cal['k']:.6f}, "
      f"tau_i={cal['tau_i']/1e6:.3f} MPa")

GT = BeamModel(variant="gpr_str", kernel_kind="matern", shear="new", **cal_kw).fit(allt)

points = [
    ("STUDENT PICK",                1.85, 12.15),
    ("rival: incumbent replicate",  1.10, 13.25),
    ("rival: unfiltered lane D",    1.39, 11.71),
    ("sweep lane-A corner (=b17)",  1.00, 13.39),
    ("sweep lane-C corner",         2.06, 13.58),
    ("student1's pick (context)",   1.39, 13.20),
]
print()
for label, b, H in points:
    sN, sw = GT.predict([b], [H])
    print(f"{label:28s} ({b:.2f}, {H:5.2f}): GT {sw[0]:6.2f} N/g = {sN[0]:6.1f} N, "
          f"mass {mass_g(b, H):.2f} g")

bb = np.linspace(1.0, 7.0, 241)
hh = np.linspace(5.0, 16.0, 221)
BB, HH = np.meshgrid(bb, hh)
_, SW = GT.predict(BB.ravel(), HH.ravel())
i = int(np.argmax(SW))
print(f"\nGT optimum (fine grid): {SW[i]:.2f} N/g at ({BB.ravel()[i]:.3f}, {HH.ravel()[i]:.3f})")

_, sw_pick = GT.predict([1.85], [12.15])
print(f"student pick regret vs GT optimum: {SW[i]-sw_pick[0]:.2f} N/g "
      f"({100*(SW[i]-sw_pick[0])/SW[i]:.1f}%)")
print(f"student pick beats {(SW < sw_pick[0]).mean()*100:.1f}% of the design box (by GT mean)")

m = mass_g(1.85, 12.15)
print(f"\nmass at pick (GT convention): {m:.2f} g")
for name, kw in [("Prelab1-cal", dict(sy=66.8e6, k=0.377, tau_i=16.76e6)),
                 ("GT-cal", cal_kw)]:
    Pb, Ps, _, Pl = phys_parts(1.85, 12.15, shear="new", **kw)
    cap, gov = phys_capacity(1.85, 12.15, shear="new", **kw)
    print(f"{name}: P_bend={Pb:.1f} P_sep={Ps:.1f} P_LTB={Pl:.1f} "
          f"-> cap {cap:.1f} N ({gov}), {cap/m:.2f} N/g")
