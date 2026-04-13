"""
ARD feature-selection sweep on full data (all ~34 beams).

Add every physics-derived feature to the input and let ARD length-scales
reveal which ones matter for predicting log(Str/w).

Features (all computed from b, H):
  - b, H (raw design vars)
  - dH (H - H_opt for that b)
  - R (Mcr / My, stability ratio)
  - Ix, Iy, J (section properties in m^4)
  - Mcr (critical moment for LTB, N·m)
  - P_ltb, P_bend (predicted loads, N)
  - P_ltb/mass, P_bend/mass (normalized strengths)
  - A_web (b*H, web shear area proxy, mm^2)

Train a GP with ARD kernel (separate length-scale per feature), alpha=1e-4, Matern.
Compare learned length-scales: short -> important, long -> ignore.
"""

import pathlib

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern

REPO = pathlib.Path(__file__).resolve().parents[1]
FULL_CSV = REPO / "data" / "I_beam_data_2var.csv"

TOTAL_HEIGHT = 25.0
B_FIXED = 16.0
LENGTH_M = 0.2023
SIGMA_Y = 81.8e6
E_MOD = 2.74e9
G_MOD = E_MOD / 2.6
C1 = 1.35
DENSITY = 1210
Y_MAX = TOTAL_HEIGHT / 2e3


def _beta(t, a):
    if a <= 0 or t <= 0: return 1.0/3.0
    r = min(t, a) / max(t, a)
    return (1.0/3.0) * (1.0 - 0.63*r + 0.052*r**5)


def calc_Ix(H, b):
    H_m, b_m, B_m = H/1e3, b/1e3, B_FIXED/1e3
    h_m = (TOTAL_HEIGHT/1e3 - H_m)/2.0
    if h_m <= 0: return 0.0
    return (b_m * H_m**3)/12 + 2*(B_m*h_m**3/12 + B_m*h_m*((H_m+h_m)/2)**2)

def calc_Iy(H, b):
    H_m, b_m, B_m = H/1e3, b/1e3, B_FIXED/1e3
    h_m = (TOTAL_HEIGHT/1e3 - H_m)/2.0
    if h_m <= 0: return 0.0
    return (H_m * b_m**3)/12 + 2*(h_m * B_m**3)/12

def calc_J(H, b):
    H_m, b_m, B_m = H/1e3, b/1e3, B_FIXED/1e3
    h_m = (TOTAL_HEIGHT/1e3 - H_m)/2.0
    if h_m <= 0: return 0.0
    rw = b_m / H_m
    beta_w = (1.0/3.0) * (1.0 - 0.63*rw + 0.052*rw**5)
    J_web = beta_w * H_m * b_m**3
    rf = h_m / B_m
    beta_f = (1.0/3.0) * (1.0 - 0.63*rf + 0.052*rf**5)
    J_fl = beta_f * B_m * h_m**3
    return J_web + 2*J_fl

def calc_mass(H, b):
    H_m, b_m, B_m = H/1e3, b/1e3, B_FIXED/1e3
    h_m = (TOTAL_HEIGHT/1e3 - H_m)/2.0
    if h_m <= 0: return 0.0
    return DENSITY * LENGTH_M * (H_m*b_m + 2*h_m*B_m) * 1000

def calc_P_bend(H, b):
    Ix = calc_Ix(H, b)
    return 4 * SIGMA_Y * Ix / Y_MAX / LENGTH_M

def calc_P_ltb(H, b):
    Iy, J = calc_Iy(H, b), calc_J(H, b)
    if Iy <= 0 or J <= 0: return 0.0
    Mcr = (C1 * np.pi / LENGTH_M) * np.sqrt(E_MOD * Iy * G_MOD * J)
    return 4 * Mcr / LENGTH_M

def find_H_opt(b):
    def obj(H):
        h = (TOTAL_HEIGHT - H)/2.0
        if h < 0 or h > 6.5: return 1e10
        P, m = calc_P_bend(H, b), calc_mass(H, b)
        return -P/m if m > 0 else 1e10
    return minimize_scalar(obj, bounds=(12.0, 23.4), method='bounded').x


def build_feature_matrix(b_arr, H_arr):
    """
    Return X (n x d), feature_names.
    Each row: [b, H, dH, R, Ix, Iy, J, Mcr, P_ltb, P_bend, Pltb_m, Pbend_m, A_web]
    """
    n = len(b_arr)
    X = np.zeros((n, 13))
    for i in range(n):
        b, H = b_arr[i], H_arr[i]
        Ix = calc_Ix(H, b)
        Iy = calc_Iy(H, b)
        J = calc_J(H, b)
        My = SIGMA_Y * Ix / Y_MAX
        Mcr = (C1 * np.pi / LENGTH_M) * np.sqrt(E_MOD * Iy * G_MOD * J) if (Iy>0 and J>0) else 0.0
        R = Mcr / My if My > 0 else 0.0
        P_bend = 4 * My / LENGTH_M
        P_ltb = 4 * Mcr / LENGTH_M
        m = calc_mass(H, b)
        Pltb_m = P_ltb / m if m > 0 else 0.0
        Pbend_m = P_bend / m if m > 0 else 0.0
        H_opt = find_H_opt(b)
        A_web = b * H  # mm^2

        X[i, :] = [b, H, H - H_opt, R, Ix, Iy, J, Mcr, P_ltb, P_bend, Pltb_m, Pbend_m, A_web]

    names = ["b", "H", "dH", "R", "Ix", "Iy", "J", "Mcr", "P_ltb", "P_bend",
             "Pltb_m", "Pbend_m", "A_web"]
    return X, names


def normalize_features(X):
    """z-score each column."""
    mu = X.mean(axis=0)
    sig = X.std(axis=0)
    sig[sig < 1e-12] = 1.0
    return (X - mu) / sig


def main():
    df = pd.read_csv(FULL_CSV)
    b_all = df["b_web_mm"].values.astype(float)
    H_all = df["H_web_mm"].values.astype(float)
    y_all = df["Str/w N/g"].values.astype(float)

    X_raw, feat_names = build_feature_matrix(b_all, H_all)
    X_norm = normalize_features(X_raw)
    y_log = np.log(y_all)
    y_mean = y_log.mean()
    y_c = y_log - y_mean

    print(f"Full dataset: {len(y_all)} beams, {X_norm.shape[1]} features")
    print("Features:", feat_names)
    print()

    # ARD: one length-scale per feature, wide prior
    length_scale_bounds = (0.05, 20.0)
    kernel = ConstantKernel(1.0) * Matern(
        length_scale=np.ones(X_norm.shape[1]),
        length_scale_bounds=length_scale_bounds,
        nu=2.5
    )

    print("Training GP with ARD (Matern, alpha=1e-4)...")
    gp = GaussianProcessRegressor(
        kernel=kernel,
        n_restarts_optimizer=25,
        alpha=1e-4,
        normalize_y=False
    )
    gp.fit(X_norm, y_c)
    print(f"  log-marginal-likelihood: {gp.log_marginal_likelihood_value_:.2f}")
    print()

    # Extract length-scales
    ls = gp.kernel_.k2.length_scale
    if np.isscalar(ls):
        ls = np.array([ls])

    print("=== ARD length-scales (shorter = more important) ===")
    ls_df = pd.DataFrame({"feature": feat_names, "length_scale": ls})
    ls_df = ls_df.sort_values("length_scale")
    print(ls_df.to_string(index=False))
    print()

    # Relative importance: inverse of length-scale, normalized
    inv_ls = 1.0 / (ls + 1e-9)
    imp = inv_ls / inv_ls.sum()
    imp_df = pd.DataFrame({"feature": feat_names, "rel_importance": imp})
    imp_df = imp_df.sort_values("rel_importance", ascending=False)
    print("=== Relative importance (1/length_scale, normalized) ===")
    print(imp_df.to_string(index=False))
    print()

    # LOO cross-val for fit quality
    print("=== Leave-one-out cross-validation ===")
    resids = []
    for i in range(len(X_norm)):
        mask = np.ones(len(X_norm), dtype=bool)
        mask[i] = False
        gp_loo = GaussianProcessRegressor(
            kernel=kernel,
            n_restarts_optimizer=15,
            alpha=1e-4,
            normalize_y=False
        )
        X_loo = normalize_features(X_raw[mask])
        y_loo_mean = np.log(y_all[mask]).mean()
        y_loo_c = np.log(y_all[mask]) - y_loo_mean
        gp_loo.fit(X_loo, y_loo_c)
        X_test = normalize_features(X_raw[i:i+1])
        mu = gp_loo.predict(X_test)
        resids.append(np.log(y_all[i]) - (mu[0] + y_loo_mean))

    resids = np.array(resids)
    rmse = np.sqrt(np.mean(resids**2))
    mae = np.mean(np.abs(resids))
    print(f"  RMSE(log): {rmse:.5f}")
    print(f"  MAE(log):  {mae:.5f}")
    print(f"  RMSE(Str/w) approx: {rmse * y_all.mean():.2f} N/g")
    print()

    # Compare to simple (b,H) baseline
    print("=== Baseline: 2-feature (b,H) GP for comparison ===")
    X_bH = normalize_features(X_raw[:, :2])
    kernel_bH = ConstantKernel(1.0) * Matern(
        length_scale=[1.0, 1.0],
        length_scale_bounds=(0.05, 20.0),
        nu=2.5
    )
    gp_bH = GaussianProcessRegressor(kernel=kernel_bH, n_restarts_optimizer=15, alpha=1e-4, normalize_y=False)
    gp_bH.fit(X_bH, y_c)
    print(f"  log-marginal-likelihood: {gp_bH.log_marginal_likelihood_value_:.2f}")
    print(f"  length-scales: b={gp_bH.kernel_.k2.length_scale[0]:.3f}, H={gp_bH.kernel_.k2.length_scale[1]:.3f}")

    # LOO for (b,H)
    resids_bH = []
    for i in range(len(X_bH)):
        mask = np.ones(len(X_bH), dtype=bool)
        mask[i] = False
        gp_loo2 = GaussianProcessRegressor(kernel=kernel_bH, n_restarts_optimizer=10, alpha=1e-4, normalize_y=False)
        X_loo2 = normalize_features(X_raw[mask, :2])
        y_loo2_mean = np.log(y_all[mask]).mean()
        y_loo2_c = np.log(y_all[mask]) - y_loo2_mean
        gp_loo2.fit(X_loo2, y_loo2_c)
        X_test2 = normalize_features(X_raw[i:i+1, :2])
        mu2 = gp_loo2.predict(X_test2)
        resids_bH.append(np.log(y_all[i]) - (mu2[0] + y_loo2_mean))
    resids_bH = np.array(resids_bH)
    print(f"  LOO RMSE(log): {np.sqrt(np.mean(resids_bH**2)):.5f}")
    print(f"  LOO MAE(log):  {np.mean(np.abs(resids_bH)):.5f}")


if __name__ == "__main__":
    main()
