"""Build the four polished student notebooks for Module 1 (ridge_blind14 flow).

Everything students see is self-contained: no ground-truth access, class query
results hardcoded, and every FILL-IN step followed by a printed checkpoint
("you should arrive at ...; if not, check your work or talk to a TA").

The builder derives every checkpoint number by executing the SOLUTION version
of the exact notebook code, so the printed values cannot drift from what the
code produces. Outputs:
  me323/student_beams_B10_L150.csv (+ copy in Module1_drafts/)
  Module1_drafts/ME323_Module1_Prelab1_FailureModes_student.ipynb
  Module1_drafts/ME323_Module1_Prelab2_ML_student.ipynb
  Module1_drafts/ME323_Module1_Submission1_Design_student.ipynb
  Module1_drafts/ME323_Module1_Submission2_Lightweight_student.ipynb
"""
import io
import os
import pathlib
import contextlib
import numpy as np
import pandas as pd
import nbformat as nbf

HERE = pathlib.Path(__file__).resolve().parent
ME323 = HERE.parent
DRAFTS = ME323 / "Module1_drafts"

# ----------------------------------------------------------------------------------
# 1. the handout CSV (ridge_blind14, re-numbered 1..14)
# ----------------------------------------------------------------------------------
RIDGE_BLIND14 = [4, 6, 20, 25, 27, 31, 33, 34, 35, 37, 39, 40, 41, 44]
master = pd.read_csv(HERE / "outputs" / "ibeam150_master.csv")
hand = master[master.print_order.isin(RIDGE_BLIND14)].sort_values("print_order").copy()
out = pd.DataFrame({
    "beam_id": range(1, 15),
    "b_mm": hand.b.values, "H_web_mm": hand.H.values,
    "weight_g": hand.weight_g.values,
    "strength_N": hand.strength_resolved_N.values,
    "failure_note": hand.comment.str.strip().values,
})
DATA_DIR = ME323.parent / "data"
out.to_csv(DATA_DIR / "student_beams_B10_L150.csv", index=False)
out.to_csv(DRAFTS / "student_beams_B10_L150.csv", index=False)
print("wrote student_beams_B10_L150.csv (14 beams) to data/ and Module1_drafts/")

# frozen class results (run12 v6 dry run, oracle policy v3; GT = gpf_sw_matern_sep
# trained on all 85 usable tests incl. the proper-supports batch — see notebook 20)
EQ_B, EQ_H, EQ_SW, EQ_N = 1.25, 13.20, 39.09, 515.6
GP_B, GP_H, GP_SW, GP_N = 1.44, 13.20, 38.90, 533.1

# ----------------------------------------------------------------------------------
# 2. shared source blocks (student-facing, self-contained)
# ----------------------------------------------------------------------------------
SRC_CONST = '''\
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import warnings; warnings.filterwarnings("ignore")
plt.rcParams["figure.dpi"] = 120

# Fixed geometry (you choose b and H_web; everything else is set)
B, TH, L = 10.0, 18.0, 150.0     # flange width, total height, test span (mm)
LP = 172.0                        # printed length (mm); overhangs the 150 mm span
KMASS = 0.2045                    # g/mm^2: mass per unit cross-section area at 172 mm

# Handbook starting values — Pre-lab 1 calibrates the three marked ones
SY = 76e6                         # Pa, PLA strength                 (calibrated)
K_LTB = 0.33                      # fixture effective-length factor  (calibrated)
TAU_I = 43.9e6                    # printed-interface shear strength (Pa) — starting
                                  # guess = bulk yield / sqrt(3)     (calibrated)
E, G = 2.5e9, 2.5e9 / 2.6         # Young's / shear modulus (Pa) — fixed
C1, C2 = 1.35, 0.55               # LTB moment-gradient / load-height factors
'''

SRC_LOAD = '''\
URL = ("https://raw.githubusercontent.com/andrewvoss8-boop/"
       "core-me-data-science-activities-public/main/data/student_beams_B10_L150.csv")
try:
    df = pd.read_csv(URL); print("loaded from GitHub")
except Exception:
    df = pd.read_csv("student_beams_B10_L150.csv"); print("loaded local copy")
df = df.rename(columns={"b_mm": "b", "H_web_mm": "H"})

def estimated_mass_g(b, H):
    A = b * H + B * (TH - H)      # cross-section area, mm^2
    return KMASS * A              # grams
df["mass_est_g"] = estimated_mass_g(df.b, df.H)
df["mass_delta_g"] = df.weight_g - df.mass_est_g
df["mass_delta_pct"] = 100*df.mass_delta_g/df.mass_est_g
print(len(df), "tested beams")
'''

SRC_SECTION = '''\
def section_props(b, H):
    """I-section properties. b, H in mm; everything returned in METERS/SI."""
    tf = (TH - H) / 2.0
    b_, h_, B_, tf_ = b/1e3, H/1e3, B/1e3, tf/1e3
    c = (TH/1e3) / 2
    Ix = (b_*h_**3)/12 + 2*((B_*tf_**3)/12 + B_*tf_*(h_/2 + tf_/2)**2)
    Iy = (h_*b_**3)/12 + 2*(tf_*B_**3)/12
    def J_rect(x, y):
        short, long = min(x, y), max(x, y)
        r = short/long
        beta = 1 - 0.63*r + 0.052*r**5
        return (1/3)*beta*long*short**3
    J = J_rect(b_, h_) + 2*J_rect(tf_, B_)
    Cw = Iy*(h_ + tf_)**2/4
    return dict(Ix=Ix, Iy=Iy, J=J, Cw=Cw, c=c,
                b=b_, h=h_, tf=tf_, B=B_)
'''

SRC_PHYS_FULL = SRC_SECTION + '''
def P_bend(p, sy):
    return 4*sy*p["Ix"] / (p["c"] * L/1e3)
def P_LTB(p, sy, k):
    My = sy*p["Ix"]/p["c"]
    Lb, zg = k*L/1e3, p["c"]
    R = p["Cw"]/p["Iy"] + (Lb**2*G*p["J"])/(np.pi**2*E*p["Iy"]) + (C2*zg)**2
    Mcr = C1*np.pi**2*E*p["Iy"]/Lb**2 * (np.sqrt(R) - C2*zg)
    return 4*min(My, Mcr)/(L/1e3)
def Q_flange(p):
    return p["B"]*p["tf"]*(p["h"]/2 + p["tf"]/2)
def P_sep(p, tau_i):
    """Flange-web separation: shear flow vs strength along the printed layer lines."""
    return 2*tau_i*p["Ix"]*p["b"]/Q_flange(p)
def capacity(b, H, sy, k, tau_i):
    """Class model (2026-07-15): plain minimum of the three mode capacities."""
    p = section_props(b, H)
    return min(P_bend(p, sy), P_sep(p, tau_i), P_LTB(p, sy, k))
def gov_mode(b, H, sy, k, tau_i):
    """Dominant pure-mode proxy, not an observed failure-mechanism label."""
    p = section_props(b, H)
    Pb, Ps, Pl = P_bend(p, sy), P_sep(p, tau_i), P_LTB(p, sy, k)
    return "separation" if Ps < min(Pb, Pl) else (
        "LTB" if Pl < 0.999*Pb else "bend")
'''

# calibrated values (verified below against the solution run)
CAL_SY, CAL_K, CAL_TAU = 66.8e6, 0.377, 17.91e6  # run12 dry run, junction model

SRC_GP_FIT = '''\
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel as C, RBF

def fit_gp(data, alpha=0.03**2, feats=("b", "H"), target="log_sw"):
    """The class GP recipe: z-scored inputs, log target, RBF kernel, MLE."""
    X = data[list(feats)].values.astype(float)
    fmu, fsd = X.mean(0), X.std(0) + 1e-12
    if target == "log_sw":
        y = np.log(data.strength_N.values /
                   estimated_mass_g(data.b.values, data.H.values))
    elif target == "log_strength":
        y = np.log(data.strength_N.values.astype(float))
    else:                                    # log residual vs calibrated physics
        Pphys = np.array([capacity(b, H, SY_CAL, K_CAL, TAU_CAL)
                          for b, H in zip(data.b, data.H)])
        y = np.log(data.strength_N.values) - np.log(Pphys)
    ymean = y.mean()
    ker = C(1.0, (1e-3, 1e3)) * RBF([1.0]*X.shape[1], (1e-1, 30.0))
    gp = GaussianProcessRegressor(ker, alpha=alpha, normalize_y=False,
                                  n_restarts_optimizer=5, random_state=0)
    gp.fit((X - fmu) / fsd, y - ymean)
    return gp, fmu, fsd, ymean
'''

# ----------------------------------------------------------------------------------
# 3. notebook cell definitions (tokens «...» filled after the solution run)
# ----------------------------------------------------------------------------------
def md(s):
    return ("md", s)

def code(s):
    return ("code", s)

def key_md(s):
    """Markdown included only in the executed staff KEY."""
    return ("key_md", s)

def key_code(s):
    """Code included only in the executed staff KEY."""
    return ("key_code", s)

# =========================== PRE-LAB 1 =============================================
P1 = [
md('''# Pre-lab 1: Failure Modes, Calibration, and the Equation Design
### ME 323 Module 1

<img src="https://raw.githubusercontent.com/andrewvoss8-boop/core-me-data-science-activities-public/main/me323/Module1_drafts/figures/I_beam_dimensions.jpg" alt="I-beam dimensions" width="260">

In the image, `b` is web thickness, `H` is web height, `B` is flange width,
and the image's `h` is the flange thickness called `t_f` in this notebook.

You will load the class beam data, compute strength-to-weight, code the
failure-mode formulas, inspect where they disagree with real failures, tune
the parameters by hand, calibrate them, and optimize the class equation design.

Lines marked `FILL IN` are yours. Each step prints a checkpoint.'''),
code(SRC_CONST + 'print("Constants loaded. Nominal SY =", SY/1e6, "MPa")'),
md('''## 1. The data

These are fourteen real three-point-bend tests. The beams were printed at
172 mm and tested on a 150 mm support span. `failure_note` is the test engineer's
observation, not a model-generated label. `weight_g` is measured; `mass_est_g`
comes from nominal geometry. They should not be identical. Read the notes and
the mass discrepancy before fitting anything.'''),
code(SRC_LOAD + '''
pd.set_option("display.max_colwidth", None)
df[["beam_id", "b", "H", "weight_g", "mass_est_g", "mass_delta_pct",
    "strength_N", "failure_note"]].round({"mass_delta_pct": 1})'''),
md('''## 2. Strength-to-weight

The design objective uses estimated mass from nominal geometry:

$$A=bH+B(T-H), \\qquad m_{est}=K_{mass}A.$$

Measured mass retains print variation, dimensional error, and scale error.
Estimated mass keeps the optimization objective available before printing.
Keep both. Frozen class rankings use `strength_N / mass_est_g`.'''),
code('''df["str_to_weight"] = ____    # >>> FILL IN: strength divided by estimated mass
df["str_to_weight_measured_mass"] = df.strength_N / df.weight_g
top = df.sort_values("str_to_weight", ascending=False)
print(top[["beam_id", "b", "H", "weight_g", "mass_est_g",
           "str_to_weight_measured_mass", "str_to_weight"]]
      .round(2).to_string(index=False))
print("\\nMeasured minus estimated mass:")
print(df[["beam_id", "mass_delta_g", "mass_delta_pct"]]
      .round(2).to_string(index=False))
print("\\nCHECKPOINT: the best of the original 14 beams should be beam «BEST_ID» "
      "(b=«BEST_B», H_web=«BEST_H») at «BEST_SW2» N/g.")
print("If you are not getting that, check your work or talk to a TA.")'''),
md('''## 3. Section geometry and what each property controls

The flange width `B = 10 mm` and total height `T = 18 mm` are fixed. You choose
web thickness `b` and web height `H`; therefore flange thickness is
$t_f=(T-H)/2$ and outer-fiber distance is the fixed $c=T/2$.

- $A=bH+B(T-H)$ is material area. It sets mass. It is linear in either design
  variable separately, but bilinear jointly.
- $I_x=[BT^3-(B-b)H^3]/12$ is the strong-axis second moment. Bending stress and
  bending deflection scale as $1/I_x$. It grows linearly with `b`; because
  total height is fixed, it decreases cubically as `H` grows and the flanges thin.
- $I_y=[Hb^3+(T-H)B^3]/12$ is the weak-axis second moment. It controls lateral
  bending in LTB. Its web term is cubic in `b`, while increasing `H` replaces
  wide flange material with narrow web material and usually lowers $I_y$.
- $J$ is the St. Venant torsion constant. LTB resistance grows with it. It is
  dominated by thickness-cubed terms with aspect-ratio corrections.
- $C_w=I_y(H+t_f)^2/4$ is the warping constant used by the LTB approximation.
  Its dependence is more complex because $I_y$ falls while flange separation grows.

The code returns SI units. Inputs arrive in millimeters, but $I_x,I_y,J$ are in
$m^4$, $C_w$ is in $m^6$, and lengths in the returned dictionary are meters.

Modes not in the capacity model still depend on this geometry. Thin-plate shear
buckling scales roughly as $Et^3/H$ in load; flange local-buckling stress scales
roughly as $E(t_f/w)^2$, where $w=(B-b)/2$ is flange outstand. Web crippling also
depends on nose/support contact geometry that this dataset does not record.'''),
code(SRC_SECTION + 'section_props(2.0, 12.0)'),
md('''## 4. Failure mode: flexural yield

<img src="https://raw.githubusercontent.com/andrewvoss8-boop/core-me-data-science-activities-public/main/me323/Module1_drafts/figures/flexural%20stress%20photo.webp" alt="Flexural stress distribution" width="520">

For a centered load in three-point bending,
$M_{max}=PL/4$. The outer flange fiber reaches yield when
$\\sigma=M_{max}c/I_x=\\sigma_y$:

$$P_{bend}=\\frac{4\\sigma_y I_x}{cL}.$$

This assumes Euler-Bernoulli bending, linear elasticity to first yield,
homogeneous isotropic material, and no local buckling or contact damage.'''),
code('''def P_bend(p, sy):
    return ____    # >>> FILL IN: P_bend; section_props is SI but L is in mm

Pb_check = P_bend(section_props(2.0, 12.0), SY)
assert 750 < Pb_check < 920, (
    f"P_bend(2,12) = {Pb_check:.6g} N is off. Convert L from mm to m.")
print(f"P_bend(2,12) = {Pb_check:.1f} N   (checkpoint: about 835 N)")'''),
md('''## 5. Shear failure: read the fracture notes first

Look at the `failure_note` column. Every non-buckling "shear-type" failure in
this dataset is a **separation of a flange from the web** — a fracture running
*along* the beam at the printed flange-web interface, not a rupture through
the web. That interface is a printed layer line, and the strength along the
layer lines is weaker than through solid material.

The stress that plane carries is the classic built-up-beam **shear flow**: in
either half-span the shear force is $V = P/2$, and the longitudinal shear
transmitted across the flange-web junction is

$$\\tau_j = \\frac{V\\,Q_f}{I_x\\,t_w}, \\qquad
Q_f = B\\,t_f\\,\\frac{H_{web}+t_f}{2},$$

with $Q_f$ the first moment of the *flange alone* and $t_w = b$ the joint
width (the glue-line check for any built-up member). Failure occurs when
$\\tau_j$ reaches the **interface strength** $\\tau_i$:

$$P_{sep} = 2\\,\\tau_i\\,\\frac{I_x\\,t_w}{Q_f}.$$

The stress measure is textbook mechanics. The strength is not: $\\tau_i$ is the
strength along the printed layer lines, weaker than the bulk material, and no
handbook lists it — calibrating it from test data is part of this pre-lab.
Start from the bulk-material guess $\\tau_i = \\sigma_y/\\sqrt{3} = 43.9$ MPa and
let the data argue.'''),
code('''def Q_flange(p):
    return p["B"]*p["tf"]*(p["h"]/2 + p["tf"]/2)     # flange first moment, m^3

def P_sep(p, tau_i):
    return ____    # >>> FILL IN: 2 * tau_i * Ix * t_w / Q_f  (t_w is p["b"])

p = section_props(2.0, 12.0)
Psep_check = P_sep(p, TAU_I)
assert 2600 < Psep_check < 3200, (
    f"P_sep(2,12) = {Psep_check:.6g} N is off. Q_flange and Ix are SI; "
    "expect about 2894 N at the 43.9 MPa starting guess.")
print(f"junction separation limit = {Psep_check:.1f} N   (checkpoint: about 2894 N)")
print("At the bulk-yield guess the junction check never governs -- hold that")
print("thought until the calibration step meets the separation notes.")'''),
md('''## 6. Lateral-torsional buckling

LTB is provided because it carries the most assumptions: elastic warping,
top-flange loading, idealized supports, initial straightness, and an effective
unbraced length $L_b=kL$. Here `k` represents fixture restraint, not a beam
material property. The expression is capped at the flexural-yield moment.'''),
code('''def P_LTB(p, sy, k):
    My = sy*p["Ix"]/p["c"]
    Lb, zg = k*L/1e3, p["c"]
    R = p["Cw"]/p["Iy"] + (Lb**2*G*p["J"])/(np.pi**2*E*p["Iy"]) + (C2*zg)**2
    Mcr = C1*np.pi**2*E*p["Iy"]/Lb**2 * (np.sqrt(R) - C2*zg)
    return 4*min(My, Mcr)/(L/1e3)

def capacity(b, H, sy, k, tau_i):
    """Class model: plain minimum of the three mode capacities."""
    p = section_props(b, H)
    return min(P_bend(p, sy), P_sep(p, tau_i), P_LTB(p, sy, k))

def gov_mode(b, H, sy, k, tau_i):
    """Dominant pure-mode proxy, not an observed failure-mechanism label."""
    p = section_props(b, H)
    Pb, Ps, Pl = P_bend(p, sy), P_sep(p, tau_i), P_LTB(p, sy, k)
    if Ps < min(Pb, Pl):
        return "separation"
    return "LTB" if Pl < 0.999*Pb else "bend"

print(f"capacity(2,16) = {capacity(2, 16, SY, K_LTB, TAU_I):.0f} N, "
      f"dominant-mode proxy = {gov_mode(2, 16, SY, K_LTB, TAU_I)}")'''),
key_md('''### KEY-only: how the LTB assumptions move the answer

The historical educational notebook usefully put a basic LTB model beside a
fixture-aware one. This comparison keeps that idea but uses the current
`B=10 mm`, `T=18 mm`, `L=150 mm` geometry.

The basic model uses full-span `k=1`, thin-strip $J$, no warping term,
shear-center loading, and no yield cap. The current branch uses the
finite-aspect-ratio correction in `section_props`, $C_w$, top-flange loading,
calibrated `k=0.377`, and a flexural-yield cap.

This is an assumption hierarchy, not a truth hierarchy. The current branch is
still an idealized stability model, and `k` absorbs fixture and model-form
effects.'''),
key_code('''def P_LTB_basic(p):
    """Basic elastic LTB: k=1, thin-strip J, no warping/load height/yield cap."""
    Lb = L/1e3
    J_thin = (p["h"]*p["b"]**3 + 2*p["B"]*p["tf"]**3)/3
    R_basic = (Lb**2*G*J_thin)/(np.pi**2*E*p["Iy"])
    Mcr = C1*np.pi**2*E*p["Iy"]/Lb**2 * np.sqrt(R_basic)
    return 4*Mcr/(L/1e3)

SY_KEY, K_KEY, TAU_KEY = «CAL_SY_E», «CAL_K_V», «CAL_TAU_E»
b_key = np.linspace(1.25, 7.0, 90)
H_key = np.linspace(5.0, 16.0, 90)
BB_key, HH_key = np.meshgrid(b_key, H_key)
X_key = np.column_stack([BB_key.ravel(), HH_key.ravel()])

ltb_basic, ltb_current, sw_basic, sw_current = [], [], [], []
for bq, Hq in X_key:
    pq = section_props(bq, Hq)
    Pbq = P_bend(pq, SY_KEY)
    Psq = P_sep(pq, TAU_KEY)
    Pbasic = P_LTB_basic(pq)
    Pcurrent = P_LTB(pq, SY_KEY, K_KEY)
    ltb_basic.append(Pbasic)
    ltb_current.append(Pcurrent)
    sw_basic.append(min(Pbq, Psq, Pbasic)/estimated_mass_g(bq, Hq))
    sw_current.append(min(Pbq, Psq, Pcurrent)/estimated_mass_g(bq, Hq))

ltb_basic = np.asarray(ltb_basic)
ltb_current = np.asarray(ltb_current)
sw_basic = np.asarray(sw_basic)
sw_current = np.asarray(sw_current)

fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), sharex=True, sharey=True)
maps = [
    (ltb_basic, "basic elastic LTB [N]"),
    (ltb_current, "current yield-capped LTB [N]"),
    (ltb_current/ltb_basic, "current / basic LTB load"),
]
for ax, (values, title) in zip(axes, maps):
    cf = ax.contourf(BB_key, HH_key, values.reshape(BB_key.shape), levels=20)
    fig.colorbar(cf, ax=ax)
    ax.set_xlabel("b [mm]"); ax.set_ylabel("H_web [mm]"); ax.set_title(title)
plt.tight_layout(); plt.show()

i_basic = int(np.argmax(sw_basic))
i_current = int(np.argmax(sw_current))
print("Basic-assumption optimum:",
      f"b={X_key[i_basic,0]:.2f}, H_web={X_key[i_basic,1]:.2f}, "
      f"str/w={sw_basic[i_basic]:.1f} N/g")
print("Current-assumption optimum:",
      f"b={X_key[i_current,0]:.2f}, H_web={X_key[i_current,1]:.2f}, "
      f"str/w={sw_current[i_current]:.1f} N/g")
print("The exact current class checkpoint uses the finer 0.05 mm grid below.")'''),
md('''## 7. Diagnose the model before fitting it

The plots below use one common scale. Point color is the predicted dominant
mode; marker shape is the observed note category. Beam IDs let you connect
every miss to the full note table.

One data-handling note before you trust the markers: the classifier below reads
the test engineer's free-text notes, which spell separation "seperation" — match
the data, not the dictionary, or the separation beams silently disappear into
the fracture bin. Beam 7 is a mixed case (a complete central fracture plus a
small secondary flange separation); the rule below counts a note as separation
only when it does not also report a complete central fracture.'''),
code('''def observed_note_class(note):
    s = str(note).lower()
    # the notes spell it "seperation" -- match the data, not the dictionary;
    # a note that also reports a complete central fracture counts as fracture
    is_sep = ("separ" in s) or ("seper" in s) or ("peel" in s)
    if is_sep and "vertical fracture across" not in s:
        return "flange-web separation"
    if any(word in s for word in ("flip", "tip", "twist", "buckl")):
        return "tip/twist"
    if "fract" in s or "vertical" in s:
        return "fracture"
    return "other"

MODE_ORDER = ["bend", "separation", "LTB"]
MODE_COLOR = {"bend": "tab:blue", "separation": "tab:orange", "LTB": "tab:red"}
OBS_MARKER = {"fracture": "o", "flange-web separation": "s", "tip/twist": "^", "other": "D"}
from matplotlib.lines import Line2D

def diagnostic_plots(sy, k, tau_i, label):
    d = df.copy()
    d["predicted_N"] = [capacity(b, H, sy, k, tau_i) for b, H in zip(d.b, d.H)]
    d["mode_proxy"] = [gov_mode(b, H, sy, k, tau_i) for b, H in zip(d.b, d.H)]
    d["observed_class"] = d.failure_note.map(observed_note_class)
    d["residual_pct"] = 100*(d.predicted_N/d.strength_N - 1)
    hi = 1.08*max(d.predicted_N.max(), d.strength_N.max())
    fig, axes = plt.subplots(1, 4, figsize=(17, 4.2), sharex=True, sharey=True)
    panels = [("all beams", d)] + [(mode, d[d.mode_proxy == mode]) for mode in MODE_ORDER]
    for ax, (title, sub) in zip(axes, panels):
        for _, row in sub.iterrows():
            ax.scatter(row.predicted_N, row.strength_N, s=70,
                       c=MODE_COLOR[row.mode_proxy],
                       marker=OBS_MARKER[row.observed_class], edgecolor="k")
            ax.annotate(str(int(row.beam_id)), (row.predicted_N, row.strength_N),
                        xytext=(4, 3), textcoords="offset points", fontsize=8)
        ax.plot([0, hi], [0, hi], "k--", alpha=0.5)
        ax.set_title(title); ax.set_xlabel("predicted [N]")
        ax.grid(alpha=0.25); ax.set_xlim(0, hi); ax.set_ylim(0, hi)
        if sub.empty:
            ax.text(0.5, 0.5, "no beams", transform=ax.transAxes, ha="center")
    axes[0].set_ylabel("measured [N]")
    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=color,
               markeredgecolor="k", label=f"predicted: {mode}")
        for mode, color in MODE_COLOR.items()
    ] + [
        Line2D([0], [0], marker=marker, color="k", linestyle="none",
               markerfacecolor="white", label=f"observed: {obs}")
        for obs, marker in OBS_MARKER.items()
    ]
    axes[0].legend(handles=legend_handles, fontsize=6, loc="lower right")
    fig.suptitle(f"{label}: sigma_y={sy/1e6:.1f} MPa, k={k:.3f}, tau_i={tau_i/1e6:.1f} MPa")
    plt.tight_layout(); plt.show()
    cols = ["beam_id", "b", "H", "strength_N", "predicted_N", "residual_pct",
            "mode_proxy", "observed_class", "failure_note"]
    print(d[cols].round({"b": 2, "H": 2, "strength_N": 1,
                         "predicted_N": 1, "residual_pct": 1}).to_string(index=False))
    mape = d.residual_pct.abs().mean()
    print(f"\\n{label} MAPE = {mape:.1f}%")
    return d, float(mape)

diag_nominal, mape_nom = diagnostic_plots(SY, K_LTB, TAU_I, "Nominal handbook parameters")
df["cap_nominal"] = diag_nominal.predicted_N
print(f"CHECKPOINT: nominal error should be about «MAPE_NOM»% MAPE.")'''),
md('''## 8. Tune by hand before optimizing

Change the three values and rerun this cell. Try to improve the parity plot,
but watch which failure notes and predicted modes each change helps or hurts.

- `TRY_SY_MPA` moves the flexural-yield side.
- `TRY_K` mostly moves the LTB-limited beams.
- `TRY_TAU_MPA` moves only the separation limit -- watch beams 12 and 14, the
  two whose notes say a flange separated from the web (beam 7 shows a partial,
  secondary separation after its central fracture).'''),
code('''TRY_SY_MPA = 76.0    # edit
TRY_K = 0.33         # edit
TRY_TAU_MPA = 43.9   # edit -- the printed-interface strength guess

diag_try, mape_try = diagnostic_plots(
    TRY_SY_MPA*1e6, TRY_K, TRY_TAU_MPA*1e6, "Your trial parameters")'''),
md('''## 9. Calibrate the three parameters

Now automate the search. The loss is mean squared log-error, so comparable
percentage misses receive comparable weight:

$$L(\\sigma_y,k,\\tau_i)=\\frac{1}{14}\\sum_{i=1}^{14}
\\left(\\ln P_{pred,i}-\\ln P_{meas,i}\\right)^2.$$

Fill in the loss. A coarse search and Nelder-Mead polish are provided.'''),
code('''from scipy.optimize import minimize

def loss(theta):
    sy, k, tau_i = theta
    if not (30e6 < sy < 150e6 and 0.05 < k < 1.5 and 3e6 < tau_i < 45e6):
        return 1e9
    pred = np.array([capacity(b, H, sy, k, tau_i) for b, H in zip(df.b, df.H)])
    return ____    # >>> FILL IN: mean squared difference of log predictions and measurements

grid = [(sy, k, ti) for sy in np.linspace(55e6, 100e6, 19)
        for k in np.linspace(0.10, 0.90, 17)
        for ti in (8e6, 12e6, 17.5e6, 25e6, 43.9e6)]
theta0 = min(grid, key=loss)
res = minimize(loss, theta0, method="Nelder-Mead",
               options=dict(xatol=1e-4, fatol=1e-10, maxiter=4000))
SY_CAL, K_CAL, TAU_CAL = res.x
diag_cal, mape_cal = diagnostic_plots(SY_CAL, K_CAL, TAU_CAL, "Calibrated parameters")
df["cap_cal"] = diag_cal.predicted_N
print(f"calibrated: sigma_y = {SY_CAL/1e6:.1f} MPa, k = {K_CAL:.3f}, "
      f"tau_i = {TAU_CAL/1e6:.2f} MPa")
print(f"CHECKPOINT: sigma_y = «CAL_SY_MPA» MPa, k = «CAL_K_V», tau_i = «CAL_TAU_MPA» MPa, "
      f"error = «MAPE_CAL»% MAPE. Your error: {mape_cal:.1f}%.")
print("tau_i lands FAR below the 43.9 MPa bulk guess: the bond along the")
print("printed layer lines, not the bulk plastic, is what fails. That number")
print("exists in no handbook.")'''),
md('''Do not read a fitted parameter as a direct material measurement. Decide
whether each change corrects a plausible numerical assumption or compensates
for missing physics. The failure-note table is evidence for that distinction.'''),
md('''## 10. Optimize the equation design

Search the design box for the best predicted strength-to-weight under the
calibrated empirical model. Fill in the objective.'''),
code('''best = (None, None, -1)
for b in np.arange(1.25, 7.01, 0.05):
    for H in np.arange(5.0, 16.01, 0.05):
        cap = capacity(b, H, SY_CAL, K_CAL, TAU_CAL)
        sw = ____    # >>> FILL IN: predicted capacity per estimated gram
        if sw > best[2]:
            best = (round(b, 2), round(H, 2), sw)
b_eq, H_eq, sw_eq = best
mode_cal = gov_mode(b_eq, H_eq, SY_CAL, K_CAL, TAU_CAL)
mode_nom = gov_mode(b_eq, H_eq, SY, K_LTB, TAU_I)
p_eq = section_props(b_eq, H_eq)
print(f"EQUATION DESIGN: b={b_eq} mm, H_web={H_eq} mm, predicted {sw_eq:.1f} N/g")
print(f"dominant-mode proxy at this geometry: calibrated={mode_cal}, nominal={mode_nom}")
print("mode capacities at the optimum, calibrated: "
      f"P_bend={P_bend(p_eq, SY_CAL):.0f} N, "
      f"P_sep={P_sep(p_eq, TAU_CAL):.0f} N, "
      f"P_LTB={P_LTB(p_eq, SY_CAL, K_CAL):.0f} N")
print("CHECKPOINT: b = «EQ_B_CK», H_web = «EQ_H_CK», predicted «EQ_PRED» N/g.")'''),
md('''Staff query one common equation design through the frozen oracle. The
returned strength appears at the start of Pre-lab 2.

## Memo questions

1. Compare measured and estimated masses. Name one physical reason they differ,
   and explain why the pre-print optimizer still uses estimated mass.
2. The final cell prints the dominant-mode proxy and all three mode capacities
   at the equation design. How close is the runner-up mode? What does that
   margin (or lack of one) say about how literally to read a single proxy
   label at an optimum found by maximizing a minimum of surfaces?
3. For $\\sigma_y$, `k`, and $\\tau_i$, decide whether calibration is a
   correction to a number or the measurement of a property no handbook has.
   Cite specific residuals and failure notes from the diagnostic table.
4. The optimum sits at minimum `b`, where predicted str/w still increases as
   the web thins. Which observed failures should reduce your trust there?

Use the final design output, the nominal/calibrated plots, and beam IDs with
their full failure notes. No additional optimization code is required.'''),
key_md('''## KEY: memo targets

1. Measured mass includes print and measurement variation; estimated mass is a
   nominal-geometry quantity available before printing. Students should not
   silently mix denominators when comparing str/w.
2. At the calibrated optimum the printed bend and LTB capacities land within
   about 1% of each other; the "bend" label is an artifact of the 0.999
   tie-break threshold. Optimizing a min() of capacity surfaces drives the
   design toward mode intersections — exactly where a single proxy label
   deserves the least trust. Treat the label as a dominant-mode proxy, not an
   observed fracture diagnosis.
3. A defensible reading is: effective $\\sigma_y$ is partly a correction for
   printed material versus a handbook coupon; `k` is a fixture correction but
   also absorbs idealized LTB assumptions; $\\tau_i$ is neither -- it is the
   *measurement* of a real printed-interface property that no handbook lists
   (the faculty model-selection study back-calculates it at 15-21 MPa across
   the campaign separations, CoV 15%).
4. The thin-web flange-web-separation notes are the direct warning. The model
   has no joint-separation or local plate-failure equation, so an edge optimum
   is extrapolation into its weakest physics.'''),
]

# =========================== PRE-LAB 2 =============================================
P2 = [
md(f'''# Pre-lab 2: Vanilla Gaussian Processes and the Class GP Design
### ME 323 Module 1

<img src="https://raw.githubusercontent.com/andrewvoss8-boop/core-me-data-science-activities-public/main/me323/Module1_drafts/figures/I_beam_dimensions.jpg" alt="I-beam dimensions" width="240">

The equation beam from Pre-lab 1, `(b={EQ_B}, H_web={EQ_H})`, was predicted at
«EQ_PRED» N/g. The class query returned **{EQ_N} N**, or **{EQ_SW} N/g on the same
estimated-mass basis**. It is the best of the first 15 beams, beating the
original best-of-14 value of «BEST_SW2» N/g. The returned ratio is
«EQ_BELOW_PCT»% below the equation prediction.

This notebook uses only data-driven, vanilla GPs. You will compare reasonable
setup choices, separate epistemic uncertainty from observation noise, use MUI
and EI, and then apply one locked recipe so the class submits one common beam.'''),
code(SRC_CONST + SRC_LOAD + f'''
eq_beam = pd.DataFrame([dict(beam_id=15, b={EQ_B}, H={EQ_H}, strength_N={EQ_N},
                             weight_g=np.nan,
                             mass_est_g=estimated_mass_g({EQ_B}, {EQ_H}),
                             failure_note="class equation beam")])
df = pd.concat([df, eq_beam], ignore_index=True)
df["str_to_weight"] = df.strength_N / df.mass_est_g
initial_best = df.loc[df.beam_id <= 14, "str_to_weight"].max()
assert {EQ_SW} > initial_best
print(f"{{len(df)}} beams; original best={{initial_best:.2f}} N/g; "
      f"equation beam={EQ_SW:.2f} N/g, now ranked #1")
pd.set_option("display.max_colwidth", None)
print("\\nObserved failure notes carried into the GP decision:")
print(df.loc[df.beam_id <= 14, ["beam_id", "b", "H", "failure_note"]]
      .to_string(index=False))'''),
md('''## 1. What choices define a vanilla GP?

A surrogate maps `(b, H_web)` to a performance prediction without using the
failure equations. For a raw target, the GP mean is the central prediction.
For the official log target, `exp(mu_log)` is the posterior median in N/g, not
the arithmetic mean.

- Target: raw str/w or log str/w. Log space makes relative errors and
  multiplicative print scatter more natural.
- Input scale: raw millimeters or standardized coordinates. Scaling changes
  what one numerical unit of distance means to the kernel.
- Kernel: RBF assumes a very smooth response; Matérn-5/2 permits less smooth
  variation.
- Length scales: separate ARD scales let `b` and `H_web` vary independently, while
  one shared scale is more strongly regularized.
- `alpha`: assumed aleatory observation variance. It is not the GP's
  reducible epistemic uncertainty.

The comparisons below change one choice at a time. None uses physics features.'''),
code('''from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel as C, RBF, Matern

X = df[["b", "H"]].values.astype(float)
sw_obs = df.str_to_weight.values.astype(float)
bg = np.linspace(1.25, 7.0, 60); Hg = np.linspace(5.0, 16.0, 60)
BB, HH = np.meshgrid(bg, Hg)
Xg = np.column_stack([BB.ravel(), HH.ravel()])

def fit_vanilla_option(target="log", scale=True, kernel_name="RBF",
                       ard=True, noise=0.03):
    fmu = X.mean(0) if scale else np.zeros(2)
    fsd = X.std(0) + 1e-12 if scale else np.ones(2)
    Xfit = (X-fmu)/fsd
    response = np.log(sw_obs) if target == "log" else sw_obs
    ymean = response.mean()
    length0 = [1.0, 1.0] if ard else 1.0
    bounds = (0.1, 30.0) if scale else (0.05, 50.0)
    base = RBF(length0, bounds) if kernel_name == "RBF" else Matern(
        length0, bounds, nu=2.5)
    kernel = C(1.0, (1e-3, 1e3))*base
    alpha = noise**2 if target == "log" else (noise*response.mean())**2
    gp_ = GaussianProcessRegressor(
        kernel, alpha=alpha, normalize_y=False,
        n_restarts_optimizer=5, random_state=0).fit(Xfit, response-ymean)
    return dict(gp=gp_, fmu=fmu, fsd=fsd, ymean=ymean, target=target,
                scale=scale, kernel_name=kernel_name, ard=ard, noise=noise)

def predict_option(model, Xq):
    mu, sd = model["gp"].predict(
        (np.asarray(Xq)-model["fmu"])/model["fsd"], return_std=True)
    centered = mu + model["ymean"]
    central_sw = np.exp(centered) if model["target"] == "log" else centered
    return central_sw, sd

def physical_length_scales(model):
    ls = np.atleast_1d(model["gp"].kernel_.k2.length_scale).astype(float)
    if ls.size == 1:
        ls = np.repeat(ls, 2)
    return ls*model["fsd"] if model["scale"] else ls

OPTION_SPECS = [
    ("official: log, scaled, RBF, ARD", dict()),
    ("raw target only", dict(target="raw")),
    ("unscaled inputs only", dict(scale=False)),
    ("Matern-5/2 only", dict(kernel_name="Matern")),
    ("shared scale only", dict(ard=False)),
]
option_models = [(name, fit_vanilla_option(**kw)) for name, kw in OPTION_SPECS]
for name, model in option_models:
    print(f"{name}\\n  {model['gp'].kernel_}\\n"
          f"  physical length scales [b,H] = {physical_length_scales(model).round(3)} mm")
'''),
md('''## 2. Compare setup choices on the same axes

These are not five independent truths. They are five posterior surfaces from
the same 15 observations under different modeling assumptions.'''),
code('''option_means = [predict_option(model, Xg)[0].reshape(BB.shape)
                for _, model in option_models]
vmin = min(z.min() for z in option_means); vmax = max(z.max() for z in option_means)
fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=True, sharey=True)
for ax, (name, _), Z in zip(axes.flat, option_models, option_means):
    cf = ax.contourf(BB, HH, Z, levels=np.linspace(vmin, vmax, 21),
                     vmin=vmin, vmax=vmax)
    ax.scatter(df.b, df.H, c="white", edgecolor="black", s=35)
    ax.set_title(name, fontsize=9)
    ax.set_xlabel("b [mm]"); ax.set_ylabel("H_web [mm]")
axes.flat[-1].axis("off")
fig.colorbar(cf, ax=axes.ravel().tolist(), label="central prediction str/w [N/g]")
plt.show()'''),
md('''## 3. Lock the class predictive model

From here onward, reset to the official recipe: standardized `(b,H_web)`, centered
log str/w, RBF with separate length scales, 3% relative noise, fixed optimizer
seed. This keeps the class result reproducible.'''),
code('''fmu, fsd = X.mean(0), X.std(0) + 1e-12
y = np.log(sw_obs); ymean = y.mean()
def official_kernel():
    return C(1.0, (1e-3, 1e3))*RBF([1.0, 1.0], (1e-1, 30.0))
kernel = official_kernel()
gp = GaussianProcessRegressor(
    kernel, alpha=0.03**2, normalize_y=False,
    n_restarts_optimizer=5, random_state=0).fit((X-fmu)/fsd, y-ymean)
mu_c, std = gp.predict((Xg-fmu)/fsd, return_std=True)
MU = np.exp(mu_c+ymean).reshape(BB.shape)
STD = std.reshape(BB.shape)
ls_std = np.asarray(gp.kernel_.k2.length_scale, float)
ls_mm = ls_std*fsd
print("fitted official kernel:", gp.kernel_)
print(f"physical length scales: b={ls_mm[0]:.2f} mm, H_web={ls_mm[1]:.2f} mm")
print("checkpoint kernel: roughly «P2_KERNEL»")

fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
for a, Z, title in [(ax[0], MU, "posterior median str/w [N/g]"),
                    (ax[1], STD, "epistemic standard deviation [log units]")]:
    cf = a.contourf(BB, HH, Z, levels=20); fig.colorbar(cf, ax=a)
    a.scatter(df.b, df.H, c="white", edgecolor="black", s=45)
    a.set_xlabel("b [mm]"); a.set_ylabel("H_web [mm]"); a.set_title(title)
plt.tight_layout(); plt.show()'''),
md('''The fitted length scale is much longer in `b` than in `H_web`, so the surface
changes mostly with `H_web`. That is an ARD identifiability result from 15 sparse
points, not a plotting-grid bug and not proof that `b` is physically irrelevant.'''),
md('''### Read the 2D posterior through two 1D slices

Let $f(b,H)=\\ln(S/W)$ be the latent log strength-to-weight trend. The GP gives

$$f(\\mathbf{x})\\mid\\mathcal D\\sim
\\mathcal N\\!\\left(\\mu_f(\\mathbf{x}),\\sigma_{epi}^2(\\mathbf{x})\\right).$$

Epistemic uncertainty describes uncertainty about that latent trend and can
shrink when informative tests are added. A future printed and tested beam also
has independent observation scatter $\\epsilon\\sim\\mathcal N(0,r^2)$:

$$y_*=f(\\mathbf{x})+\\epsilon,\\qquad
\\sigma_{total}=\\sqrt{\\sigma_{epi}^2+r^2},\\quad r=0.03.$$

The two cuts below cross at the equation-query point. The inner band is
uncertainty about the latent trend; the outer band predicts one future
observation. Both are conditional on the kernel, noise, and model form.'''),
code('''r_log, z_band = 0.03, 2.0
b_slice = np.linspace(1.25, 7.0, 400)
H_slice = np.linspace(5.0, 16.0, 400)
slices = [
    ("vary b at H_web = 13.20 mm", b_slice,
     np.column_stack([b_slice, np.full_like(b_slice, 13.20)]),
     "b [mm]", 1.25),
    ("vary H_web at b = 1.25 mm", H_slice,
     np.column_stack([np.full_like(H_slice, 1.25), H_slice]),
     "H_web [mm]", 13.20),
]
equation_sw = float(df.loc[df.beam_id.eq(15), "str_to_weight"].iloc[0])
fig, axes = plt.subplots(2, 2, figsize=(12, 7.5))
for col, (title, xplot, Xslice, xlabel, x_anchor) in enumerate(slices):
    mu_slice, sigma_epi = gp.predict((Xslice-fmu)/fsd, return_std=True)
    mu_log = mu_slice + ymean
    median_sw = np.exp(mu_log)
    sigma_total = np.sqrt(sigma_epi**2 + r_log**2)
    lo_epi, hi_epi = (np.exp(mu_log-z_band*sigma_epi),
                      np.exp(mu_log+z_band*sigma_epi))
    lo_total, hi_total = (np.exp(mu_log-z_band*sigma_total),
                          np.exp(mu_log+z_band*sigma_total))
    ax = axes[0, col]
    ax.fill_between(xplot, lo_total, hi_total, alpha=0.18,
                    label="future observation: total uncertainty")
    ax.fill_between(xplot, lo_epi, hi_epi, alpha=0.35,
                    label="latent trend: epistemic uncertainty")
    ax.plot(xplot, median_sw, color="black", label="posterior median")
    ax.scatter(x_anchor, equation_sw, color="red", marker="x", s=70,
               label="oracle-returned equation query")
    ax.set(title=title, xlabel=xlabel, ylabel="str/w [N/g]")
    ax.grid(alpha=0.25)
    ax = axes[1, col]
    ax.plot(xplot, sigma_epi, label=r"$\\sigma_{epi}$")
    ax.axhline(r_log, color="tab:orange", linestyle="--", label=r"$r=0.03$")
    ax.plot(xplot, sigma_total, label=r"$\\sigma_{total}$")
    ax.set(xlabel=xlabel, ylabel="log standard deviation")
    ax.grid(alpha=0.25)
axes[0, 0].legend(fontsize=8)
axes[1, 0].legend(fontsize=8)
plt.tight_layout(); plt.show()

cross = np.array([[1.25, 13.20]])
cross_mu, cross_epi = gp.predict((cross-fmu)/fsd, return_std=True)
cross_total = np.sqrt(cross_epi[0]**2 + r_log**2)
print(f"slice crossing: median={np.exp(cross_mu[0]+ymean):.2f} N/g, "
      f"sigma_epi={cross_epi[0]:.4f}, r={r_log:.4f}, "
      f"sigma_total={cross_total:.4f}")'''),
md('''## 4. Noise: aleatory versus epistemic uncertainty

Refit at 1%, 3%, and 10% assumed relative observation noise. The latent GP
standard deviation is epistemic and can shrink with more informative tests.
Total predictive uncertainty also includes the assumed observation noise:
$\\sigma_{total}=\\sqrt{\\sigma_{epi}^2+r^2}$ in log space.'''),
code('''tested_excl = np.zeros(len(Xg), bool)
for _b, _H in X:
    tested_excl |= (np.abs(Xg[:, 0]-_b) < 0.15) & (np.abs(Xg[:, 1]-_H) < 0.30)

noise_fits, noise_rows = {}, []
fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=True, sharey=True)
for col, pct in enumerate([1, 3, 10]):
    r = pct/100
    g2 = GaussianProcessRegressor(
        official_kernel(), alpha=r**2, normalize_y=False,
        n_restarts_optimizer=5, random_state=0).fit((X-fmu)/fsd, y-ymean)
    m2, s2 = g2.predict((Xg-fmu)/fsd, return_std=True)
    total2 = np.sqrt(s2**2+r**2)
    noise_fits[pct] = (g2, m2, s2)
    i = int(np.argmax(np.where(tested_excl, -np.inf, m2+s2)))
    noise_rows.append(dict(noise_pct=pct, b=Xg[i,0], H_web=Xg[i,1],
                           median_sw=np.exp(m2[i]+ymean),
                           sigma_epistemic=s2[i], sigma_total=total2[i]))
    for row, (Z, label) in enumerate([(s2, "epistemic"), (total2, "total")]):
        cf = axes[row, col].contourf(BB, HH, Z.reshape(BB.shape), levels=20)
        axes[row, col].scatter(df.b, df.H, c="white", edgecolor="black", s=30)
        axes[row, col].set_title(f"{pct}% noise: {label} sigma")
        axes[row, col].set_xlabel("b [mm]")
        axes[row, col].set_ylabel("H_web [mm]")
        fig.colorbar(cf, ax=axes[row, col])
plt.tight_layout(); plt.show()
print(pd.DataFrame(noise_rows).round(3).to_string(index=False))
print("\\nCHECKPOINT: «NOISE_BEHAVIOR»")'''),
md('''A noise value can be a physical repeatability estimate and a regularization
assumption. If the recommendation moves, the action is model-assumption
sensitive. If it does not, that one decision is locally robust; the noise value
is not thereby proven correct.'''),
md('''## 5. MUI and Expected Improvement in the full 2D design box

Maximum Upper Interval uses $a=\\mu+\\psi\\sigma$. Expected Improvement uses

$$EI=(\\mu-y_{best}-\\xi)\\Phi(Z)+\\sigma\\phi(Z),\\quad
Z=\\frac{\\mu-y_{best}-\\xi}{\\sigma}.$$

Both operate in centered log-str/w space here, and both exclude already-tested
designs with the same rule. Fill in one line in each function.'''),
code('''from scipy.stats import norm

def mui(mu, sigma, psi):
    return ____    # >>> FILL IN: mean plus psi times sigma

y_best = np.log(df.str_to_weight).max()-ymean
def ei(mu, sigma, xi=0.0):
    imp = ____    # >>> FILL IN: mean minus best-so-far minus xi
    safe = np.maximum(sigma, 1e-12)
    Z = imp/safe
    return np.where(sigma > 1e-12,
                    imp*norm.cdf(Z)+sigma*norm.pdf(Z), 0.0)

def recommend_mui(psi, mu=mu_c, sigma=std):
    acq = np.where(tested_excl, -np.inf, mui(mu, sigma, psi))
    i = int(np.argmax(acq))
    return Xg[i], np.exp(mu[i]+ymean), sigma[i], acq[i]

def recommend_ei(xi, mu=mu_c, sigma=std):
    acq = np.where(tested_excl, -np.inf, ei(mu, sigma, xi))
    i = int(np.argmax(acq))
    return Xg[i], np.exp(mu[i]+ymean), sigma[i], acq[i]

rows = []
for psi in [0.0, 0.5, 1.0, 2.0, 3.0]:
    x, median, sig, acq = recommend_mui(psi)
    rows.append(dict(method="MUI", dial=psi, b=x[0], H_web=x[1],
                     median_sw=median, sigma_epi=sig, acquisition=acq))
for xi in [0.0, 0.005, 0.01, 0.03, 0.05]:
    x, median, sig, acq = recommend_ei(xi)
    rows.append(dict(method="EI", dial=xi, b=x[0], H_web=x[1],
                     median_sw=median, sigma_epi=sig, acquisition=acq))
acq_table = pd.DataFrame(rows)
print(acq_table.round(3).to_string(index=False))'''),
md('''## 6. See what each acquisition rule values

The predictive model is identical in both panels. Only the acquisition rule
changes.'''),
code('''psi_show, xi_show = 1.0, 0.01
mui_surface = mui(mu_c, std, psi_show).reshape(BB.shape)
ei_surface = ei(mu_c, std, xi_show).reshape(BB.shape)
x_mui, _, _, _ = recommend_mui(psi_show)
x_ei, _, _, _ = recommend_ei(xi_show)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
for ax, Z, title, xrec in [
    (axes[0], mui_surface, f"MUI, psi={psi_show}", x_mui),
    (axes[1], ei_surface, f"EI, xi={xi_show}", x_ei)]:
    cf = ax.contourf(BB, HH, Z, levels=20); fig.colorbar(cf, ax=ax)
    ax.scatter(df.b, df.H, c="white", edgecolor="black", s=40)
    ax.scatter(*xrec, c="red", marker="*", s=170, label="recommendation")
    ax.set_xlabel("b [mm]"); ax.set_ylabel("H_web [mm]")
    ax.set_title(title); ax.legend()
plt.tight_layout(); plt.show()
print(f"MUI psi=1: b={x_mui[0]:.2f}, H_web={x_mui[1]:.2f}")
print(f"EI xi=.01: b={x_ei[0]:.2f}, H_web={x_ei[1]:.2f}")
print("EI checkpoint: b=«EI_B», H_web=«EI_H».")'''),
md('''## 7. Final filter: the one class GP design

You explored alternatives, but the class query must be reproducible. The final
rule is fixed: official ARD-RBF model, 3% noise, MUI with $\\psi=1$, the stated
grid, and the tested-point exclusion rule.'''),
code(f'''x_class, mean_class, sigma_class, _ = recommend_mui(1.0)
print(f"LOCKED CLASS DESIGN: b={{x_class[0]:.2f}} mm, H_web={{x_class[1]:.2f}} mm")
print(f"posterior median={{mean_class:.1f}} N/g, epistemic sigma_log={{sigma_class:.3f}}")
print("CHECKPOINT: b=«MUI1_B», H_web=«MUI1_H», predicted «MUI1_M» N/g.")'''),
key_code(f'''assert abs(x_class[0]-{GP_B}) < 0.06
assert abs(x_class[1]-{GP_H}) < 0.06'''),
key_md('''## KEY-only sensitivity comparison

The official model remains the class rule. The next cell only shows what
regularizing the sparse length-scale problem would change.'''),
key_code('''matern_fixed = GaussianProcessRegressor(
    C(1.0, (1e-3, 1e3))*Matern(
        length_scale=0.25, length_scale_bounds="fixed", nu=2.5),
    alpha=0.03**2, normalize_y=False,
    n_restarts_optimizer=5, random_state=0).fit(
        (X-np.array([1.25, 5.0]))/np.array([5.75, 11.0]), y-ymean)
mm, ss = matern_fixed.predict(
    (Xg-np.array([1.25, 5.0]))/np.array([5.75, 11.0]), return_std=True)
surfaces = [MU, np.exp(mm+ymean).reshape(BB.shape)]
im = int(np.argmax(np.where(tested_excl, -np.inf, mm+ss)))
x_matern = Xg[im]
lo = min(z.min() for z in surfaces); hi = max(z.max() for z in surfaces)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharex=True, sharey=True)
for ax, Z, title, xrec in zip(
        axes, surfaces,
        ["official ARD RBF", "isotropic Matern-5/2, fixed scale=0.25"],
        [x_class, x_matern]):
    cf = ax.contourf(BB, HH, Z, levels=np.linspace(lo, hi, 21), vmin=lo, vmax=hi)
    ax.scatter(df.b, df.H, c="white", edgecolor="black", s=40)
    ax.scatter(*xrec, c="red", marker="*", s=170)
    ax.set_xlabel("b [mm]"); ax.set_ylabel("H_web [mm]"); ax.set_title(title)
fig.colorbar(cf, ax=axes.ravel().tolist(), label="posterior median str/w [N/g]")
plt.show()
print(f"official MUI psi=1 recommendation: {tuple(np.round(x_class, 2))}")
print(f"regularized Matern recommendation: {tuple(np.round(x_matern, 2))}")
print("This comparison changes kernel and length-scale regularization; it is not the class recommendation.")'''),
md(f'''## Memo questions

1. Cite one region where epistemic uncertainty changes the action relative to
   maximizing the posterior median alone. Use the median, epistemic-sigma, and
   acquisition maps.
2. Compare at least two vanilla setup choices from section 2. Which assumption
   changed the surface, and why is that not evidence that one is automatically true?
3. Compare MUI and EI. Do they recommend the same design, and what does each dial value?
4. Why does the locked GP design differ from the equation design? What do the
   failure notes contain that neither scalar-response model uses?
5. Explain whether the noise activity makes the locked recommendation robust
   or assumption-sensitive.

No new design code is required. The final submitted class design is
`(b={GP_B}, H_web={GP_H})` from the locked cell.'''),
key_md('''## KEY: memo targets

1. Accept any map-supported region where a larger epistemic sigma changes the
   acquisition ranking relative to median-only exploitation.
2. Students should identify the one changed assumption and use the printed
   kernels/length scales or common-scale maps as evidence. Sparse-data MLE can
   support materially different surfaces.
3. MUI adds a sigma bonus everywhere; EI weights the probability and amount of
   beating the incumbent. The recommendation table supplies exact comparisons.
4. The equation maximizes its calibrated capacity/mass. The locked GP maximizes
   a data-conditioned upper interval. Failure morphology, layer separation,
   fixture tipping, and fracture progression are absent from both scalar targets.
5. Use the generated 1/3/10% table. Stability of one recommendation is local
   robustness, not validation of the assumed noise or kernel.'''),
]

# =========================== SUBMISSION 1 ==========================================
# the header prose below narrates the equation beam staying best of 16;
# if a re-freeze ever flips the ordering, the text must be rewritten by hand
assert GP_SW < EQ_SW, "S1 header prose assumes the equation beam is still best of 16"

S1 = [
md(f'''# Submission 1: Your Model, Your Beam
### ME 323 Module 1

<img src="https://raw.githubusercontent.com/andrewvoss8-boop/core-me-data-science-activities-public/main/me323/Module1_drafts/figures/I_beam_dimensions.jpg" alt="I-beam dimensions" width="220">

Both common class designs have been queried. The scoreboard so far:

| design | (b, H_web) | predicted | returned strength and str/w on estimated-mass basis |
|---|---|---|---|
| equation-query beam from Pre-lab 1 | ({EQ_B}, {EQ_H}) | «EQ_PRED» N/g | **{EQ_SW} N/g** ({EQ_N} N) |
| locked GP-query beam from Pre-lab 2, MUI ψ=1 | ({GP_B}, {GP_H}) | «MUI1_M» N/g | **{GP_SW} N/g** ({GP_N} N) |

Both beat the original 14-beam best of «BEST_SW2» N/g. The equation beam became
the best of 15 at {EQ_SW} N/g — and it is *still* the best of all 16. The GP
beam returned more raw strength ({GP_N} N vs {EQ_N} N) but spent more mass to
get it, so on the strength-to-weight basis the scoreboard runs on, it slots in
second at {GP_SW} N/g. Relative
to their own predictions, the equation result came in «EQ_BELOW_PCT»% low and the GP
result «GP_VS_PRED_TEXT». Sit with that pair of facts: the
winning beam came from the prediction that missed by «EQ_BELOW_PCT»%, and the
well-calibrated model got beaten. One test settles less than it seems to.

Fold both query results into the data, build a model your way, and commit to a
third design: the beam your group will print. Do not call either common query
beam your Submission 1 design unless you deliberately choose those coordinates.
The final answer is a decision defended in the memo.'''),
md('''## Your knobs

This notebook hands you a working pipeline, but every modeling decision in it
is a variable you set — and each one is an assumption about the world, not a
setting with a known right answer. The full dashboard:

| knob | variable (where) | options | the assumption you are making |
|---|---|---|---|
| model architecture | `CHOICE` (§3) | `"A plain"` / `"B strength"` / `"C features"` / `"D residual"` | how much physics the model gets, and what quantity it learns — §2 |
| prediction target | comes with the lane | str/w directly (lanes A, C, D) or raw strength ÷ mass (lane B) | which quantity is the smoother, easier thing to learn — §2 |
| kernel | `KERNEL` (§3) | `"RBF"` / `"Matern"` | how smooth the true strength surface is — §3 |
| assumed noise | `NOISE_PCT` (§3) | any percent; class default 3 | how much of beam-to-beam scatter is repeatability rather than real shape — §3 |
| acquisition rule | `ACQ` (§4) | `"MUI"` / `"EI"` | how predicted value and uncertainty combine into one pick — §4 |
| explore vs exploit | `psi` (§4, MUI only) | 0 = pure exploit; larger = more explore | how much a *chance* at a better beam is worth against a safe, good one — §4 |

Two kinds of knobs, two ways to choose. Architecture and kernel make claims
the data can score, and the leave-one-out table in §2 is their referee. Noise
and ψ make claims the data *cannot* score: no table can tell you the rig's
repeatability or how much risk your group should carry. Those you defend in
the memo with physical reasoning and stated values.'''),
code(SRC_CONST + SRC_LOAD + f'''
new = pd.DataFrame([
    dict(beam_id=15, b={EQ_B}, H={EQ_H}, strength_N={EQ_N},
         failure_note="equation-query result; observed morphology not supplied"),
    dict(beam_id=16, b={GP_B}, H={GP_H}, strength_N={GP_N},
         failure_note="locked-GP-query result; observed morphology not supplied"),
])
new["weight_g"] = np.nan
new["mass_est_g"] = estimated_mass_g(new.b, new.H)
df = pd.concat([df, new], ignore_index=True)
df["str_to_weight"] = df.strength_N / df.mass_est_g
print(len(df), "beams. best observed:", round(df.str_to_weight.max(), 2), "N/g")
pd.set_option("display.max_colwidth", None)
print("\\nFailure-note evidence available to the design decision:")
print(df[["beam_id", "b", "H", "failure_note"]].to_string(index=False))'''),
md('''## 1. The calibrated physics (carried over from Pre-lab 1)

Provided complete this time, with the class calibration values baked in.'''),
code(SRC_PHYS_FULL + f'''
SY_CAL, K_CAL, TAU_CAL = {CAL_SY:.3e}, {CAL_K}, {CAL_TAU:.3e}   # your Pre-lab 1 calibration
print("calibrated capacity(2,12) =", round(capacity(2, 12, SY_CAL, K_CAL, TAU_CAL), 1), "N")'''),
md('''## 2. Pick a lane: four ways to model the same 16 beams

"Model architecture" here means two choices at once: what the GP sees, and
what quantity it learns.

| lane | what the GP sees | what it predicts |
|---|---|---|
| **A — plain (vanilla GP)** | (b, H_web) | log str/w — the Pre-lab 2 model |
| **B — strength target** | (b, H_web) | log strength; divide by mass afterwards |
| **C — physics features** | (b, H_web, log P_phys, P_LTB/P_bend) | log str/w |
| **D — residual** | (b, H_web) | log(measured / P_phys) — physics first, GP corrects |

What each lane assumes:

- **A — plain (vanilla GP).** A pure pattern-matcher: str/w is a smooth
  function of the two geometry numbers and 16 points are enough to learn it.
  No physics at all — which also means no physics *errors*. Between data
  points it interpolates; far from data it drifts back toward the mean and
  its error bars balloon. That ballooning is honest, and it is also all the
  guidance you get out there.
- **B — strength target.** The same vanilla GP, but it learns raw newtons and
  you divide by estimated mass afterwards. Worth trying if you believe raw
  strength is the smoother surface. The catch: a small percentage error on a
  900 N prediction becomes a large N/g error once you divide by a light
  beam's mass. The LOO table shows how that gamble went here.
- **C — physics features.** The GP still learns str/w, but you hand it two
  extra inputs computed from the calibrated equations: the physics capacity
  and an LTB-to-bending stability ratio. The model can lean on the physics
  where it tracks the data and ignore it where it doesn't — at the cost of
  learning a 4-D input space from the same 16 points.
- **D — residual.** Physics goes first: compute P_phys from the calibrated
  equations, then let the GP learn only the correction factor
  (measured / physics). Where the equations are right the GP has nothing to
  do; where they are biased it learns the bias. This carries physics shape
  into regions with no data — the strongest extrapolator of the four — and it
  inherits every blind spot of the equations, including any mechanism they
  leave out entirely.

**How to discern:** the leave-one-out (LOO) table below scores each lane on a
beam it did not see, sixteen times over — a dress rehearsal for predicting
your un-printed design. Low LOO RMSE is real evidence. It is also 16-point
evidence: a lane that wins by 0.3 N/g is a coin flip; a lane that loses by
3 N/g is genuinely worse. You may overrule the table if you argue the case
(for instance: "D wins LOO, but I am designing near the thin-web region where
its physics is blind to separation").'''),
code('''from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel as C, RBF, Matern

def make_kernel(kernel, ndim):
    """The smoothness assumption, written as code.
    RBF:    infinitely differentiable — believes the strength surface is
            gentle everywhere; can round over a sharp failure-mode handoff.
    Matern: nu = 2.5, twice differentiable — believes the surface may carry
            kinks, e.g. where the governing failure mode changes."""
    if kernel == "RBF":
        return C(1.0, (1e-3, 1e3)) * RBF([1.0]*ndim, (1e-1, 30.0))
    elif kernel == "Matern":
        return C(1.0, (1e-3, 1e3)) * Matern([1.0]*ndim, (1e-1, 30.0), nu=2.5)
    raise ValueError(f"unknown kernel {kernel!r}: use 'RBF' or 'Matern'")

def fit_gp(data, alpha=0.03**2, feats=("b", "H"), target="log_sw", kernel="RBF"):
    """The class GP recipe: z-scored inputs, log target, MLE hyperparameters."""
    X = data[list(feats)].values.astype(float)
    fmu, fsd = X.mean(0), X.std(0) + 1e-12
    if target == "log_sw":
        y = np.log(data.strength_N.values /
                   estimated_mass_g(data.b.values, data.H.values))
    elif target == "log_strength":
        y = np.log(data.strength_N.values.astype(float))
    else:                                    # log residual vs calibrated physics
        Pphys = np.array([capacity(b, H, SY_CAL, K_CAL, TAU_CAL)
                          for b, H in zip(data.b, data.H)])
        y = np.log(data.strength_N.values) - np.log(Pphys)
    ymean = y.mean()
    gp = GaussianProcessRegressor(make_kernel(kernel, X.shape[1]), alpha=alpha,
                                  normalize_y=False,
                                  n_restarts_optimizer=5, random_state=0)
    gp.fit((X - fmu) / fsd, y - ymean)
    return gp, fmu, fsd, ymean

def predict_sw(gp, fmu, fsd, ymean, bq, Hq, target, feats):
    Xq = build_feats(bq, Hq, feats)
    mu, sd = gp.predict((Xq - fmu)/fsd, return_std=True)
    mu = mu + ymean
    mass = estimated_mass_g(np.asarray(bq, float), np.asarray(Hq, float))
    if target == "log_sw":
        sw = np.exp(mu)
    elif target == "log_strength":
        sw = np.exp(mu)/mass
    else:
        Pphys = np.array([capacity(b, H, SY_CAL, K_CAL, TAU_CAL)
                          for b, H in zip(np.atleast_1d(bq), np.atleast_1d(Hq))])
        sw = Pphys*np.exp(mu)/mass
    return sw, sd

def build_feats(bq, Hq, feats):
    bq, Hq = np.atleast_1d(np.asarray(bq, float)), np.atleast_1d(np.asarray(Hq, float))
    cols = {"b": bq, "H": Hq}
    if "logP" in feats or "stab" in feats:
        pp = [section_props(b, H) for b, H in zip(bq, Hq)]
        Pb = np.array([P_bend(p, SY_CAL) for p in pp])
        Pl = np.array([P_LTB(p, SY_CAL, K_CAL) for p in pp])
        Ps = np.array([P_sep(p, TAU_CAL) for p in pp])
        cols["logP"] = np.log(np.minimum(Pb, np.minimum(Ps, Pl)))
        cols["stab"] = Pl/Pb
    return np.column_stack([cols[f] for f in feats])

LANES = {
    "A plain":    dict(feats=("b", "H"), target="log_sw"),
    "B strength": dict(feats=("b", "H"), target="log_strength"),
    "C features": dict(feats=("b", "H", "logP", "stab"), target="log_sw"),
    "D residual": dict(feats=("b", "H"), target="log_residual"),
}

def fit_lane(data, lane, alpha=0.03**2, kernel="RBF"):
    cfg = LANES[lane]
    d2 = data.copy()
    Xf = build_feats(d2.b.values, d2.H.values, cfg["feats"])
    for j, f in enumerate(cfg["feats"]):
        d2[f] = Xf[:, j]
    gp, fmu, fsd, ymean = fit_gp(d2, alpha=alpha, feats=cfg["feats"],
                                 target=cfg["target"], kernel=kernel)
    return gp, fmu, fsd, ymean, cfg

print("leave-one-out RMSE in str/w space (lower is better):")
for kernel in ("RBF", "Matern"):
    print(f"  kernel = {kernel}")
    for lane in LANES:
        errs = []
        for i in range(len(df)):
            tr = df.drop(df.index[i])
            gp_, fmu_, fsd_, ym_, cfg_ = fit_lane(tr, lane, kernel=kernel)
            sw_hat, _ = predict_sw(gp_, fmu_, fsd_, ym_, df.b.iloc[i], df.H.iloc[i],
                                   cfg_["target"], cfg_["feats"])
            errs.append(sw_hat[0] - df.str_to_weight.iloc[i])
        print(f"    {lane}: {np.sqrt(np.mean(np.array(errs)**2)):.2f} N/g")
print("\\nCHECKPOINT (RBF):    roughly «LOO_RBF».")
print("CHECKPOINT (Matern): roughly «LOO_MATERN».")
print("If your numbers are far off, check your work or talk to a TA.")'''),
md('''## 3. Rebuild the maps with your knobs

Three knobs live in the next cell. Set them, refit on all 16 beams, and look
at the surfaces you will decide from.

**`KERNEL` — how smooth do you believe the strength surface is?**
The kernel is the GP's smoothness assumption; `make_kernel` above is where it
becomes code.

- `"RBF"` assumes an infinitely smooth surface: strength varies gently, and
  each data point says a lot about its whole neighborhood. If the truth has a
  crease — say, where the governing failure mode hands off from bending to
  flange-web separation — RBF rounds it over.
- `"Matern"` (ν = 2.5) assumes less: the surface may carry kinks, and a data
  point speaks a bit less confidently about its neighbors.

How to discern: the LOO table in §2 now scores both kernels, so start there —
remembering the 16-point caveat. Then ask whether you believe this surface
*has* a crease: the failure-note table says different beams died by different
mechanisms, which is an argument that it does.

**`NOISE_PCT` — how much of the scatter do you trust?**
The GP receives `alpha = (NOISE_PCT/100)**2` in log space, which reads as:
"an identical beam, printed and tested again, comes back within roughly
NOISE_PCT percent." Small values force the fit to thread every data point —
every wiggle is treated as real shape. Large values let it smooth through
them — much of the wiggle is print luck and rig luck. No cell in this
notebook can compute the right value: the 16 beams contain no repeated
geometry, so the data cannot measure its own error bar. This knob is an
assumption. The honest move is to state your number, and to know what it did
to your answer — try 1 and 8 and watch where the recommendation moves before
you commit.'''),
code('''CHOICE    = "A plain"   # <<< your lane:   "A plain" | "B strength" | "C features" | "D residual"
KERNEL    = "RBF"       # <<< your smoothness assumption: "RBF" | "Matern"
NOISE_PCT = 3           # <<< your assumed repeatability, percent

gpF, fmuF, fsdF, ymF, cfgF = fit_lane(df, CHOICE, alpha=(NOISE_PCT/100)**2,
                                      kernel=KERNEL)
bg = np.linspace(1.25, 7.0, 60); Hg = np.linspace(5.0, 16.0, 60)
BB, HH = np.meshgrid(bg, Hg)
SWg, SDg = predict_sw(gpF, fmuF, fsdF, ymF, BB.ravel(), HH.ravel(),
                      cfgF["target"], cfgF["feats"])
MU, STD = SWg.reshape(BB.shape), SDg.reshape(BB.shape)

fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
for a, Z, t in [(ax[0], MU, f"posterior median str/w: {CHOICE}, {KERNEL}"),
                (ax[1], STD, "epistemic uncertainty (log units)")]:
    cf = a.contourf(BB, HH, Z, levels=20); fig.colorbar(cf, ax=a)
    a.scatter(df.b, df.H, c="w", edgecolor="k", s=40)
    a.scatter(df.b.iloc[-2:], df.H.iloc[-2:], c="red", marker="*", s=170,
              label="the two class beams")
    a.set_xlabel("b [mm]"); a.set_ylabel("H_web [mm]"); a.set_title(t); a.legend(fontsize=7)
plt.tight_layout(); plt.show()'''),
md(f'''## 4. Choose your beam *(you write this — graded on the memo, not a checkpoint)*

The maps give you two numbers at every candidate design: `MU`, the predicted
str/w, and `STD`, how unsure the model is there (log units). An *acquisition
rule* collapses the two maps into one pick. Two rules are wired in:

- **`ACQ = "MUI"` — maximum upper improvement.**
  `score = log(MU) + psi*STD`: judge every design by its optimistic upper
  bound. `psi` is the explore–exploit dial, and it is yours to set.
  `psi = 0` ignores uncertainty and picks the best posterior median — pure
  exploitation. `psi = 1` credits each design one sigma of upside. Large
  `psi` chases the unexplored corners of the map. There is no correct value:
  ψ prices how much a *chance* at a better beam is worth to your group
  against a safe, good one.
- **`ACQ = "EI"` — expected improvement.** Averages the improvement over the
  incumbent best tested beam ({EQ_SW} N/g) under the model's own uncertainty.
  No dial: it trades explore against exploit automatically, and it goes to
  zero wherever the model is confident nothing beats the incumbent.

How to discern: pick MUI when you want the risk dial in your own hands and
are prepared to defend a ψ in the memo; pick EI when you would rather let the
model's probabilities make the trade — and defend *that* delegation instead.
With the default lane, kernel, and noise, both rules land on the same beam;
if your knob settings make them split, the disagreement itself is worth a
memo sentence.

Whatever the rule says, you hold a veto. The calibrated physics (`capacity`)
and the failure-note table are also in front of you — the standard move is to
strike regions the notes make you distrust (which beams peeled apart, and
where?).

For orientation only: the *default* recipe — lane A, RBF, 3% noise, MUI
ψ = 1 — lands at **(b ≈ «DEF_B», H_web ≈ «DEF_H»)**. You are free to submit
that; you are also free to beat it. Say why either way.

One deliberate difference from Pre-lab 2: the class-query steps *excluded*
already-tested designs, because a shared oracle query spent on a known point is
wasted. Your print is yours to spend, so the default recipe above applies no
such exclusion«DEF_NEAR_TXT». If you choose a design within the Pre-lab 2
exclusion radius (|Δb| < 0.15, |ΔH_web| < 0.30) of a tested beam, say in the
memo what a near-replicate print buys you — verifying a suspiciously good
result is a legitimate answer; sleepwalking into a repeat is not.'''),
code('''from scipy.stats import norm

ACQ = "MUI"          # <<< your rule: "MUI" | "EI"
psi = 1.0            # <<< your explore-exploit dial (MUI only): 0 = pure exploit

if ACQ == "MUI":
    score = np.log(MU) + psi*STD              # optimistic upper bound, log space
elif ACQ == "EI":
    best = np.log(df.str_to_weight.max())     # incumbent: best tested str/w
    z = (np.log(MU) - best) / STD
    score = STD * (z*norm.cdf(z) + norm.pdf(z))
else:
    raise ValueError(f"unknown ACQ {ACQ!r}: use 'MUI' or 'EI'")

i = np.unravel_index(np.argmax(score), score.shape)
b_final, H_final = float(BB[i]), float(HH[i])
print(f"FINAL DESIGN ({ACQ}):  b = {b_final:.2f} mm,  H_web = {H_final:.2f} mm")
print(f"  posterior median {MU[i]:.1f} N/g,  epistemic sigma_log {STD[i]:.3f},  "
      f"calibrated physics {capacity(b_final, H_final, SY_CAL, K_CAL, TAU_CAL)/estimated_mass_g(b_final, H_final):.1f} N/g")
print(f"  physics mode there: {gov_mode(b_final, H_final, SY_CAL, K_CAL, TAU_CAL)}")'''),
md('''## Memo

1. The two class beams: use the generated scoreboard percentages, with their
   stated denominators. What does each miss reveal, and which miss is costlier
   for the intended design decision?
2. Your lane and kernel: what did the LOO table say under both kernels, and
   did you follow it? If you chose C or D, what does physics contribute
   between the observations?
3. Risk: name your acquisition rule (`ACQ`, plus `psi` if MUI) and your
   `NOISE_PCT`, and use the printed posterior median, epistemic sigma, and
   final coordinates to explain whether you exploited or explored. Is the
   main risk a weak beam or a model that is confidently wrong?
4. Limits: compare your coordinates with the thin-web flange-web-separation
   notes. Where could that unmodeled mechanism affect your design?

The default-parameter design is already computed by the section-4 code. You do
not need a new optimization cell unless you choose a different decision rule.'''),
key_md('''## KEY: memo targets

1. The scoreboard supplies the actual errors. Overprediction is a capacity-risk
   problem; underprediction is usually a mass/opportunity-cost problem. A strong
   answer distinguishes the denominator instead of comparing ambiguous
   percentages — and notices that the best beam of 16 came from the model with
   the larger miss.
2. Report the generated LOO ordering and at least one beam-level miss. The lane
   ordering holds under both kernels (D residual best at «LOO_D_RBF» RBF /
   «LOO_D_MAT» Matérn; B strength worst at «LOO_B_RBF» / «LOO_B_MAT»). Matérn
   helps the residual lane a little and hurts the plain lane a little; a strong
   answer ties the kernel choice to a belief about failure-mode creases in the
   surface rather than treating 0.1–0.3 N/g LOO differences as decisive.
   Following the lowest RMSE is acceptable but not mandatory if the model-risk
   argument is specific. Physics-informed lanes carry shape outside the data
   but also inherit the calibrated capacity model's omissions (no local plate
   buckling or web crippling, and a single-number τ_i standing in for a
   scattered interface strength).
3. The final cell prints all required evidence. Larger `psi` spends more of the
   decision on epistemic uncertainty. Note for grading: at the default lane,
   kernel, and noise, MUI ψ=1 and EI select the same point (b ≈ «DEF_B»,
   H_web ≈ «DEF_H»), so "I used EI" is not by itself a differentiated decision —
   credit students who explain *why* their rule picked what it did, and who
   know what their `NOISE_PCT` assumption did to the maps. The serious risk is
   confident extrapolation into an unmodeled failure region.
4. Flange-web separation occurs in thin-web examples and is absent from the
   yield/LTB equations. Students should locate their design relative to those
   beams rather than claim the mode is impossible.'''),
]

# =========================== SUBMISSION 2 ==========================================
S2 = [
md('''# Submission 2: Reflection and the Lightweight Challenge
### ME 323 Module 1

<img src="https://raw.githubusercontent.com/andrewvoss8-boop/core-me-data-science-activities-public/main/me323/Module1_drafts/figures/I_beam_dimensions.jpg" alt="I-beam dimensions" width="220">

Your beam has been printed and tested. Three jobs here:

1. Recall the module's ideas from memory.
2. Reflect on your measured result against your recorded prediction.
3. Design the lightest beam that confidently clears 700 N.
4. Refit the model with your own result and see what it changes.'''),
md('''## 0. Recall

Write before computing. Corrections earn credit; unsupported bluffing does not.

1. Name the three modeled capacity branches and explain how the dominant-mode
   proxy is assigned. Which region of the (b, H_web) box does each own?
2. Pre-lab 1 calibrated σ_y, k, and τ_i. For each: was it a correction or a
   confession? (One sentence each.)
3. Distinguish epistemic, aleatory, and total predictive uncertainty. Which
   sigma drives explore-vs-exploit, and which belongs in a future-beam bound?
4. The equation query returned below its prediction; the GP query returned
   above its central prediction. Give one plausible reason for each miss.
5. Name the four modeling lanes from Submission 1 and the one-line idea of each.'''),
md('''## 1. Your beam's test result'''),
code(SRC_CONST + SRC_LOAD + f'''
new = pd.DataFrame([
    dict(beam_id=15, b={EQ_B}, H={EQ_H}, strength_N={EQ_N},
         failure_note="equation-query result; observed morphology not supplied"),
    dict(beam_id=16, b={GP_B}, H={GP_H}, strength_N={GP_N},
         failure_note="locked-GP-query result; observed morphology not supplied"),
])
new["weight_g"] = np.nan
new["mass_est_g"] = estimated_mass_g(new.b, new.H)
df = pd.concat([df, new], ignore_index=True)
df["str_to_weight"] = df.strength_N / df.mass_est_g

# >>> ENTER your group's final design and its measured result:
b_mine, H_mine = None, None        # your Submission 1 design (mm)
P_mine = None                      # measured failure load (N)
mass_measured_mine = None          # measured printed-beam mass (g)
note_mine = ""                     # what the failure looked like
pred_median_sw = None              # copy model central prediction from Submission 1
pred_sigma_log = None              # copy epistemic sigma_log from Submission 1
if None not in (b_mine, H_mine, P_mine, mass_measured_mine,
                pred_median_sw, pred_sigma_log):
    mass_est_mine = estimated_mass_g(b_mine, H_mine)
    sw_mine_model_basis = P_mine / mass_est_mine
    sw_mine_measured_mass = P_mine / mass_measured_mine
    sigma_total_log = np.sqrt(pred_sigma_log**2 + 0.03**2)
    pred_lo_sw = pred_median_sw*np.exp(-2*sigma_total_log)
    pred_hi_sw = pred_median_sw*np.exp(2*sigma_total_log)
    inside_2sigma = pred_lo_sw <= sw_mine_model_basis <= pred_hi_sw
    print(f"your beam: ({{b_mine}}, {{H_mine}}), {{P_mine}} N")
    print("  observed failure note:", note_mine)
    print(f"  measured mass={{mass_measured_mine:.2f}} g; "
          f"estimated mass={{mass_est_mine:.2f}} g; "
          f"difference={{mass_measured_mine-mass_est_mine:+.2f}} g")
    print(f"  measured-mass str/w={{sw_mine_measured_mass:.1f}} N/g; "
          f"model-basis str/w={{sw_mine_model_basis:.1f}} N/g")
    print(f"  sigma_epi={{pred_sigma_log:.3f}}, sigma_total={{sigma_total_log:.3f}}")
    print(f"posterior-predictive interval: [{{pred_lo_sw:.1f}}, {{pred_hi_sw:.1f}}] N/g")
    print("inside recorded model +/-2 sigma interval:", inside_2sigma)
    print(f"class scoreboard: best tested so far {{df.str_to_weight.max():.1f}} N/g")'''),
md('''The model was trained on strength divided by estimated mass, so the interval
comparison uses that same denominator. Report the measured-mass ratio too, but
do not compare ratios with different denominators as if they were the same
quantity. If the result lies outside the interval, distinguish model-form error,
print-to-print variability, and an unmodeled failure mechanism. One test does
not identify which.'''),
md('''## 2. The lightweight challenge: hold 700 N, weigh as little as possible

Same 16 beams, same tools — different objective. Now strength is a
**constraint**, not the prize. The class-default confidence rule: require the
model's lower posterior-predictive quantile for one future beam to clear the
target. Epistemic uncertainty and 3% aleatory observation scatter are
independent in log space:

$$\\sigma_{total}=\\sqrt{\\sigma_{epi}^2+0.03^2},\\qquad
P_{lo}(b,H)=e^{\\mu_{\\ln P}(b,H)-2\\sigma_{total}(b,H)}
\\ge 700\\text{ N}.$$

Among designs that pass, take the lightest. **FILL IN** the two marked lines.
(You may argue a different z than 2 in your memo — that is a risk posture,
not a math fact.)'''),
code(SRC_PHYS_FULL + f'''
SY_CAL, K_CAL, TAU_CAL = {CAL_SY:.3e}, {CAL_K}, {CAL_TAU:.3e}
P_TARGET = 700.0

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel as C, RBF

# class-default model: lane A (log str/w), 3% noise — swap in your own lane if you prefer
X = df[["b", "H"]].values
fmu, fsd = X.mean(0), X.std(0) + 1e-12
y = np.log(df.str_to_weight.values)
ymean = y.mean()
gp = GaussianProcessRegressor(C(1.0, (1e-3, 1e3))*RBF([1.0, 1.0], (1e-1, 30.0)),
                              alpha=0.03**2, normalize_y=False,
                              n_restarts_optimizer=5, random_state=0).fit((X-fmu)/fsd, y-ymean)

bg = np.linspace(1.25, 7.0, 60); Hg = np.linspace(5.0, 16.0, 60)
BB, HH = np.meshgrid(bg, Hg)
Xg = np.column_stack([BB.ravel(), HH.ravel()])
mu_c, std = gp.predict((Xg - fmu)/fsd, return_std=True)
mass_grid = estimated_mass_g(Xg[:, 0], Xg[:, 1])
# strength = str/w * mass, so in logs: ln P = (mu + ymean) + ln(mass)
mu_lnP = mu_c + ymean + np.log(mass_grid)
sigma_aleatory = 0.03
sigma_total = np.sqrt(std**2 + sigma_aleatory**2)

P_lo = ____        # >>> FILL IN: lower predictive strength, exp(mu_lnP minus 2*sigma_total)
feasible = ____    # >>> FILL IN: boolean mask, P_lo at or above P_TARGET
median_strength = np.exp(mu_lnP)
masked = np.where(feasible, mass_grid, np.inf)
i = int(np.argmin(masked))
b_lt, H_lt = float(Xg[i, 0]), float(Xg[i, 1])
median_feasible = median_strength >= P_TARGET
i_median = int(np.argmin(np.where(median_feasible, mass_grid, np.inf)))
lighter_infeasible = (~feasible) & (mass_grid < mass_grid[i])
if lighter_infeasible.any():
    j = int(np.argmax(np.where(lighter_infeasible, mass_grid, -np.inf)))
else:
    j = None
print(f"LIGHTWEIGHT DESIGN: b = {{b_lt:.2f}} mm, H_web = {{H_lt:.2f}} mm")
print(f"  mass {{mass_grid[i]:.1f}} g,  P_lo {{P_lo[i]:.0f}} N,  "
      f"posterior median {{median_strength[i]:.0f}} N")
print(f"  uncertainty allowance: posterior median - P_lo = "
      f"{{median_strength[i]-P_lo[i]:.0f}} N")
print(f"  median-only lightest design: b={{Xg[i_median,0]:.2f}}, "
      f"H_web={{Xg[i_median,1]:.2f}}, mass={{mass_grid[i_median]:.1f}} g, "
      f"median={{median_strength[i_median]:.0f}} N, P_lo={{P_lo[i_median]:.0f}} N")
print(f"  mass added by the 2-sigma rule versus median-only: "
      f"{{mass_grid[i]-mass_grid[i_median]:.1f}} g")
if j is not None:
    print(f"  closest-in-mass lighter infeasible grid point: b={{Xg[j,0]:.2f}}, "
          f"H_web={{Xg[j,1]:.2f}}, mass={{mass_grid[j]:.3f}} g "
          f"({{mass_grid[i]-mass_grid[j]:.3f}} g lighter), P_lo={{P_lo[j]:.0f}} N")
print(f"  calibrated-physics check: {{capacity(b_lt, H_lt, SY_CAL, K_CAL, TAU_CAL):.0f}} N, "
      f"mode {{gov_mode(b_lt, H_lt, SY_CAL, K_CAL, TAU_CAL)}}")
print("\\nCHECKPOINT (class-default model): you should arrive at "
      "b = «LT_B», H_web = «LT_H», mass = «LT_M» g.")
print("If you are not getting that, check your work or talk to a TA.")'''),
md('''### Stress-test the assumed aleatory noise

The table below refits the same class-default GP at 1%, 3%, and 10% observation
noise and uses that same value in each future-beam predictive bound. This is a
sensitivity analysis, not a vote on which noise value is true.'''),
code('''noise_design_rows = []
for pct in [1, 3, 10]:
    r = pct/100
    gp_r = GaussianProcessRegressor(
        C(1.0, (1e-3, 1e3))*RBF([1.0, 1.0], (1e-1, 30.0)),
        alpha=r**2, normalize_y=False,
        n_restarts_optimizer=5, random_state=0).fit((X-fmu)/fsd, y-ymean)
    mu_r, epi_r = gp_r.predict((Xg-fmu)/fsd, return_std=True)
    total_r = np.sqrt(epi_r**2 + r**2)
    lo_r = np.exp(mu_r+ymean+np.log(mass_grid)-2*total_r)
    i_r = int(np.argmin(np.where(lo_r >= P_TARGET, mass_grid, np.inf)))
    noise_design_rows.append(dict(
        noise_pct=pct, b=Xg[i_r, 0], H_web=Xg[i_r, 1],
        mass_est_g=mass_grid[i_r],
        median_strength_N=np.exp(mu_r[i_r]+ymean)*mass_grid[i_r],
        lower_predictive_N=lo_r[i_r]))
noise_design_table = pd.DataFrame(noise_design_rows)
print(noise_design_table.round(2).to_string(index=False))'''),
key_md('''### KEY-only: synthetic example result for the refit demo

The next cell fills the section-1 blanks with an invented but plausible result
(the Submission 1 default-recipe design failing 3% below its predicted median
strength) purely so the refit section below shows real output in this KEY.
It is labeled synthetic and is NOT a test result. Students use their own beam.'''),
key_code('''b_mine, H_mine = «DEF_B», «DEF_H»
mu_demo = gp.predict((np.array([[b_mine, H_mine]])-fmu)/fsd)[0] + ymean
P_mine = round(0.97*float(np.exp(mu_demo))*estimated_mass_g(b_mine, H_mine), 1)
mass_measured_mine = round(float(estimated_mass_g(b_mine, H_mine)), 2)
note_mine = "synthetic KEY example -- not a real test"
print(f"KEY demo beam: ({b_mine}, {H_mine}), {P_mine} N (synthetic)")'''),
md('''## 3. What your beam changes: refit with your own result

The lightweight design above deliberately used only the 16 frozen class beams,
so everyone's checkpoint matches. But your group now owns a 17th data point.
Fold it in, refit the same class-default model, and see what actually moves:
the 700 N design, the best-strength-to-weight pick, or neither. There is no
checkpoint here — the outcome depends on your beam, and it is graded through
the memo.'''),
code('''if None in (b_mine, H_mine, P_mine):
    print("Enter your beam in section 1 first; this cell is skipped without it.")
else:
    mine = pd.DataFrame([dict(beam_id=17, b=b_mine, H=H_mine, strength_N=P_mine,
                              weight_g=mass_measured_mine,
                              mass_est_g=estimated_mass_g(b_mine, H_mine),
                              failure_note=note_mine)])
    df17 = pd.concat([df, mine], ignore_index=True)
    df17["str_to_weight"] = df17.strength_N / df17.mass_est_g
    X17 = df17[["b", "H"]].values
    fmu17, fsd17 = X17.mean(0), X17.std(0) + 1e-12
    y17 = np.log(df17.str_to_weight.values); ym17 = y17.mean()
    gp17 = GaussianProcessRegressor(
        C(1.0, (1e-3, 1e3))*RBF([1.0, 1.0], (1e-1, 30.0)),
        alpha=0.03**2, normalize_y=False,
        n_restarts_optimizer=5, random_state=0).fit((X17-fmu17)/fsd17, y17-ym17)
    mu17, epi17 = gp17.predict((Xg-fmu17)/fsd17, return_std=True)
    tot17 = np.sqrt(epi17**2 + sigma_aleatory**2)
    lo17 = np.exp(mu17 + ym17 + np.log(mass_grid) - 2*tot17)
    i17 = int(np.argmin(np.where(lo17 >= P_TARGET, mass_grid, np.inf)))
    i_sw16 = int(np.argmax(mu_c))
    i_sw17 = int(np.argmax(mu17))
    mu_at_mine, _ = gp.predict((np.array([[b_mine, H_mine]])-fmu)/fsd,
                               return_std=True)
    pred_N_at_mine = np.exp(mu_at_mine[0]+ymean)*estimated_mass_g(b_mine, H_mine)
    print("lightweight design, 16 beams -> 17 beams:")
    print(f"  before: b={b_lt:.2f}, H_web={H_lt:.2f}, mass={mass_grid[i]:.1f} g")
    print(f"  after:  b={Xg[i17,0]:.2f}, H_web={Xg[i17,1]:.2f}, "
          f"mass={mass_grid[i17]:.1f} g")
    print("best posterior-median str/w point, 16 -> 17 beams:")
    print(f"  before: ({Xg[i_sw16,0]:.2f}, {Xg[i_sw16,1]:.2f});  "
          f"after: ({Xg[i_sw17,0]:.2f}, {Xg[i_sw17,1]:.2f})")
    print(f"  16-beam model median at your design: {pred_N_at_mine:.0f} N; "
          f"your measured strength: {P_mine:.0f} N")
    print("If nothing moved: one test rarely re-shapes a 16-beam posterior far")
    print("from the tested point. Whether it SHOULD have moved more is a memo")
    print("question about the noise and length-scale assumptions, not a code bug.")'''),
md('''## Memo

1. Reflection: report measured and estimated mass, use the model-basis ratio for
   the interval check, and compare the observed failure note with the modeled proxy.
2. Margin: use the printed posterior median, lower bound, median-only design,
   robust design, and closest-in-mass lighter infeasible candidate. State the
   comparison in newtons and grams.
3. `z`: defend 2 or price another value. Under the independent Gaussian
   log-noise model, the chance that one future measured beam falls below a
   two-sigma lower predictive bound is 2.28%. Kernel and model-form errors are
   outside that probability statement.
4. Physics veto: cite the calibrated capacity and dominant-mode proxy. If it
   disagrees with the GP constraint, explain which evidence you prioritize.
5. Noise sensitivity: use the 1/3/10% table. State what moves and whether your
   design decision is assumption-sensitive.
6. One more test: provide coordinates and say whether posterior median,
   epistemic sigma, or proximity to the feasibility boundary motivates it.
7. Redesign: from section 3, did your result move the lightweight design or
   the best-str/w pick? Whichever way it went, defend what you would print
   next, and connect the movement (or its absence) to the noise and
   length-scale assumptions.'''),
key_md('''## KEY: memo targets

1. The interval must compare like denominators: measured strength divided by
   estimated mass versus the GP prediction trained on that same quantity.
   Measured mass is reported separately as print-process evidence.
2. The class-default output directly supplies the required quantities and a
   defined closest-in-mass lighter grid point. Students should not compare against the
   globally lightest infeasible beam.
3. `z=2` corresponds to a 2.28% one-sided tail for one future observation only
   under the independent Gaussian log-noise model. Sparse data, kernel choices,
   and model-form error make that probability provisional.
4. Compare the printed GP lower bound with the empirical-physics capacity and
   proxy mode. Agreement is supporting evidence, not independent validation,
   because both were informed by the same small campaign.
5. Use the generated 1/3/10% table. Movement indicates assumption sensitivity;
   stability is local robustness, not proof of the assumed noise.
6. A useful extra test lies near the active lower-boundary contour, especially
   where epistemic uncertainty or an observed separation mechanism could change
   feasibility.
7. Either outcome is defensible on the evidence; strong answers quantify the
   movement (or its absence) in grams and millimeters and tie it to the 3%
   noise assumption and the fitted length scales, rather than asserting that
   the model "learned" from one point.'''),
]

# ----------------------------------------------------------------------------------
# 4. solution run: derive + verify every checkpoint from the notebook code itself
# ----------------------------------------------------------------------------------
SOLUTIONS = {
    'df["str_to_weight"] = ____    # >>> FILL IN: strength divided by estimated mass':
        'df["str_to_weight"] = df.strength_N / df.mass_est_g',
    '    return ____    # >>> FILL IN: P_bend; section_props is SI but L is in mm':
        '    return 4*sy*p["Ix"] / (p["c"] * L/1e3)',
    '    return ____    # >>> FILL IN: 2 * tau_i * Ix * t_w / Q_f  (t_w is p["b"])':
        '    return 2*tau_i*p["Ix"]*p["b"]/Q_flange(p)',
    '    return ____    # >>> FILL IN: mean squared difference of log predictions and measurements':
        '    return float(np.mean((np.log(pred) - np.log(df.strength_N.values))**2))',
    '        sw = ____    # >>> FILL IN: predicted capacity per estimated gram':
        '        sw = cap / estimated_mass_g(b, H)',
    '    return ____    # >>> FILL IN: mean plus psi times sigma':
        '    return mu + psi*sigma',
    '    imp = ____    # >>> FILL IN: mean minus best-so-far minus xi':
        '    imp = mu - y_best - xi',
    'P_lo = ____        # >>> FILL IN: lower predictive strength, exp(mu_lnP minus 2*sigma_total)':
        'P_lo = np.exp(mu_lnP - 2*sigma_total)',
    'feasible = ____    # >>> FILL IN: boolean mask, P_lo at or above P_TARGET':
        'feasible = P_lo >= P_TARGET',
}

def run_solution(cells, extra_replacements=()):
    src = "\n\n".join(s for k, s in cells if k == "code")
    for a, b in SOLUTIONS.items():
        src = src.replace(a, b)
    for a, b in extra_replacements:
        src = src.replace(a, b)
    src = src.replace('«', '').replace('»', '')     # tokens are inert inside strings
    import matplotlib
    matplotlib.use("Agg")
    ns = {}
    cwd = os.getcwd()
    os.chdir(DRAFTS)
    try:
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            exec(compile(src, "<solution>", "exec"), ns)
    finally:
        os.chdir(cwd)
    return ns, buf.getvalue()

print("running Pre-lab 1 solution ...")
ns1, _ = run_solution(P1)
assert 40e6 < ns1["SY_CAL"] < 100e6 and 0.05 < ns1["K_CAL"] < 1.0, "calibration off the rails"
assert 3e6 < ns1["TAU_CAL"] < 45e6, ns1["TAU_CAL"]
assert (ns1["b_eq"], ns1["H_eq"]) == (EQ_B, EQ_H), \
    f"equation design {(ns1['b_eq'], ns1['H_eq'])} != frozen ({EQ_B}, {EQ_H}) - " \
    "update the EQ_* constants from the run12 dry run"
best_row = ns1["df"].loc[ns1["df"].str_to_weight.idxmax()]
mape_nom = (ns1["df"].cap_nominal/ns1["df"].strength_N - 1).abs().mean()*100
initial_best_sw = float(best_row.str_to_weight)
eq_below_pct = 100*(ns1["sw_eq"]-EQ_SW)/ns1["sw_eq"]
assert abs(initial_best_sw-36.88) < 0.01, initial_best_sw
assert EQ_SW > initial_best_sw and GP_SW > initial_best_sw   # both queries beat the handout best
assert -50 < eq_below_pct < 60, eq_below_pct

print("running Pre-lab 2 solution ...")
ns2, _ = run_solution(P2)
x1, m1, _, _ = ns2["recommend_mui"](1.0)
assert abs(x1[0] - GP_B) < 0.06 and abs(x1[1] - GP_H) < 0.06, x1
gp_vs_pred_pct = 100*(GP_SW-m1)/m1
GP_VS_PRED_TXT = (
    f"{abs(gp_vs_pred_pct):.1f}% above its {m1:.1f} N/g prediction"
    if gp_vs_pred_pct >= 0 else
    f"{abs(gp_vs_pred_pct):.1f}% below its {m1:.1f} N/g prediction")
xe, _, _, _ = ns2["recommend_ei"](0.01)
ei_b, ei_H = xe
# checkpoint text comes from the exact noise table students generate
noise_recs = [(int(r["noise_pct"]), round(float(r["b"]), 2),
               round(float(r["H_web"]), 2))
              for r in ns2["noise_rows"]]
uniq = {r[1:] for r in noise_recs}
triplet = ";  ".join(f"{p}% -> ({b_}, {H_})" for p, b_, H_ in noise_recs)
if len(uniq) == 1:
    NOISE_TXT = ("all three settings agree on the same beam; this "
                 "recommendation is locally insensitive to the noise dial")
elif noise_recs[0][1:] == noise_recs[-1][1:]:
    NOISE_TXT = (f"the three settings do not all agree ({triplet}). Note the "
                 "pattern: the dependence is not monotone -- the 1% and 10% "
                 "choices coincide and only the middle setting differs, by "
                 "one grid step. Near-robustness of the argmax is a local "
                 "fact, not a vote for any noise value")
else:
    NOISE_TXT = f"the recommendation depends on the assumed noise: {triplet}"

print("running Submission 1 solution ...")
ns3, out3 = run_solution(S1)
# parse the per-kernel LOO table out of the solution run's own printout
loo = {}
_cur = None
for ln in out3.splitlines():
    t = ln.strip()
    if t.startswith("kernel = "):
        _cur = t.split("= ")[1]
        loo[_cur] = {}
    elif _cur and t.startswith(("A ", "B ", "C ", "D ")):
        lane_name, val = t.rsplit(":", 1)
        loo[_cur][lane_name.strip()] = float(val.replace("N/g", "").strip())
assert set(loo) == {"RBF", "Matern"} and all(len(v) == 4 for v in loo.values()), loo
def loo_line_txt(kern):
    return ",  ".join(f"{lane} {loo[kern][lane]:.2f}" for lane in
                      ("A plain", "B strength", "C features", "D residual")) + " N/g"
# the KEY asserts MUI psi=1 and EI agree at the default knobs -- verify it
from scipy.stats import norm as _norm
_best = np.log(ns3["df"].str_to_weight.max())
_zz = (np.log(ns3["MU"]) - _best) / ns3["STD"]
_score_ei = ns3["STD"] * (_zz*_norm.cdf(_zz) + _norm.pdf(_zz))
_iei = np.unravel_index(np.argmax(_score_ei), _score_ei.shape)
assert (abs(float(ns3["BB"][_iei]) - ns3["b_final"]) < 0.005
        and abs(float(ns3["HH"][_iei]) - ns3["H_final"]) < 0.005), \
    "EI default pick no longer matches MUI psi=1 -- rewrite the S1 section-4/KEY text"
print(f"S1 default-lane final: ({ns3['b_final']:.2f}, {ns3['H_final']:.2f}); "
      "EI agreement verified")
near = [(int(r.beam_id), r.b, r.H) for _, r in ns3["df"].iterrows()
        if abs(ns3["b_final"] - r.b) < 0.15 and abs(ns3["H_final"] - r.H) < 0.30]
DEF_NEAR_TXT = (
    f" -- and in fact its pick lands inside that radius, next to tested beam "
    f"{near[0][0]} at ({near[0][1]:g}, {near[0][2]:g})" if near else "")

print("running Submission 2 solution ...")
ns4, _ = run_solution(S2)
LT_B, LT_H, LT_M = ns4["b_lt"], ns4["H_lt"], float(ns4["mass_grid"][int(np.argmin(np.where(ns4["feasible"], ns4["mass_grid"], np.inf)))])

# ----------------------------------------------------------------------------------
# 5. fill tokens and write the notebooks
# ----------------------------------------------------------------------------------
TOKENS = {
    "«P2_KERNEL»": str(ns2["gp"].kernel_),
    "«BEST_ID»": str(int(best_row.beam_id)),
    "«BEST_B»": f"{best_row.b:g}", "«BEST_H»": f"{best_row.H:g}",
    "«BEST_SW»": f"{best_row.str_to_weight:.1f}",
    "«BEST_SW2»": f"{best_row.str_to_weight:.2f}",
    "«EQ_BELOW_PCT»": f"{eq_below_pct:.1f}",
    "«GP_VS_PRED_TEXT»": GP_VS_PRED_TXT,
    "«MAPE_NOM»": f"{mape_nom:.0f}",
    "«MAPE_CAL»": f"{ns1['mape_cal']:.1f}",
    "«CAL_SY_MPA»": f"{ns1['SY_CAL']/1e6:.1f}",
    "«CAL_K_V»": f"{ns1['K_CAL']:.3f}",
    "«CAL_TAU_MPA»": f"{ns1['TAU_CAL']/1e6:.2f}",
    "«CAL_SY_E»": f"{ns1['SY_CAL']:.3e}",
    "«CAL_TAU_E»": f"{ns1['TAU_CAL']:.3e}",
    "«EQ_B_CK»": f"{EQ_B:g}", "«EQ_H_CK»": f"{EQ_H:g}",
    "«EQ_PRED»": f"{ns1['sw_eq']:.1f}",
    "«MUI1_B»": f"{x1[0]:.2f}", "«MUI1_H»": f"{x1[1]:.2f}", "«MUI1_M»": f"{m1:.1f}",
    "«EI_B»": f"{ei_b:.2f}", "«EI_H»": f"{ei_H:.2f}",
    "«NOISE_BEHAVIOR»": NOISE_TXT,
    "«LOO_RBF»": loo_line_txt("RBF"),
    "«LOO_MATERN»": loo_line_txt("Matern"),
    "«LOO_D_RBF»": f"{loo['RBF']['D residual']:.2f}",
    "«LOO_D_MAT»": f"{loo['Matern']['D residual']:.2f}",
    "«LOO_B_RBF»": f"{loo['RBF']['B strength']:.2f}",
    "«LOO_B_MAT»": f"{loo['Matern']['B strength']:.2f}",
    "«DEF_B»": f"{ns3['b_final']:.2f}", "«DEF_H»": f"{ns3['H_final']:.2f}",
    "«DEF_NEAR_TXT»": DEF_NEAR_TXT,
    "«LT_B»": f"{LT_B:.2f}", "«LT_H»": f"{LT_H:.2f}", "«LT_M»": f"{LT_M:.1f}",
}

def write_nb(cells, path):
    nb_cells = []
    for kind, s in cells:
        if kind in ("key_md", "key_code"):
            continue
        for a, b in TOKENS.items():
            s = s.replace(a, b)
        nb_cells.append(nbf.v4.new_markdown_cell(s) if kind == "md"
                        else nbf.v4.new_code_cell(s))
    nb = nbf.v4.new_notebook(cells=nb_cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    })
    nbf.write(nb, path)
    print("wrote", path.name)

write_nb(P1, DRAFTS / "ME323_Module1_Prelab1_FailureModes_student.ipynb")
write_nb(P2, DRAFTS / "ME323_Module1_Prelab2_ML_student.ipynb")
write_nb(S1, DRAFTS / "ME323_Module1_Submission1_Design_student.ipynb")
write_nb(S2, DRAFTS / "ME323_Module1_Submission2_Lightweight_student.ipynb")


def write_key(cells, path):
    """Solution notebook: fill-ins answered, executed so TAs see every output."""
    from nbclient import NotebookClient
    nb_cells = []
    first_md = True
    for kind, s in cells:
        for a, b in SOLUTIONS.items():
            s = s.replace(a, b)
        for a, b in TOKENS.items():
            s = s.replace(a, b)
        if kind == "md" and first_md:
            s = s.replace("\n### ME 323 Module 1",
                          ": SOLUTION KEY\n### ME 323 Module 1 (staff only)", 1)
            first_md = False
        nb_cells.append(nbf.v4.new_markdown_cell(s) if kind in ("md", "key_md")
                        else nbf.v4.new_code_cell(s))
    nb = nbf.v4.new_notebook(cells=nb_cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    })
    client = NotebookClient(nb, timeout=1800, kernel_name="python3",
                            resources={"metadata": {"path": str(DRAFTS)}})
    client.execute()
    n_err = sum(1 for c in nb.cells if c.cell_type == "code"
                for o in c.get("outputs", []) if o.get("output_type") == "error")
    nbf.write(nb, path)
    print("wrote", path.name, f"(executed, errors={n_err})")
    assert n_err == 0, f"{path.name} has execution errors"


write_key(P1, DRAFTS / "ME323_Module1_Prelab1_FailureModes_KEY.ipynb")
write_key(P2, DRAFTS / "ME323_Module1_Prelab2_ML_KEY.ipynb")
write_key(S1, DRAFTS / "ME323_Module1_Submission1_Design_KEY.ipynb")
write_key(S2, DRAFTS / "ME323_Module1_Submission2_Lightweight_KEY.ipynb")

print("\nverified checkpoints:")
print(f"  P1: best beam {TOKENS['«BEST_ID»']} ({TOKENS['«BEST_B»']},{TOKENS['«BEST_H»']}) "
      f"{TOKENS['«BEST_SW»']} N/g;  nominal MAPE {TOKENS['«MAPE_NOM»']}%;  "
      f"cal ({ns1['SY_CAL']/1e6:.1f} MPa, {ns1['K_CAL']:.3f}, "
      f"{ns1['TAU_CAL']/1e6:.2f} MPa);  eq ({EQ_B}, {EQ_H})")
print(f"  P2: MUI1 ({TOKENS['«MUI1_B»']}, {TOKENS['«MUI1_H»']}) pred {TOKENS['«MUI1_M»']};  "
      f"EI ({TOKENS['«EI_B»']}, {TOKENS['«EI_H»']});  noise: {NOISE_TXT[:70]}...")
print(f"  S1: LOO RBF {loo_line_txt('RBF')};  Matern {loo_line_txt('Matern')};  "
      f"default final ({TOKENS['«DEF_B»']}, {TOKENS['«DEF_H»']})")
print(f"  S2: lightweight ({TOKENS['«LT_B»']}, {TOKENS['«LT_H»']}) mass {TOKENS['«LT_M»']} g")
