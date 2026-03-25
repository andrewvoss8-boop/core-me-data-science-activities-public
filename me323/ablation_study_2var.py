"""
Retrospective BO Ablation Study -- I-beam 2-variable data

Train on the first 16 beams. For every combination of
  parameterization x kernel x length-scale bounds x acquisition x noise
generate a single next-beam recommendation, then score it against a
ground-truth GP trained on ALL 27 beams.

Parameterizations:
  (b, H)        -- raw design variables
  (b, dH, R)    -- physics-informed 3-param
  (dH, R)       -- physics-only 2-param

Noise baseline: sample variance from repeated test of strongest beam
(Beam 17 & 24, both b=4.5 H=14.5, Str/w 32.04 & 32.28).
"""

import pandas as pd
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, RBF, ConstantKernel
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import norm
import itertools
import warnings
import time
warnings.filterwarnings("ignore")

# =====================================================================
# PHYSICS
# =====================================================================
TOTAL_HEIGHT = 25.0
B_FIXED = 16.0
LENGTH_M = 0.2023
YIELD_STRENGTH = 76e6
E_MODULUS = 2.5e9
G_MODULUS = E_MODULUS / 2.6
C1_3PT = 1.35
MATERIAL_DENSITY = 1240

def _fillet_props(r_m):
    if r_m <= 0:
        return 0.0, 0.0
    A_f = r_m**2 * (4 - np.pi) / 4
    c_f = 2 * r_m / (3 * (4 - np.pi))
    return A_f, c_f

def calc_Ix(H, h, B, b, r=0):
    H_m, h_m, B_m, b_m, r_m = H/1e3, h/1e3, B/1e3, b/1e3, r/1e3
    Ix = (H_m**3 * b_m) / 12 + 2 * ((h_m**3 * B_m) / 12 + h_m * B_m * ((H_m + h_m) / 2)**2)
    A_f, c_f = _fillet_props(r_m)
    if A_f > 0:
        d_x = H_m / 2 + c_f
        Il = r_m**4 * (16 - 3 * np.pi) / 48
        Ix += 4 * (Il - A_f * c_f**2 + A_f * d_x**2)
    return Ix

def calc_Iy(H, h, B, b, r=0):
    H_m, h_m, B_m, b_m, r_m = H/1e3, h/1e3, B/1e3, b/1e3, r/1e3
    Iy = (H_m * b_m**3) / 12 + 2 * (h_m * B_m**3) / 12
    A_f, c_f = _fillet_props(r_m)
    if A_f > 0:
        d_y = b_m / 2 + c_f
        Il = r_m**4 * (16 - 3 * np.pi) / 48
        Iy += 4 * (Il - A_f * c_f**2 + A_f * d_y**2)
    return Iy

def calc_J(H, h, B, b, r=0):
    H_m, h_m, B_m, b_m, r_m = H/1e3, h/1e3, B/1e3, b/1e3, r/1e3
    J = (H_m * b_m**3 + 2 * B_m * h_m**3) / 3
    if r_m > 0:
        J += 4 * 0.15 * r_m**4
    return J

def calc_mass(H, h, B, b, r=0):
    H_m, h_m, B_m, b_m, r_m = H/1e3, h/1e3, B/1e3, b/1e3, r/1e3
    A = H_m * b_m + 2 * h_m * B_m
    A_f, _ = _fillet_props(r_m)
    return MATERIAL_DENSITY * LENGTH_M * (A + 4 * A_f) * 1000

def calc_str_w(H, B, b, r=0):
    h = (TOTAL_HEIGHT - H) / 2.0
    Ix = calc_Ix(H, h, B, b, r)
    strength = (4 * YIELD_STRENGTH * Ix) / (0.0125 * LENGTH_M)
    mass = calc_mass(H, h, B, b, r)
    if mass <= 0:
        return 0.0
    return strength / mass

def find_H_opt(b, B=B_FIXED, r=0):
    def obj(H):
        if H < 12.0 or H > 23.4:
            return 1e10
        h = (TOTAL_HEIGHT - H) / 2.0
        if h < 0 or h > 6.5:
            return 1e10
        return -calc_str_w(H, B, b, r)
    return minimize_scalar(obj, bounds=(12.0, 23.4), method='bounded').x

def stability_ratio(H, h, B, b, r=0):
    Iy = calc_Iy(H, h, B, b, r)
    J = calc_J(H, h, B, b, r)
    if Iy <= 0 or J <= 0:
        return 0.0
    Mcr = (C1_3PT * np.pi / LENGTH_M) * np.sqrt(E_MODULUS * Iy * G_MODULUS * J)
    Ix = calc_Ix(H, h, B, b, r)
    y_max = (H / 1e3 + h / 1e3)
    if y_max <= 0:
        return 0.0
    My = YIELD_STRENGTH * Ix / y_max
    if My <= 0:
        return 0.0
    return Mcr / My

def bH_to_R(b, H):
    h = (TOTAL_HEIGHT - H) / 2.0
    if h <= 0:
        return 0.0
    return stability_ratio(H, h, B_FIXED, b)

def bH_to_dH(b, H):
    return H - find_H_opt(b)

# =====================================================================
# DATA
# =====================================================================
CSV_URL = "https://raw.githubusercontent.com/andrewvoss8-boop/core-me-data-science-activities-public/main/data/I_beam_data_2var.csv"

def load_data():
    df = pd.read_csv(CSV_URL)
    b_all = df['b_web_mm'].values.astype(float)
    H_all = df['H_web_mm'].values.astype(float)
    y_all = df['Str/w N/g'].values.astype(float)
    return b_all, H_all, y_all

# =====================================================================
# PARAMETERIZATION TRANSFORMS
# =====================================================================
BOUNDS_bH = {'b': (1.0, 8.0), 'H': (12.0, 23.0)}
BOUNDS_bdHR = {'b': (1.0, 8.0), 'dH': (-6.0, 4.0), 'R': (0.0, 6.0)}
BOUNDS_dHR = {'dH': (-6.0, 4.0), 'R': (0.0, 6.0)}

def to_bH(b, H):
    return np.column_stack([b, H])

def to_bdHR(b, H):
    n = len(b)
    out = np.zeros((n, 3))
    for i in range(n):
        out[i, 0] = b[i]
        out[i, 1] = bH_to_dH(b[i], H[i])
        out[i, 2] = bH_to_R(b[i], H[i])
    return out

def to_dHR(b, H):
    n = len(b)
    out = np.zeros((n, 2))
    for i in range(n):
        out[i, 0] = bH_to_dH(b[i], H[i])
        out[i, 1] = bH_to_R(b[i], H[i])
    return out

PARAM_CONFIGS = {
    'b_H': {'transform': to_bH, 'bounds': BOUNDS_bH, 'ndim': 2},
    'b_dH_R': {'transform': to_bdHR, 'bounds': BOUNDS_bdHR, 'ndim': 3},
    'dH_R': {'transform': to_dHR, 'bounds': BOUNDS_dHR, 'ndim': 2},
}

# =====================================================================
# NORMALIZE / GP
# =====================================================================
def normalize(X, bounds):
    X_n = np.copy(X).astype(float)
    keys = list(bounds.keys())
    for i, k in enumerate(keys):
        lo, hi = bounds[k]
        X_n[:, i] = (X[:, i] - lo) / (hi - lo)
    return X_n

def denormalize(X_n, bounds):
    X = np.copy(X_n)
    keys = list(bounds.keys())
    for i, k in enumerate(keys):
        lo, hi = bounds[k]
        X[:, i] = X_n[:, i] * (hi - lo) + lo
    return X

def train_gp(X, y, bounds, kernel_type='matern', alpha=1e-4,
             ls_bounds_style='adaptive'):
    X_n = normalize(X, bounds)
    y_log = np.log(y)
    y_mean = np.mean(y_log)
    y_c = y_log - y_mean
    nd = X.shape[1]

    if ls_bounds_style == 'adaptive':
        ls_bounds = (0.15, 3.0)
    elif ls_bounds_style == 'tight':
        ls_bounds = (0.1, 2.0)
    elif ls_bounds_style == 'loose':
        ls_bounds = (0.05, 10.0)
    else:
        ls_bounds = (0.01, 20.0)

    if kernel_type == 'matern':
        base = Matern(length_scale=[0.5] * nd, length_scale_bounds=ls_bounds, nu=2.5)
    else:
        base = RBF(length_scale=[0.5] * nd, length_scale_bounds=ls_bounds)

    kernel = ConstantKernel(1.0) * base
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=15,
                                  alpha=alpha, normalize_y=False)
    gp.fit(X_n, y_c)
    return gp, X_n, y_c, y_mean

# =====================================================================
# ACQUISITION (single best recommendation)
# =====================================================================
def best_recommendation(gp, y_centered, bounds, acq_type='ei', kappa=2.0,
                        n_starts=50):
    """Return the single best point in normalized space."""
    nd = len(bounds)

    if acq_type == 'ei':
        best_y = np.max(y_centered)
        def neg_acq(x):
            mu, sig = gp.predict(x.reshape(1, -1), return_std=True)
            if sig < 1e-9:
                return 0.0
            Z = (mu - best_y) / sig
            return -(((mu - best_y) * norm.cdf(Z) + sig * norm.pdf(Z)).item())
    else:
        def neg_acq(x):
            mu, sig = gp.predict(x.reshape(1, -1), return_std=True)
            return -(mu + kappa * sig).item()

    best_x, best_score = None, 1e10
    for _ in range(n_starts):
        x0 = np.random.uniform(0, 1, nd)
        res = minimize(neg_acq, x0, bounds=[(0, 1)] * nd, method='L-BFGS-B')
        if res.fun < best_score:
            best_score = res.fun
            best_x = res.x
    return best_x

def recommend_in_bH_space(gp, y_centered, y_mean, bounds, param_name,
                          b_train, H_train, acq_type='ei', kappa=2.0,
                          n_cand=5000):
    """
    For all parameterizations, generate candidates in physical (b,H),
    transform, score with GP, return best (b, H) and predicted Str/w.
    """
    b_cand = np.random.uniform(BOUNDS_bH['b'][0], BOUNDS_bH['b'][1], n_cand)
    H_cand = np.random.uniform(BOUNDS_bH['H'][0], BOUNDS_bH['H'][1], n_cand)

    cfg = PARAM_CONFIGS[param_name]
    X_cand = cfg['transform'](b_cand, H_cand)
    X_cand_n = normalize(X_cand, cfg['bounds'])

    mu, sig = gp.predict(X_cand_n, return_std=True)

    if acq_type == 'ei':
        best_y = np.max(y_centered)
        Z = np.where(sig > 1e-9, (mu - best_y) / sig, 0.0)
        acq_vals = np.where(sig > 1e-9,
                            (mu - best_y) * norm.cdf(Z) + sig * norm.pdf(Z),
                            0.0)
    else:
        acq_vals = mu + kappa * sig

    idx = np.argmax(acq_vals)
    pred_strw = np.exp(mu[idx] + y_mean)
    return b_cand[idx], H_cand[idx], pred_strw

# =====================================================================
# GROUND TRUTH
# =====================================================================
def build_ground_truth(b_all, H_all, y_all):
    """GP on all 27 beams in (b, H) space -- our best estimate of reality."""
    X_gt = to_bH(b_all, H_all)
    gp_gt, X_gt_n, y_gt_c, y_gt_mean = train_gp(
        X_gt, y_all, BOUNDS_bH, kernel_type='matern',
        alpha=3e-5, ls_bounds_style='adaptive')
    return gp_gt, y_gt_mean

def eval_ground_truth(gp_gt, y_gt_mean, b_rec, H_rec):
    """Predict Str/w at recommendation from ground truth GP."""
    x = normalize(np.array([[b_rec, H_rec]]), BOUNDS_bH)
    mu, sig = gp_gt.predict(x, return_std=True)
    return np.exp(mu[0] + y_gt_mean), sig[0]

# =====================================================================
# KNOWN STRONG BEAMS (from all 27)
# =====================================================================
def distance_to_strong_zone(b_rec, H_rec, b_all, H_all, y_all, threshold=30.0):
    """Min Euclidean distance (in normalized bH space) to any beam with Str/w > threshold."""
    mask = y_all >= threshold
    if not np.any(mask):
        return 1.0
    b_s = b_all[mask]
    H_s = H_all[mask]
    b_n = (b_rec - BOUNDS_bH['b'][0]) / (BOUNDS_bH['b'][1] - BOUNDS_bH['b'][0])
    H_n = (H_rec - BOUNDS_bH['H'][0]) / (BOUNDS_bH['H'][1] - BOUNDS_bH['H'][0])
    b_sn = (b_s - BOUNDS_bH['b'][0]) / (BOUNDS_bH['b'][1] - BOUNDS_bH['b'][0])
    H_sn = (H_s - BOUNDS_bH['H'][0]) / (BOUNDS_bH['H'][1] - BOUNDS_bH['H'][0])
    dists = np.sqrt((b_n - b_sn)**2 + (H_n - H_sn)**2)
    return np.min(dists)

# =====================================================================
# MAIN SWEEP
# =====================================================================
def run_ablation():
    print("Loading data...")
    b_all, H_all, y_all = load_data()

    b_train = b_all[:16]
    H_train = H_all[:16]
    y_train = y_all[:16]

    # Noise baseline from repeated beam (rows 19, 26 = Beam 17 & 24)
    y_repeat = y_all[[19, 26]]
    log_repeat = np.log(y_repeat)
    baseline_var = np.var(log_repeat, ddof=1)
    print(f"Noise baseline (log-space variance from repeats): {baseline_var:.2e}")

    # Ground truth GP
    print("Training ground truth GP on all 27 beams...")
    gp_gt, y_gt_mean = build_ground_truth(b_all, H_all, y_all)

    # Factorial levels
    parameterizations = ['b_H', 'b_dH_R', 'dH_R']
    kernels = ['matern', 'rbf']
    ls_styles = ['adaptive', 'tight', 'loose']
    acquisitions = [('ei', None), ('ucb', 1.0), ('ucb', 2.0), ('ucb', 3.0)]
    noise_levels = [baseline_var, 1e-4, 3e-4, 1e-3, 3e-3]

    total = (len(parameterizations) * len(kernels) * len(ls_styles) *
             len(acquisitions) * len(noise_levels))
    print(f"\nTotal configs: {total}")
    print("Running...\n")

    results = []
    done = 0
    t0 = time.time()

    for param_name in parameterizations:
        cfg = PARAM_CONFIGS[param_name]
        X_train_param = cfg['transform'](b_train, H_train)
        bds = cfg['bounds']

        for kern in kernels:
            for ls_style in ls_styles:
                for (acq_type, kappa) in acquisitions:
                    for noise in noise_levels:
                        done += 1
                        if done % 30 == 0:
                            elapsed = time.time() - t0
                            print(f"  {done}/{total}  ({elapsed:.0f}s)")

                        try:
                            gp, X_n, y_c, y_mean = train_gp(
                                X_train_param, y_train, bds,
                                kernel_type=kern, alpha=noise,
                                ls_bounds_style=ls_style)

                            b_rec, H_rec, pred_strw = recommend_in_bH_space(
                                gp, y_c, y_mean, bds, param_name,
                                b_train, H_train,
                                acq_type=acq_type,
                                kappa=kappa if kappa else 2.0)

                            gt_strw, gt_sig = eval_ground_truth(gp_gt, y_gt_mean, b_rec, H_rec)
                            dist_strong = distance_to_strong_zone(
                                b_rec, H_rec, b_all, H_all, y_all, threshold=30.0)

                            ls = gp.kernel_.k2.length_scale

                            results.append({
                                'param': param_name,
                                'kernel': kern,
                                'ls_bounds': ls_style,
                                'acquisition': acq_type,
                                'kappa': kappa,
                                'noise': noise,
                                'b_rec': round(b_rec, 3),
                                'H_rec': round(H_rec, 3),
                                'pred_strw': round(pred_strw, 2),
                                'gt_strw': round(gt_strw, 2),
                                'gt_sig': round(gt_sig, 4),
                                'dist_to_strong': round(dist_strong, 4),
                                'in_strong_zone': dist_strong < 0.15,
                                'gt_above_30': gt_strw >= 30.0,
                                'length_scales': [round(x, 3) for x in ls],
                            })

                        except Exception as e:
                            results.append({
                                'param': param_name,
                                'kernel': kern,
                                'ls_bounds': ls_style,
                                'acquisition': acq_type,
                                'kappa': kappa,
                                'noise': noise,
                                'error': str(e),
                            })

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")
    df = pd.DataFrame(results)
    return df

# =====================================================================
# ANALYSIS
# =====================================================================
def analyze(df):
    ok = df[~df['gt_strw'].isna()].copy()
    print("=" * 80)
    print("RETROSPECTIVE BO ABLATION -- I-BEAM 2-VAR DATA (first 16 beams)")
    print("=" * 80)
    print(f"\nConfigs run: {len(ok)}  (errors: {len(df) - len(ok)})")

    print(f"\n--- OVERALL ---")
    print(f"  GT Str/w > 30:   {ok['gt_above_30'].sum()}/{len(ok)}  "
          f"({100*ok['gt_above_30'].mean():.1f}%)")
    print(f"  In strong zone:  {ok['in_strong_zone'].sum()}/{len(ok)}  "
          f"({100*ok['in_strong_zone'].mean():.1f}%)")
    print(f"  Mean GT Str/w:   {ok['gt_strw'].mean():.2f}")
    print(f"  Median GT Str/w: {ok['gt_strw'].median():.2f}")

    for factor in ['param', 'kernel', 'ls_bounds', 'acquisition', 'noise']:
        print(f"\n--- By {factor} ---")
        grp = ok.groupby(factor)
        summary = grp.agg(
            n=('gt_strw', 'count'),
            mean_gt=('gt_strw', 'mean'),
            median_gt=('gt_strw', 'median'),
            pct_above_30=('gt_above_30', 'mean'),
            pct_in_strong=('in_strong_zone', 'mean'),
            mean_dist=('dist_to_strong', 'mean'),
        ).round(3)
        summary['pct_above_30'] = (summary['pct_above_30'] * 100).round(1)
        summary['pct_in_strong'] = (summary['pct_in_strong'] * 100).round(1)
        print(summary.to_string())

    # Top 15 by GT Str/w
    print(f"\n--- TOP 15 CONFIGS (by ground-truth Str/w) ---")
    top = ok.nlargest(15, 'gt_strw')
    cols = ['param', 'kernel', 'ls_bounds', 'acquisition', 'kappa', 'noise',
            'b_rec', 'H_rec', 'gt_strw', 'dist_to_strong']
    print(top[cols].to_string(index=False))

    # Bottom 10
    print(f"\n--- BOTTOM 10 CONFIGS ---")
    bot = ok.nsmallest(10, 'gt_strw')
    print(bot[cols].to_string(index=False))

    # Interaction: param x acquisition
    print(f"\n--- PARAMETERIZATION x ACQUISITION (mean GT Str/w) ---")
    pivot = ok.pivot_table(values='gt_strw', index='param',
                           columns='acquisition', aggfunc='mean').round(2)
    print(pivot.to_string())

    # Interaction: param x kernel
    print(f"\n--- PARAMETERIZATION x KERNEL (mean GT Str/w) ---")
    pivot2 = ok.pivot_table(values='gt_strw', index='param',
                            columns='kernel', aggfunc='mean').round(2)
    print(pivot2.to_string())

    # Interaction: param x noise
    print(f"\n--- PARAMETERIZATION x NOISE (mean GT Str/w) ---")
    pivot3 = ok.pivot_table(values='gt_strw', index='param',
                            columns='noise', aggfunc='mean').round(2)
    print(pivot3.to_string())

    return ok

# =====================================================================
if __name__ == '__main__':
    np.random.seed(42)
    df = run_ablation()
    csv_path = 'me323/ablation_results_2var.csv'
    df.to_csv(csv_path, index=False)
    print(f"\nSaved to {csv_path}")
    ok = analyze(df)
