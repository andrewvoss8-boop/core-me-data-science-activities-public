"""
Smoke test for heteroscedastic_noise (optional R-dependent GP alpha).

Run from repo: python me323/heteroscedastic_test.py
Or from me323: python heteroscedastic_test.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
import urllib.request, io
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel

from heteroscedastic_noise import calc_R, get_noise_variance

DATA_URL = (
    "https://raw.githubusercontent.com/andrewvoss8-boop/"
    "core-me-data-science-activities-public/main/data/I_beam_data_2var.csv"
)


def load_data():
    print("Downloading data...")
    with urllib.request.urlopen(DATA_URL) as r:
        df = pd.read_csv(io.StringIO(r.read().decode("utf-8")))
    return df


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


if __name__ == "__main__":
    df = load_data()
    b_all = df['b_web_mm'].values.astype(float)
    H_all = df['H_web_mm'].values.astype(float)
    y_all = df['Str/w N/g'].values.astype(float)
    R_all = np.array([calc_R(b, H) for b, H in zip(b_all, H_all)])

    bounds = [(b_all.min() - 0.5, b_all.max() + 0.5),
              (H_all.min() - 0.5, H_all.max() + 0.5)]
    X = np.column_stack([b_all, H_all])

    print("\n=== Noise model across dataset ===")
    print(f"{'Beam':>20}  b     H      R     var_noise   sqrt(var)")
    for i in range(len(df)):
        v = get_noise_variance(R_all[i])
        nm = str(df['Beam Number'].iloc[i])
        print(f"{nm:>20}  {b_all[i]:.2f}  {H_all[i]:.2f}  {R_all[i]:.3f}  {v:.2e}    {np.sqrt(v):.4f}")

    alpha_het = np.array([get_noise_variance(R) for R in R_all])
    alpha_homo = 7e-5

    print(f"\n=== Training GP: homoscedastic alpha={alpha_homo:.1e} ===")
    gp_homo, _, _, ym_homo = train_gp(X, y_all, bounds, alpha=alpha_homo)
    print(f"  kernel: {gp_homo.kernel_}")
    print(f"  log-marginal-likelihood: {gp_homo.log_marginal_likelihood_value_:.2f}")

    print(f"\n=== Training GP: heteroscedastic (R-dependent) ===")
    print(f"  alpha range: [{alpha_het.min():.2e}, {alpha_het.max():.2e}]")
    gp_het, _, _, ym_het = train_gp(X, y_all, bounds, alpha=alpha_het)
    print(f"  kernel: {gp_het.kernel_}")
    print(f"  log-marginal-likelihood: {gp_het.log_marginal_likelihood_value_:.2f}")

    test_pts = [
        ("strong zone",    4.5, 14.5),
        ("mid R",          4.0, 16.0),
        ("low R (thin)",   2.0, 18.0),
        ("high R (thick)", 7.5, 13.0),
    ]

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

    print("\n=== Leave-one-out residuals (log space) ===")
    for name, alpha_val in [("homo", alpha_homo), ("het", alpha_het)]:
        resids = []
        for i in range(len(X)):
            mask = np.ones(len(X), dtype=bool)
            mask[i] = False
            a = alpha_val if np.isscalar(alpha_val) else alpha_val[mask]
            gp_loo, _, _, ym_loo = train_gp(X[mask], y_all[mask], bounds, alpha=a)
            xn = normalize(X[i:i+1], bounds)
            mu = gp_loo.predict(xn)
            resids.append(np.log(y_all[i]) - (mu[0] + ym_loo))
        resids = np.array(resids)
        rmse = np.sqrt(np.mean(resids**2))
        print(f"  {name:>5}  RMSE(log): {rmse:.5f}  MAE(log): {np.mean(np.abs(resids)):.5f}")
