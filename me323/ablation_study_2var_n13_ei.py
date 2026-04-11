"""
Ablation: 13-beam subset + optional b>=2 training/BO constraint.
- Train only on data/lhs16_subset_bH_even_n13.csv (verbatim 13 LHS rows).
- Scenario A: all 13 beams, BO samples b in [1, 8].
- Scenario B: train on beams with b >= 2 only (10 beams: drops 7,12,13); BO samples b in [2, 8].
- Matern kernel, EI acquisition, noise alpha = 1e-4 only.
- Ground-truth scoring GP unchanged: b_dH_Pltb_Pbend on full GitHub CSV.

Run from repo root: python me323/ablation_study_2var_n13_ei.py
"""
from __future__ import annotations

import io
import pathlib
import time
import urllib.request
import warnings

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern

warnings.filterwarnings("ignore")

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBSET_CSV = REPO / "data" / "lhs16_subset_bH_even_n13.csv"
OUT_CSV = pathlib.Path(__file__).resolve().parent / "ablation_results_2var_n13_ei.csv"

DATA_URL = (
    "https://raw.githubusercontent.com/andrewvoss8-boop/"
    "core-me-data-science-activities-public/main/data/I_beam_data_2var.csv"
)

# --- physics (same as v2) ---
TOTAL_HEIGHT = 25.0
B_FIXED = 16.0
LENGTH_M = 0.2023
SIGMA_Y = 81.8e6
E_MOD = 2.74e9
G_MOD = E_MOD / 2.6
C1 = 1.35
DENSITY = 1210
Y_MAX = TOTAL_HEIGHT / 2e3


def calc_Ix(H, b, B=B_FIXED):
    H_m, b_m, B_m = H / 1e3, b / 1e3, B / 1e3
    h_m = (TOTAL_HEIGHT / 1e3 - H_m) / 2.0
    if h_m <= 0:
        return 0.0
    return (b_m * H_m**3) / 12 + 2 * (
        B_m * h_m**3 / 12 + B_m * h_m * ((H_m + h_m) / 2) ** 2
    )


def calc_Iy(H, b, B=B_FIXED):
    H_m, b_m, B_m = H / 1e3, b / 1e3, B / 1e3
    h_m = (TOTAL_HEIGHT / 1e3 - H_m) / 2.0
    if h_m <= 0:
        return 0.0
    return (H_m * b_m**3) / 12 + 2 * (h_m * B_m**3) / 12


def calc_J(H, b, B=B_FIXED):
    H_m, b_m, B_m = H / 1e3, b / 1e3, B / 1e3
    h_m = (TOTAL_HEIGHT / 1e3 - H_m) / 2.0
    if h_m <= 0:
        return 0.0
    rw = b_m / H_m
    beta_w = (1.0 / 3.0) * (1.0 - 0.63 * rw + 0.052 * rw**5)
    J_web = beta_w * H_m * b_m**3
    rf = h_m / B_m
    beta_f = (1.0 / 3.0) * (1.0 - 0.63 * rf + 0.052 * rf**5)
    J_fl = beta_f * B_m * h_m**3
    return J_web + 2 * J_fl


def calc_mass(H, b, B=B_FIXED):
    H_m, b_m, B_m = H / 1e3, b / 1e3, B / 1e3
    h_m = (TOTAL_HEIGHT / 1e3 - H_m) / 2.0
    if h_m <= 0:
        return 0.0
    return DENSITY * LENGTH_M * (H_m * b_m + 2 * h_m * B_m) * 1000


def calc_P_bend(H, b):
    Ix = calc_Ix(H, b)
    My = SIGMA_Y * Ix / Y_MAX
    return 4 * My / LENGTH_M


def calc_P_ltb(H, b):
    Iy = calc_Iy(H, b)
    J = calc_J(H, b)
    if Iy <= 0 or J <= 0:
        return 0.0
    Mcr = (C1 * np.pi / LENGTH_M) * np.sqrt(E_MOD * Iy * G_MOD * J)
    return 4 * Mcr / LENGTH_M


def calc_R(H, b):
    Ix = calc_Ix(H, b)
    My = SIGMA_Y * Ix / Y_MAX
    if My <= 0:
        return 0.0
    Iy = calc_Iy(H, b)
    J = calc_J(H, b)
    if Iy <= 0 or J <= 0:
        return 0.0
    Mcr = (C1 * np.pi / LENGTH_M) * np.sqrt(E_MOD * Iy * G_MOD * J)
    return Mcr / My


def calc_str_w(H, b):
    P = calc_P_bend(H, b)
    m = calc_mass(H, b)
    return P / m if m > 0 else 0.0


def find_H_opt(b):
    def obj(H):
        if H < 12.0 or H > 23.4:
            return 1e10
        h = (TOTAL_HEIGHT - H) / 2.0
        if h < 0 or h > 6.5:
            return 1e10
        return -calc_str_w(H, b)

    return minimize_scalar(obj, bounds=(12.0, 23.4), method="bounded").x


def _Pltb_per_mass(b, H):
    m = calc_mass(H, b)
    return calc_P_ltb(H, b) / m if m > 0 else 0.0


def _Pbend_per_mass(b, H):
    m = calc_mass(H, b)
    return calc_P_bend(H, b) / m if m > 0 else 0.0


def _dH(b, H):
    return H - find_H_opt(b)


def to_bH(b_arr, H_arr):
    return np.column_stack([b_arr, H_arr])


def to_bdHR(b_arr, H_arr):
    n = len(b_arr)
    out = np.zeros((n, 3))
    for i in range(n):
        out[i, 0] = b_arr[i]
        out[i, 1] = _dH(b_arr[i], H_arr[i])
        out[i, 2] = calc_R(H_arr[i], b_arr[i])
    return out


def to_Pltb_Pbend(b_arr, H_arr):
    n = len(b_arr)
    out = np.zeros((n, 2))
    for i in range(n):
        out[i, 0] = _Pltb_per_mass(b_arr[i], H_arr[i])
        out[i, 1] = _Pbend_per_mass(b_arr[i], H_arr[i])
    return out


def to_b_Pltb_Pbend(b_arr, H_arr):
    n = len(b_arr)
    out = np.zeros((n, 3))
    for i in range(n):
        out[i, 0] = b_arr[i]
        out[i, 1] = _Pltb_per_mass(b_arr[i], H_arr[i])
        out[i, 2] = _Pbend_per_mass(b_arr[i], H_arr[i])
    return out


def to_b_dH_Pltb_Pbend(b_arr, H_arr):
    n = len(b_arr)
    out = np.zeros((n, 4))
    for i in range(n):
        out[i, 0] = b_arr[i]
        out[i, 1] = _dH(b_arr[i], H_arr[i])
        out[i, 2] = _Pltb_per_mass(b_arr[i], H_arr[i])
        out[i, 3] = _Pbend_per_mass(b_arr[i], H_arr[i])
    return out


def _bounds_from_data(X, names, margin=0.15):
    bds = {}
    for i, nm in enumerate(names):
        lo, hi = X[:, i].min(), X[:, i].max()
        span = hi - lo
        if span < 1e-9:
            span = abs(lo) * 0.1 + 1e-6
        bds[nm] = (lo - margin * span, hi + margin * span)
    return bds


def build_param_configs(b_tr, H_tr, b_lo_box, b_hi_box=8.0):
    """Bounds for transforms from training (b_tr,H_tr); physical b box for sampling."""
    H_lo, H_hi = 12.0, 23.0
    BOUNDS_bH = {"b": (float(b_lo_box), float(b_hi_box)), "H": (H_lo, H_hi)}

    _X_bdHR = to_bdHR(b_tr, H_tr)
    _X_PP = to_Pltb_Pbend(b_tr, H_tr)
    _X_bPP = to_b_Pltb_Pbend(b_tr, H_tr)
    _X_bdHPP = to_b_dH_Pltb_Pbend(b_tr, H_tr)

    BOUNDS_bdHR = _bounds_from_data(_X_bdHR, ["b", "dH", "R"])
    BOUNDS_bdHR["b"] = (b_lo_box, b_hi_box)

    BOUNDS_PP = _bounds_from_data(_X_PP, ["Pltb_m", "Pbend_m"])
    BOUNDS_bPP = _bounds_from_data(_X_bPP, ["b", "Pltb_m", "Pbend_m"])
    BOUNDS_bPP["b"] = (b_lo_box, b_hi_box)

    BOUNDS_bdHPP = _bounds_from_data(_X_bdHPP, ["b", "dH", "Pltb_m", "Pbend_m"])
    BOUNDS_bdHPP["b"] = (b_lo_box, b_hi_box)

    return {
        "BOUNDS_bH": BOUNDS_bH,
        "configs": {
            "b_H": {"transform": to_bH, "bounds": BOUNDS_bH, "ndim": 2},
            "b_dH_R": {"transform": to_bdHR, "bounds": BOUNDS_bdHR, "ndim": 3},
            "Pltb_Pbend": {"transform": to_Pltb_Pbend, "bounds": BOUNDS_PP, "ndim": 2},
            "b_Pltb_Pbend": {"transform": to_b_Pltb_Pbend, "bounds": BOUNDS_bPP, "ndim": 3},
            "b_dH_Pltb_Pbend": {
                "transform": to_b_dH_Pltb_Pbend,
                "bounds": BOUNDS_bdHPP,
                "ndim": 4,
            },
        },
    }


def normalize(X, bounds):
    X_n = np.copy(X).astype(float)
    keys = list(bounds.keys())
    for i, k in enumerate(keys):
        lo, hi = bounds[k]
        X_n[:, i] = (X[:, i] - lo) / (hi - lo)
    return X_n


def train_gp(X, y, bounds, alpha=1e-4):
    X_n = normalize(X, bounds)
    y_log = np.log(y)
    y_mean = np.mean(y_log)
    y_c = y_log - y_mean
    nd = X.shape[1]
    ls_bounds = (0.15, 3.0)
    base = Matern(length_scale=[0.5] * nd, length_scale_bounds=ls_bounds, nu=2.5)
    kernel = ConstantKernel(1.0) * base
    gp = GaussianProcessRegressor(
        kernel=kernel, n_restarts_optimizer=15, alpha=alpha, normalize_y=False
    )
    gp.fit(X_n, y_c)
    return gp, X_n, y_c, y_mean


def recommend_in_bH(
    gp, y_c, y_mean, bounds, transform_fn, b_lo, b_hi, H_lo=12.0, H_hi=23.0, n_cand=5000
):
    b_cand = np.random.uniform(b_lo, b_hi, n_cand)
    H_cand = np.random.uniform(H_lo, H_hi, n_cand)
    X_cand = transform_fn(b_cand, H_cand)
    X_cand_n = normalize(X_cand, bounds)
    mu, sig = gp.predict(X_cand_n, return_std=True)

    best_y = np.max(y_c)
    Z = np.where(sig > 1e-9, (mu - best_y) / sig, 0.0)
    acq = np.where(
        sig > 1e-9,
        (mu - best_y) * norm.cdf(Z) + sig * norm.pdf(Z),
        0.0,
    )
    idx = np.argmax(acq)
    pred_strw = np.exp(mu[idx] + y_mean)
    return b_cand[idx], H_cand[idx], pred_strw


STRONG_THRESHOLD = 31.75


def load_full_data():
    print("Downloading full dataset...")
    with urllib.request.urlopen(DATA_URL) as r:
        df = pd.read_csv(io.StringIO(r.read().decode("utf-8")))
    b_all = df["b_web_mm"].values.astype(float)
    H_all = df["H_web_mm"].values.astype(float)
    y_all = df["Str/w N/g"].values.astype(float)
    return df, b_all, H_all, y_all


def run_ablation():
    df_subset = pd.read_csv(SUBSET_CSV)
    print(f"Subset CSV: {SUBSET_CSV} ({len(df_subset)} rows)")

    _, b_all, H_all, y_all = load_full_data()

    def build_ground_truth():
        X_gt = to_b_dH_Pltb_Pbend(b_all, H_all)
        gt_bounds = _bounds_from_data(X_gt, ["b", "dH", "Pltb_m", "Pbend_m"])
        gt_bounds["b"] = (1.0, 8.0)
        gp_gt, _, _, y_gt_mean = train_gp(X_gt, y_all, gt_bounds, alpha=3e-5)
        return gp_gt, gt_bounds, y_gt_mean

    def eval_gt(gp_gt, gt_bounds, y_gt_mean, b_rec, H_rec):
        X_pt = to_b_dH_Pltb_Pbend(np.array([b_rec]), np.array([H_rec]))
        X_pt_n = normalize(X_pt, gt_bounds)
        mu, sig = gp_gt.predict(X_pt_n, return_std=True)
        return np.exp(mu[0] + y_gt_mean), sig[0] ** 2

    def dist_to_strong(b_rec, H_rec):
        mask = y_all >= STRONG_THRESHOLD
        if not np.any(mask):
            return 1.0
        b_s, H_s = b_all[mask], H_all[mask]
        b_n = (b_rec - 1.0) / 7.0
        H_n = (H_rec - 12.0) / 11.0
        b_sn = (b_s - 1.0) / 7.0
        H_sn = (H_s - 12.0) / 11.0
        return float(np.min(np.sqrt((b_n - b_sn) ** 2 + (H_n - H_sn) ** 2)))

    print("Building ground-truth GP...")
    gp_gt, gt_bounds, y_gt_mean = build_ground_truth()

    b_sub = df_subset["b_web_mm"].values.astype(float)
    H_sub = df_subset["H_web_mm"].values.astype(float)
    y_sub = df_subset["Str/w N/g"].values.astype(float)

    scenarios = [
        ("n13_all", b_sub, H_sub, y_sub, 1.0, 8.0),
        (
            "n13_train_b_ge2_bo_b_ge2",
            b_sub[b_sub >= 2.0],
            H_sub[b_sub >= 2.0],
            y_sub[b_sub >= 2.0],
            2.0,
            8.0,
        ),
    ]

    NOISE = 1e-4
    np.random.seed(42)
    results = []
    t0 = time.time()

    for name, b_tr, H_tr, y_tr, b_lo, b_hi in scenarios:
        print(f"\n--- Scenario {name}: n_train={len(b_tr)} b_BO in [{b_lo},{b_hi}] ---")
        pack = build_param_configs(b_tr, H_tr, b_lo, b_hi)
        BOUNDS_BO = pack["BOUNDS_bH"]

        for pname, cfg in pack["configs"].items():
            try:
                X_tr = cfg["transform"](b_tr, H_tr)
                bds = cfg["bounds"]
                gp, X_n, y_c, y_mean = train_gp(X_tr, y_tr, bds, alpha=NOISE)
                b_rec, H_rec, pred = recommend_in_bH(
                    gp,
                    y_c,
                    y_mean,
                    bds,
                    cfg["transform"],
                    b_lo,
                    b_hi,
                    BOUNDS_BO["H"][0],
                    BOUNDS_BO["H"][1],
                )
                gt_strw, gt_var = eval_gt(gp_gt, gt_bounds, y_gt_mean, b_rec, H_rec)
                d_strong = dist_to_strong(b_rec, H_rec)
                ls = gp.kernel_.k2.length_scale
                results.append(
                    {
                        "subset": name,
                        "param": pname,
                        "kernel": "matern",
                        "acquisition": "ei",
                        "kappa": np.nan,
                        "noise": NOISE,
                        "n_train": len(b_tr),
                        "b_lo_bo": b_lo,
                        "b_rec": round(float(b_rec), 3),
                        "H_rec": round(float(H_rec), 3),
                        "pred_strw": round(float(pred), 2),
                        "gt_strw": round(float(gt_strw), 2),
                        "gt_var": round(float(gt_var), 6),
                        "dist_to_strong": round(d_strong, 4),
                        "in_strong_zone": d_strong < 0.15,
                        "length_scales": [round(float(x), 3) for x in ls],
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "subset": name,
                        "param": pname,
                        "error": str(e),
                    }
                )

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")
    return pd.DataFrame(results)


if __name__ == "__main__":
    df_results = run_ablation()
    df_results.to_csv(OUT_CSV, index=False)
    print(f"Saved {len(df_results)} rows to {OUT_CSV}")
    print()
    ok = df_results.dropna(subset=["gt_strw"])
    print(ok.to_string(index=False))
