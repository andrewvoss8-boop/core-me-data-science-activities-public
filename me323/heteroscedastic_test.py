"""
Heteroscedastic GP noise as a function of R (stability ratio).

Calibration data (same-geometry repeats, log(Str/w) variance):
  (4.50, 14.50)  R=0.73  n=4  var(log y) = 1.6e-5
  (3.50, 14.50)  R=0.70  n=2  var(log y) = 3.1e-4   <-- outlier, n=2
  (4.25, 14.25)  R=0.74  n=2  var(log y) = 2.2e-5
  (4.50, 18.50)  R=0.51  n=2  var(log y) = 2.5e-5

All four groups are R < 1 (LTB-governed). No repeats exist at R > 1
(yield-governed) or near R ~ 1 (transition). The bump shape near R=1
is a physics argument (transition zone = more sensitivity to BCs,
imperfections, print quality), not empirically calibrated here.
"""

import numpy as np
import pandas as pd
import urllib.request, io
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel

# ── geometry / material (same as beam_strength_comparison) ──────────────
E = 2.74e9;  SIGMA_Y = 81.8e6;  G = E / 2.6
L = 0.2023;  C1 = 1.35
TOTAL_H = 25.0;  B_F = 16.0;  Y_MAX = TOTAL_H / 2e3

DATA_URL = (
    "https://raw.githubusercontent.com/andrewvoss8-boop/"
    "core-me-data-science-activities-public/main/data/I_beam_data_2var.csv"
)

def _beta(t, a):
    if a <= 0 or t <= 0: return 1.0/3.0
    r = min(t, a) / max(t, a)
    return (1.0/3.0) * (1.0 - 0.63*r + 0.052*r**5)

def calc_R(b_mm, H_mm):
    H, b, Bf = H_mm/1e3, b_mm/1e3, B_F/1e3
    h = (TOTAL_H/1e3 - H) / 2.0
    if h <= 0: return 0.0
    Ix = (b * H**3)/12 + 2*(Bf * h**3/12 + Bf * h * ((H + h)/2)**2)
    Iy = (H * b**3)/12 + 2*(h * Bf**3)/12
    J_web = _beta(min(b, H), max(b, H)) * max(b, H) * min(b, H)**3
    J_fl  = _beta(min(h, Bf), max(h, Bf)) * max(h, Bf) * min(h, Bf)**3
    J = J_web + 2 * J_fl
    My = SIGMA_Y * Ix / Y_MAX
    Mcr = (C1 * np.pi / L) * np.sqrt(E * Iy * G * J)
    return Mcr / My if My > 0 else 0.0


# ── heteroscedastic noise model ────────────────────────────────────────
#
# Model: Gaussian bump in log(R) centered at R=1 (log R = 0).
#   var_noise(R) = (sigma_base + sigma_peak * bump(R))^2
#   bump(R)      = exp(-0.5 * (ln R / width)^2)
#
# Calibration (from repeat groups, log-space):
#   3 of 4 groups give var ~ 2e-5  => sigma ~ 0.004
#   These sit at R ~ 0.5–0.74, so bump(R) ~ 0.1–0.4
#   Set sigma_base so that floor (R >> 1, bump ~ 0) ~ 1e-5
#     => sigma_base ~ 0.003
#   Set sigma_peak so that at R ~ 0.7, total sigma ~ 0.005
#     bump(0.7) = exp(-0.5*(ln 0.7 / 0.4)^2) ~ 0.37
#     0.003 + sigma_peak * 0.37 ~ 0.005 => sigma_peak ~ 0.005
#   At R = 1: noise = (0.003 + 0.005)^2 = 6.4e-5 (peak)
#   At R >> 1 or R << 0.3: noise ~ (0.003)^2 = 9e-6 (floor)
#
# The (3.5, 14.5) outlier (var ~ 3e-4) is not fit; with n=2 and a
# different failure mode ("top flange sheared off and split in half")
# it may reflect a mode switch rather than random noise at that R.

SIGMA_BASE = 0.003
SIGMA_PEAK = 0.005
WIDTH = 0.4

def get_noise_variance(R):
    """Return var(log Str/w) as a function of stability ratio R."""
    log_R = np.log(max(R, 1e-6))
    bump = np.exp(-0.5 * (log_R / WIDTH)**2)
    return (SIGMA_BASE + SIGMA_PEAK * bump)**2


# ── load data ──────────────────────────────────────────────────────────
def load_data():
    print("Downloading data...")
    with urllib.request.urlopen(DATA_URL) as r:
        df = pd.read_csv(io.StringIO(r.read().decode("utf-8")))
    return df


# ── GP helpers (minimal, same pattern as beam_lab_student) ─────────────
def normalize(X, bounds):
    lo = np.array([b[0] for b in bounds])
    hi = np.array([b[1] for b in bounds])
    return (X - lo) / (hi - lo)

def train_gp(X, y, bounds, alpha):
    X_n = normalize(X, bounds)
    y_log = np.log(y)
    y_mean = y_log.mean()
    y_c = y_log - y_mean
    kernel = ConstantKernel(1.0) * Matern(nu=2.5)
    gp = GaussianProcessRegressor(
        kernel=kernel, n_restarts_optimizer=10,
        alpha=alpha, normalize_y=False)
    gp.fit(X_n, y_c)
    return gp, X_n, y_c, y_mean


# ── main ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = load_data()
    b_all = df['b_web_mm'].values.astype(float)
    H_all = df['H_web_mm'].values.astype(float)
    y_all = df['Str/w N/g'].values.astype(float)
    R_all = np.array([calc_R(b, H) for b, H in zip(b_all, H_all)])

    bounds = [(b_all.min() - 0.5, b_all.max() + 0.5),
              (H_all.min() - 0.5, H_all.max() + 0.5)]
    X = np.column_stack([b_all, H_all])

    # ── noise profile ──
    print("\n=== Noise model across dataset ===")
    print(f"{'Beam':>20}  b     H      R     var_noise   sqrt(var)")
    for i in range(len(df)):
        v = get_noise_variance(R_all[i])
        nm = str(df['Beam Number'].iloc[i])
        print(f"{nm:>20}  {b_all[i]:.2f}  {H_all[i]:.2f}  {R_all[i]:.3f}  {v:.2e}    {np.sqrt(v):.4f}")

    # ── heteroscedastic alpha array ──
    alpha_het = np.array([get_noise_variance(R) for R in R_all])

    # ── homoscedastic baseline (pooled repeat variance) ──
    alpha_homo = 7e-5

    # ── train both ──
    print(f"\n=== Training GP: homoscedastic alpha={alpha_homo:.1e} ===")
    gp_homo, _, _, ym_homo = train_gp(X, y_all, bounds, alpha=alpha_homo)
    print(f"  kernel: {gp_homo.kernel_}")
    print(f"  log-marginal-likelihood: {gp_homo.log_marginal_likelihood_value_:.2f}")

    print(f"\n=== Training GP: heteroscedastic (R-dependent) ===")
    print(f"  alpha range: [{alpha_het.min():.2e}, {alpha_het.max():.2e}]")
    gp_het, _, _, ym_het = train_gp(X, y_all, bounds, alpha=alpha_het)
    print(f"  kernel: {gp_het.kernel_}")
    print(f"  log-marginal-likelihood: {gp_het.log_marginal_likelihood_value_:.2f}")

    # ── compare predictions at a few points ──
    test_pts = [
        ("strong zone",    4.5, 14.5),
        ("mid R",          4.0, 16.0),
        ("low R (thin)",   2.0, 18.0),
        ("high R (thick)", 7.5, 13.0),
    ]
    X_n_homo = normalize(X, bounds)
    X_n_het  = normalize(X, bounds)

    print("\n=== Predictions at test points ===")
    print(f"{'label':>20}  b     H     R    | homo mu(Str/w)  sig  | het mu(Str/w)  sig")
    for label, b, H in test_pts:
        R = calc_R(b, H)
        xn = normalize(np.array([[b, H]]), bounds)
        mu_ho, sig_ho = gp_homo.predict(xn, return_std=True)
        mu_he, sig_he = gp_het.predict(xn, return_std=True)
        strw_ho = np.exp(mu_ho[0] + ym_homo)
        strw_he = np.exp(mu_he[0] + ym_het)
        sig_strw_ho = strw_ho * sig_ho[0]
        sig_strw_he = strw_he * sig_he[0]
        print(f"{label:>20}  {b:.1f}  {H:.1f}  {R:.3f}  | "
              f"{strw_ho:.2f}  {sig_strw_ho:.2f}  | "
              f"{strw_he:.2f}  {sig_strw_he:.2f}")

    # ── LOO residuals (quick check, not rigorous) ──
    print("\n=== Leave-one-out residuals (log space) ===")
    for name, alpha_val in [("homo", alpha_homo), ("het", alpha_het)]:
        resids = []
        for i in range(len(X)):
            mask = np.ones(len(X), dtype=bool); mask[i] = False
            a = alpha_val if np.isscalar(alpha_val) else alpha_val[mask]
            gp_loo, _, _, ym_loo = train_gp(X[mask], y_all[mask], bounds, alpha=a)
            xn = normalize(X[i:i+1], bounds)
            mu = gp_loo.predict(xn)
            resids.append(np.log(y_all[i]) - (mu[0] + ym_loo))
        resids = np.array(resids)
        rmse = np.sqrt(np.mean(resids**2))
        print(f"  {name:>5}  RMSE(log): {rmse:.5f}  MAE(log): {np.mean(np.abs(resids)):.5f}")
