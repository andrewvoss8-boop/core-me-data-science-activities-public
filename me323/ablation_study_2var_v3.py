"""
Ablation v3: focused sweep on the 13-beam even-spaced subset.

Two training sets:
  n13_all  -- all 13 beams from lhs16_subset_bH_even_n13.csv
  n10_b2   -- same 13 minus beams with b < 2 (beams 7, 12, 13 removed);
              BO candidates also constrained to b >= 2.0

Fixed: noise = 1e-4, acquisition = EI, kernels = [matern, rbf].
All 5 parameterizations from v2.

Ground truth: same b_dH_Pltb_Pbend GP on full CSV (all beams).
"""

import pathlib
import time
import warnings

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, RBF

warnings.filterwarnings("ignore")

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBSET_CSV = REPO / "data" / "lhs16_subset_bH_even_n13.csv"
FULL_CSV = REPO / "data" / "I_beam_data_2var.csv"
OUT_CSV = REPO / "me323" / "ablation_results_2var_v3.csv"

# ── physics constants ──────────────────────────────────────────────────
TOTAL_HEIGHT = 25.0
B_FIXED = 16.0
LENGTH_M = 0.2023
SIGMA_Y = 81.8e6
E_MOD = 2.74e9
G_MOD = E_MOD / 2.6
C1 = 1.35
DENSITY = 1210
Y_MAX = TOTAL_HEIGHT / 2e3


# ── section properties (mm in, m^4 out) ───────────────────────────────
def calc_Ix(H, b, B=B_FIXED):
    H_m, b_m, B_m = H / 1e3, b / 1e3, B / 1e3
    h_m = (TOTAL_HEIGHT / 1e3 - H_m) / 2.0
    if h_m <= 0: return 0.0
    return (b_m * H_m**3) / 12 + 2 * (B_m * h_m**3 / 12 + B_m * h_m * ((H_m + h_m) / 2) ** 2)

def calc_Iy(H, b, B=B_FIXED):
    H_m, b_m, B_m = H / 1e3, b / 1e3, B / 1e3
    h_m = (TOTAL_HEIGHT / 1e3 - H_m) / 2.0
    if h_m <= 0: return 0.0
    return (H_m * b_m**3) / 12 + 2 * (h_m * B_m**3) / 12

def calc_J(H, b, B=B_FIXED):
    H_m, b_m, B_m = H / 1e3, b / 1e3, B / 1e3
    h_m = (TOTAL_HEIGHT / 1e3 - H_m) / 2.0
    if h_m <= 0: return 0.0
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
    if h_m <= 0: return 0.0
    return DENSITY * LENGTH_M * (H_m * b_m + 2 * h_m * B_m) * 1000

def calc_P_bend(H, b):
    Ix = calc_Ix(H, b)
    return 4 * SIGMA_Y * Ix / Y_MAX / LENGTH_M

def calc_P_ltb(H, b):
    Iy, J = calc_Iy(H, b), calc_J(H, b)
    if Iy <= 0 or J <= 0: return 0.0
    Mcr = (C1 * np.pi / LENGTH_M) * np.sqrt(E_MOD * Iy * G_MOD * J)
    return 4 * Mcr / LENGTH_M

def calc_R(H, b):
    Ix = calc_Ix(H, b)
    My = SIGMA_Y * Ix / Y_MAX
    if My <= 0: return 0.0
    Iy, J = calc_Iy(H, b), calc_J(H, b)
    if Iy <= 0 or J <= 0: return 0.0
    Mcr = (C1 * np.pi / LENGTH_M) * np.sqrt(E_MOD * Iy * G_MOD * J)
    return Mcr / My

def calc_str_w(H, b):
    P, m = calc_P_bend(H, b), calc_mass(H, b)
    return P / m if m > 0 else 0.0

def find_H_opt(b):
    def obj(H):
        h = (TOTAL_HEIGHT - H) / 2.0
        if h < 0 or h > 6.5: return 1e10
        return -calc_str_w(H, b)
    return minimize_scalar(obj, bounds=(12.0, 23.4), method="bounded").x


# ── parameterizations ─────────────────────────────────────────────────
def _Pltb_m(b, H):
    m = calc_mass(H, b); return calc_P_ltb(H, b) / m if m > 0 else 0.0

def _Pbend_m(b, H):
    m = calc_mass(H, b); return calc_P_bend(H, b) / m if m > 0 else 0.0

def _dH(b, H): return H - find_H_opt(b)
def _R(b, H):  return calc_R(H, b)

def to_bH(b, H):             return np.column_stack([b, H])
def to_bdHR(b, H):           return np.column_stack([b, [_dH(bi, Hi) for bi, Hi in zip(b, H)], [_R(bi, Hi) for bi, Hi in zip(b, H)]])
def to_PP(b, H):             return np.column_stack([[_Pltb_m(bi, Hi) for bi, Hi in zip(b, H)], [_Pbend_m(bi, Hi) for bi, Hi in zip(b, H)]])
def to_bPP(b, H):            return np.column_stack([b, [_Pltb_m(bi, Hi) for bi, Hi in zip(b, H)], [_Pbend_m(bi, Hi) for bi, Hi in zip(b, H)]])
def to_bdHPP(b, H):          return np.column_stack([b, [_dH(bi, Hi) for bi, Hi in zip(b, H)], [_Pltb_m(bi, Hi) for bi, Hi in zip(b, H)], [_Pbend_m(bi, Hi) for bi, Hi in zip(b, H)]])


# ── GP training ───────────────────────────────────────────────────────
def normalize(X, bounds):
    X_n = np.copy(X).astype(float)
    for i, k in enumerate(bounds):
        lo, hi = bounds[k]
        X_n[:, i] = (X[:, i] - lo) / (hi - lo)
    return X_n

def train_gp(X, y, bounds, kernel_type="matern", alpha=1e-4):
    X_n = normalize(X, bounds)
    y_log = np.log(y)
    y_mean = y_log.mean()
    y_c = y_log - y_mean
    nd = X.shape[1]
    ls_bounds = (0.15, 3.0)
    if kernel_type == "matern":
        base = Matern(length_scale=[0.5] * nd, length_scale_bounds=ls_bounds, nu=2.5)
    else:
        base = RBF(length_scale=[0.5] * nd, length_scale_bounds=ls_bounds)
    kernel = ConstantKernel(1.0) * base
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=15, alpha=alpha, normalize_y=False)
    gp.fit(X_n, y_c)
    return gp, X_n, y_c, y_mean


# ── acquisition (EI only) ─────────────────────────────────────────────
def recommend_ei(gp, y_c, y_mean, bounds, transform_fn, b_lo=1.0, n_cand=5000):
    b_cand = np.random.uniform(b_lo, 8.0, n_cand)
    H_cand = np.random.uniform(12.0, 23.0, n_cand)
    X_cand = transform_fn(b_cand, H_cand)
    X_cand_n = normalize(X_cand, bounds)
    mu, sig = gp.predict(X_cand_n, return_std=True)
    best_y = np.max(y_c)
    Z = np.where(sig > 1e-9, (mu - best_y) / sig, 0.0)
    acq = np.where(sig > 1e-9, (mu - best_y) * norm.cdf(Z) + sig * norm.pdf(Z), 0.0)
    idx = np.argmax(acq)
    return b_cand[idx], H_cand[idx], np.exp(mu[idx] + y_mean)


# ── bounds helper ─────────────────────────────────────────────────────
def _bounds_from_data(X, names, margin=0.15):
    bds = {}
    for i, nm in enumerate(names):
        lo, hi = X[:, i].min(), X[:, i].max()
        span = max(hi - lo, abs(lo) * 0.1 + 1e-6)
        bds[nm] = (lo - margin * span, hi + margin * span)
    return bds

def make_bounds(b_arr, H_arr, b_lo=1.0):
    """Build the full bounds dict set for all 5 parameterizations."""
    X_bdHR = to_bdHR(b_arr, H_arr)
    X_PP   = to_PP(b_arr, H_arr)
    X_bPP  = to_bPP(b_arr, H_arr)
    X_bdHPP = to_bdHPP(b_arr, H_arr)

    bds_bH    = {"b": (b_lo, 8.0), "H": (12.0, 23.0)}
    bds_bdHR  = _bounds_from_data(X_bdHR, ["b", "dH", "R"]);  bds_bdHR["b"] = (b_lo, 8.0)
    bds_PP    = _bounds_from_data(X_PP, ["Pltb_m", "Pbend_m"])
    bds_bPP   = _bounds_from_data(X_bPP, ["b", "Pltb_m", "Pbend_m"]);  bds_bPP["b"] = (b_lo, 8.0)
    bds_bdHPP = _bounds_from_data(X_bdHPP, ["b", "dH", "Pltb_m", "Pbend_m"]);  bds_bdHPP["b"] = (b_lo, 8.0)

    return {
        "b_H":             {"transform": to_bH,    "bounds": bds_bH,    "ndim": 2},
        "b_dH_R":          {"transform": to_bdHR,  "bounds": bds_bdHR,  "ndim": 3},
        "Pltb_Pbend":      {"transform": to_PP,    "bounds": bds_PP,    "ndim": 2},
        "b_Pltb_Pbend":    {"transform": to_bPP,   "bounds": bds_bPP,   "ndim": 3},
        "b_dH_Pltb_Pbend": {"transform": to_bdHPP, "bounds": bds_bdHPP, "ndim": 4},
    }


# ── ground truth (same as v2) ────────────────────────────────────────
STRONG_THRESHOLD = 31.75

def build_ground_truth(b_all, H_all, y_all):
    X_gt = to_bdHPP(b_all, H_all)
    gt_bounds = _bounds_from_data(X_gt, ["b", "dH", "Pltb_m", "Pbend_m"])
    gt_bounds["b"] = (1.0, 8.0)
    gp_gt, _, _, y_gt_mean = train_gp(X_gt, y_all, gt_bounds, kernel_type="matern", alpha=3e-5)
    return gp_gt, gt_bounds, y_gt_mean

def eval_gt(gp_gt, gt_bounds, y_gt_mean, b_rec, H_rec):
    X_pt = to_bdHPP(np.array([b_rec]), np.array([H_rec]))
    X_pt_n = normalize(X_pt, gt_bounds)
    mu, sig = gp_gt.predict(X_pt_n, return_std=True)
    return float(np.exp(mu[0] + y_gt_mean)), float(sig[0] ** 2)

def dist_to_strong(b_rec, H_rec, b_all, H_all, y_all):
    mask = y_all >= STRONG_THRESHOLD
    if not np.any(mask): return 1.0
    b_s, H_s = b_all[mask], H_all[mask]
    b_n  = (b_rec - 1.0) / 7.0;  H_n  = (H_rec - 12.0) / 11.0
    b_sn = (b_s   - 1.0) / 7.0;  H_sn = (H_s   - 12.0) / 11.0
    return float(np.min(np.sqrt((b_n - b_sn)**2 + (H_n - H_sn)**2)))


# ── main sweep ────────────────────────────────────────────────────────
NOISE = 1e-4
KERNELS = ["matern", "rbf"]
N_SEEDS = 5  # run each config 5 times with different candidate seeds

def main():
    df_sub = pd.read_csv(SUBSET_CSV)
    df_full = pd.read_csv(FULL_CSV)

    b_sub = df_sub["b_web_mm"].values.astype(float)
    H_sub = df_sub["H_web_mm"].values.astype(float)
    y_sub = df_sub["Str/w N/g"].values.astype(float)

    b_full = df_full["b_web_mm"].values.astype(float)
    H_full = df_full["H_web_mm"].values.astype(float)
    y_full = df_full["Str/w N/g"].values.astype(float)

    # n11_b2: drop beams with b < 2 from the 13-beam subset
    mask_b2 = b_sub >= 2.0
    b_b2, H_b2, y_b2 = b_sub[mask_b2], H_sub[mask_b2], y_sub[mask_b2]

    datasets = [
        ("n13_all", b_sub, H_sub, y_sub, 1.0),   # b_lo=1.0
        ("n10_b2",  b_b2,  H_b2,  y_b2,  2.0),   # b_lo=2.0
    ]

    print(f"Subset CSV: {SUBSET_CSV}  ({len(df_sub)} rows)")
    for name, b, H, y, blo in datasets:
        beams = df_sub.loc[b_sub >= blo if name == "n10_b2" else [True]*len(b_sub), "Beam Number"].tolist() if name == "n10_b2" else df_sub["Beam Number"].tolist()
        print(f"  {name}: {len(b)} beams, b_lo={blo}")

    print(f"\nFull CSV: {FULL_CSV}  ({len(df_full)} rows)")
    print("Building ground-truth GP...")
    gp_gt, gt_bounds, y_gt_mean = build_ground_truth(b_full, H_full, y_full)
    n_strong = np.sum(y_full >= STRONG_THRESHOLD)
    print(f"  strong-zone: {n_strong}/{len(y_full)} beams >= {STRONG_THRESHOLD}")

    results = []
    total = len(datasets) * len(KERNELS) * 5 * N_SEEDS
    print(f"\nConfigs: {total} (2 datasets x 2 kernels x 5 params x {N_SEEDS} seeds)")
    t0 = time.time()
    done = 0

    for ds_name, b_tr, H_tr, y_tr, b_lo in datasets:
        param_cfgs = make_bounds(b_tr, H_tr, b_lo=b_lo)

        for kern in KERNELS:
            for pname, cfg in param_cfgs.items():
                X_tr = cfg["transform"](b_tr, H_tr)
                bds = cfg["bounds"]
                try:
                    gp, X_n, y_c, y_mean = train_gp(X_tr, y_tr, bds, kernel_type=kern, alpha=NOISE)
                except Exception as e:
                    for seed in range(N_SEEDS):
                        results.append({"dataset": ds_name, "param": pname, "kernel": kern, "error": str(e)})
                    done += N_SEEDS
                    continue

                for seed in range(N_SEEDS):
                    done += 1
                    np.random.seed(42 + seed * 1000)
                    try:
                        b_rec, H_rec, pred = recommend_ei(gp, y_c, y_mean, bds, cfg["transform"], b_lo=b_lo)
                        gt_strw, gt_var = eval_gt(gp_gt, gt_bounds, y_gt_mean, b_rec, H_rec)
                        d_strong = dist_to_strong(b_rec, H_rec, b_full, H_full, y_full)
                        ls = gp.kernel_.k2.length_scale

                        results.append({
                            "dataset": ds_name,
                            "param": pname,
                            "kernel": kern,
                            "seed": seed,
                            "noise": NOISE,
                            "b_rec": round(b_rec, 3),
                            "H_rec": round(H_rec, 3),
                            "pred_strw": round(pred, 2),
                            "gt_strw": round(gt_strw, 2),
                            "gt_var": round(gt_var, 6),
                            "dist_to_strong": round(d_strong, 4),
                            "in_strong_zone": d_strong < 0.15,
                            "length_scales": [round(float(x), 3) for x in ls],
                        })
                    except Exception as e:
                        results.append({"dataset": ds_name, "param": pname, "kernel": kern, "seed": seed, "error": str(e)})

                    if done % 10 == 0:
                        print(f"  {done}/{total}  ({time.time()-t0:.0f}s)")

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")

    df = pd.DataFrame(results)
    df.to_csv(OUT_CSV, index=False)
    print(f"Saved {len(df)} rows to {OUT_CSV}")

    # ── analysis ──
    ok = df[~df["gt_strw"].isna()].copy()
    ok["in_strong_zone"] = ok["in_strong_zone"].astype(bool)
    print(f"\nValid rows: {len(ok)}")

    for ds in ok["dataset"].unique():
        sub = ok[ok["dataset"] == ds]
        print(f"\n{'='*60}")
        print(f"Dataset: {ds}  ({len(sub)} rows)")
        print(f"{'='*60}")

        print("\n--- Mean gt_strw by param ---")
        print(sub.groupby("param")["gt_strw"].agg(["mean", "std"]).sort_values("mean", ascending=False))

        print("\n--- Mean gt_strw by param + kernel ---")
        print(sub.groupby(["param", "kernel"])["gt_strw"].mean().unstack("kernel").round(2))

        print("\n--- Strong-zone rate by param ---")
        print(sub.groupby("param")["in_strong_zone"].mean().sort_values(ascending=False))

        print("\n--- Mean gt_var by param ---")
        print(sub.groupby("param")["gt_var"].mean().sort_values())

        cols = ["dataset", "param", "kernel", "seed", "b_rec", "H_rec",
                "gt_strw", "gt_var", "dist_to_strong", "in_strong_zone"]
        print("\n--- Top 10 by gt_strw ---")
        print(sub.sort_values("gt_strw", ascending=False)[cols].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
