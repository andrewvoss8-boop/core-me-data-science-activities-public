"""
INTERACTIVE I-BEAM BAYESIAN OPTIMIZATION TEACHING TOOL
=======================================================
Explore GP regression and Bayesian Optimization concepts by toggling:
- Data subsets (LHS only, all data, custom ranges)
- GP hyperparameters (noise, length scales)
- Acquisition functions (EI vs UCB with different exploration levels)
- Fantasy iterations (sequential vs batch recommendations)
- Visualization types (marginal vs slices, 1D vs 2D)

Educational Focus:
- Understand how noise affects GP uncertainty
- See impact of length scale constraints (ARD vs fixed)
- Compare exploration/exploitation trade-offs
- Visualize sequential (fantasy) vs batch optimization
"""

import pandas as pd
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel
from scipy.stats import norm
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ==========================================
# CONFIGURATION - ADJUST THESE TO EXPLORE
# ==========================================

# ===== DATA SELECTION =====
DATA_MODE = 'all'  # 'lhs_only' (first 15), 'all', 'custom_range', 'top_performers'
CUSTOM_DATA_RANGE = (0, 30)  # If DATA_MODE='custom_range', use beams [start:end]
TOP_N_PERFORMERS = 10  # If DATA_MODE='top_performers', use N best beams

# ===== GP HYPERPARAMETERS =====
NOISE_LEVEL = 1e-3  # Alpha parameter (noise variance): 1e-3 (low), 3e-3 (observed max), 1e-2 (high)
                     # Higher noise = more uncertainty, smoother predictions

LENGTH_SCALE_MODE = 'free'  # 'free' (ARD learns per dimension), 'constrained', 'fixed'
FIXED_LENGTH_SCALES = [0.5, 0.5, 0.5]  # Only used if LENGTH_SCALE_MODE='fixed'
LENGTH_SCALE_BOUNDS = (0.1, 3.0)  # Bounds for learning if 'free' or 'constrained'

# ===== ACQUISITION FUNCTION =====
ACQ_FUNCTION = 'EI'  # 'EI' or 'UCB'
EXPLORE_EXPLOIT_DIAL = 0.05  # 0.0=greedy/exploit, 1.0=exploratory
                              # For EI: controls xi (0.0001 to 0.02)
                              # For UCB: controls kappa (0.2 to 2.0)

# ===== RECOMMENDATION STRATEGY =====
N_RECOMMENDATIONS = 3  # How many beams to recommend
FANTASY_MODE = 'sequential'  # 'sequential' (update GP after each), 'batch' (all at once), 'none' (just first)
                              # Sequential = iterative BO, Batch = parallel testing

# ===== VISUALIZATION CONTROLS =====
PLOT_1D_MARGINAL = True   # Average effect across design space
PLOT_2D_MARGINAL = True   # 2D marginal contours
PLOT_1D_GLOBAL = True     # 1D slices at mean point
PLOT_2D_GLOBAL = True     # 2D contours at mean point

# Slice-specific plots (at particular beam designs)
PLOT_SLICES = True
SLICE_SELECTIONS = ['top_3', 'recommendations']  # 'top_3', 'worst_3', 'recommendations', 'random_5', 'custom'
CUSTOM_SLICE_INDICES = [5, 10, 20]  # If SLICE_SELECTIONS includes 'custom'

MARGINAL_SAMPLES = 200  # For averaging in marginal plots (higher = slower but smoother)

# ===== TEACHING SCENARIOS (PRESETS) =====
# Uncomment one of these to quickly load a teaching scenario:

# SCENARIO = 'noise_comparison'
# SCENARIO = 'length_scale_demo'  
# SCENARIO = 'exploration_demo'
# SCENARIO = 'sequential_vs_batch'
SCENARIO = None  # Use manual settings above

# ==========================================
# APPLY TEACHING SCENARIOS
# ==========================================
if SCENARIO == 'noise_comparison':
    # Show how noise affects predictions
    DATA_MODE = 'lhs_only'
    NOISE_LEVEL = 3e-3  # High noise from observed data
    PLOT_SLICES = False  # Focus on marginal effects
    print("📚 SCENARIO: Noise Comparison - High noise (3e-3) with LHS data only")
    
elif SCENARIO == 'length_scale_demo':
    # Compare free ARD vs fixed length scales
    DATA_MODE = 'all'
    LENGTH_SCALE_MODE = 'free'
    PLOT_2D_MARGINAL = True
    print("📚 SCENARIO: Length Scale Learning - ARD will learn different scales per dimension")
    
elif SCENARIO == 'exploration_demo':
    # Compare greedy vs exploratory
    DATA_MODE = 'all'
    ACQ_FUNCTION = 'EI'
    EXPLORE_EXPLOIT_DIAL = 0.5  # Balanced
    print("📚 SCENARIO: Exploration Demo - Balanced exploration (dial=0.5)")
    
elif SCENARIO == 'sequential_vs_batch':
    # Show sequential BO with fantasy iterations
    DATA_MODE = 'all'
    FANTASY_MODE = 'sequential'
    N_RECOMMENDATIONS = 5
    PLOT_SLICES = True
    SLICE_SELECTIONS = ['recommendations']
    print("📚 SCENARIO: Sequential BO - 5 iterations with fantasy updates")

# ==========================================
# PHYSICS CONSTANTS
# ==========================================
TOTAL_HEIGHT = 25.0
B_FIXED = 16.0
MIN_WEB_THICKNESS = 0.8
MIN_FLANGE_WIDTH = 8.0
MAX_WEB_RATIO = 2/3
MATERIAL_DENSITY = 1240
LENGTH_M = 0.2023
YIELD_STRENGTH = 76000000
BOUNDS_3D = {'b': (0.8, 10.67), 'r': (0.0, 4.0), 'delta_H': (-6.0, 4.0)}
PARAM_NAMES_3D = ['b_web (mm)', 'r_fillet (mm)', 'ΔH (mm)']

# ==========================================
# PHYSICS CALCULATIONS
# ==========================================
def calc_I(H, h, B, b):
    H_m, h_m, B_m, b_m = H/1000, h/1000, B/1000, b/1000
    I_web = (H_m**3 * b_m) / 12
    I_fl = (h_m**3 * B_m) / 12 + h_m * B_m * ((H_m + h_m) / 2)**2
    return I_web + 2*I_fl

def calc_mass(H, h, B, b):
    H_m, h_m, B_m, b_m = H/1000, h/1000, B/1000, b/1000
    return MATERIAL_DENSITY * LENGTH_M * (H_m*b_m + 2*h_m*B_m) * 1000

def calc_strength(H, h, B, b):
    return (4 * YIELD_STRENGTH * calc_I(H, h, B, b)) / (0.0125 * LENGTH_M)

def calc_str_w(H, B, b):
    h = (TOTAL_HEIGHT - H) / 2.0
    return calc_strength(H, h, B, b) / calc_mass(H, h, B, b)

def find_H_opt(b, B=B_FIXED):
    def obj(H):
        if H < 12.0 or H > 23.4: return 1e10
        h = (TOTAL_HEIGHT - H) / 2.0
        if h < 0 or h > 6.5: return 1e10
        return -calc_str_w(H, B, b)
    return minimize_scalar(obj, bounds=(12.0, 23.4), method='bounded').x

# ==========================================
# CONSTRAINTS & TRANSFORMS
# ==========================================
def check_3d(b, r, delta_H):
    H_phys = find_H_opt(b)
    H = H_phys + delta_H
    h = (TOTAL_HEIGHT - H) / 2.0
    if not (12.0 <= H <= 23.4 and 0 <= h <= 6.5): return False
    if not (MIN_WEB_THICKNESS <= b <= MAX_WEB_RATIO*B_FIXED): return False
    return 0 <= r <= (B_FIXED - b)/2.0

def enforce_3d(params):
    b, r, delta_H = params
    b = np.clip(b, BOUNDS_3D['b'][0], min(MAX_WEB_RATIO*B_FIXED, BOUNDS_3D['b'][1]))
    r = np.clip(r, 0, min((B_FIXED-b)/2.0, BOUNDS_3D['r'][1]))
    H_phys = find_H_opt(b)
    delta_H = np.clip(delta_H, BOUNDS_3D['delta_H'][0], BOUNDS_3D['delta_H'][1])
    H = np.clip(H_phys + delta_H, 12.0, 23.4)
    delta_H = H - H_phys
    h = (TOTAL_HEIGHT - H) / 2.0
    return np.array([b, r, delta_H]), H, h

def transform_4d_to_3d(X_4d):
    X_3d = []
    for i in range(len(X_4d)):
        b, r = X_4d[i, 2], X_4d[i, 3]
        H_phys = find_H_opt(b)
        delta_H = X_4d[i, 0] - H_phys
        X_3d.append([b, r, delta_H])
    return np.array(X_3d)

def normalize(X):
    X_n = np.copy(X).astype(float)
    for i, k in enumerate(['b', 'r', 'delta_H']):
        X_n[:, i] = (X[:, i] - BOUNDS_3D[k][0]) / (BOUNDS_3D[k][1] - BOUNDS_3D[k][0])
    return X_n

def denormalize(X_n):
    X = np.copy(X_n)
    for i, k in enumerate(['b', 'r', 'delta_H']):
        X[:, i] = X_n[:, i] * (BOUNDS_3D[k][1] - BOUNDS_3D[k][0]) + BOUNDS_3D[k][0]
    return X

# ==========================================
# GP TRAINING WITH CONFIGURABLE PARAMETERS
# ==========================================
def train_gp(X_3d, y):
    X_norm = normalize(X_3d)
    y_log = np.log(y)
    y_mean, y_cent = np.mean(y_log), y_log - np.mean(y_log)

    # Configure kernel based on LENGTH_SCALE_MODE
    if LENGTH_SCALE_MODE == 'fixed':
        kernel = ConstantKernel(1.0, (0.1, 10.0)) * Matern(
            length_scale=FIXED_LENGTH_SCALES, length_scale_bounds='fixed', nu=2.5)
        print(f"  Using FIXED length scales: {FIXED_LENGTH_SCALES}")
    elif LENGTH_SCALE_MODE == 'constrained':
        kernel = ConstantKernel(1.0, (0.1, 10.0)) * Matern(
            length_scale=[0.5]*3, length_scale_bounds=LENGTH_SCALE_BOUNDS, nu=2.5)
        print(f"  Using CONSTRAINED length scale bounds: {LENGTH_SCALE_BOUNDS}")
    else:  # 'free'
        kernel = ConstantKernel(1.0, (0.1, 10.0)) * Matern(
            length_scale=[0.5]*3, length_scale_bounds=(0.1, 3.0), nu=2.5)
        print(f"  Using FREE ARD length scales (will learn per dimension)")

    gp = GaussianProcessRegressor(
        kernel=kernel, 
        n_restarts_optimizer=25,
        alpha=NOISE_LEVEL,  # Configurable noise
        normalize_y=False
    )
    gp.fit(X_norm, y_cent)
    
    # Report learned parameters
    if LENGTH_SCALE_MODE != 'fixed':
        scales = gp.kernel_.k2.length_scale
        print(f"  Learned length scales: b={scales[0]:.3f}, r={scales[1]:.3f}, dH={scales[2]:.3f}")
    
    return gp, X_norm, y_cent, y_mean

# ==========================================
# ACQUISITION FUNCTIONS
# ==========================================
def get_acq_params(dial):
    """Generate acquisition parameters from explore/exploit dial"""
    xi_mod = 0.0001 + dial * 0.0199
    kappa_mod = 0.2 + dial * 1.8
    return {
        'EI': {'moderate': xi_mod, 'exploit': 0.0001, 'explore': 0.02},
        'UCB': {'moderate': kappa_mod, 'exploit': 0.2, 'explore': 2.0}
    }

def ei_acq(gp, X_norm, y_best, xi):
    mu, sigma = gp.predict(X_norm, return_std=True)
    sigma = np.maximum(sigma, 1e-9)
    imp = mu - y_best - xi
    Z = imp / sigma
    return imp * norm.cdf(Z) + sigma * norm.pdf(Z), mu, sigma

def ucb_acq(gp, X_norm, kappa):
    mu, sigma = gp.predict(X_norm, return_std=True)
    return mu + kappa * np.maximum(sigma, 1e-9), mu, sigma

def optimize_acq(gp, acq_fn, acq_params, n_cand=4000):
    valid_cand, valid_norm = [], []
    attempts = 0
    while len(valid_cand) < n_cand and attempts < 5000:
        attempts += 1
        b = np.random.uniform(*BOUNDS_3D['b'])
        r = np.random.uniform(0, min((B_FIXED-b)/2.0, BOUNDS_3D['r'][1]))
        dH = np.random.uniform(*BOUNDS_3D['delta_H'])
        if check_3d(b, r, dH):
            cand = np.array([b, r, dH])
            valid_cand.append(cand)
            valid_norm.append(normalize(cand.reshape(1, -1))[0])

    if not valid_cand: raise ValueError("No valid candidates!")
    valid_norm = np.array(valid_norm)
    acq_vals, mu_vals, sig_vals = acq_fn(gp, valid_norm, **acq_params)
    idx = np.argmax(acq_vals)
    return valid_cand[idx], acq_vals[idx], mu_vals[idx], sig_vals[idx]

# ==========================================
# RECOMMENDATION GENERATOR
# ==========================================
def generate_recommendations(gp, y_cent, y_mean, X_train_3d, y_train):
    """Generate recommendations based on configuration"""
    np.random.seed(100)
    
    ACQ_CONFIG = get_acq_params(EXPLORE_EXPLOIT_DIAL)
    
    print(f"\n{'='*70}")
    print(f"GENERATING {N_RECOMMENDATIONS} RECOMMENDATIONS")
    print(f"Acquisition: {ACQ_FUNCTION}, Mode: {FANTASY_MODE}")
    if ACQ_FUNCTION == 'EI':
        param_val = ACQ_CONFIG['EI']['moderate']
        print(f"EI parameter ξ = {param_val:.4f} (dial={EXPLORE_EXPLOIT_DIAL:.2f})")
    else:
        param_val = ACQ_CONFIG['UCB']['moderate']
        print(f"UCB parameter κ = {param_val:.4f} (dial={EXPLORE_EXPLOIT_DIAL:.2f})")
    print(f"{'='*70}")
    
    recs = []
    
    # Initialize for sequential updates
    current_gp = gp
    current_X = X_train_3d.copy()
    current_y = y_train.copy()
    current_y_mean = y_mean
    current_y_cent = y_cent.copy()
    
    for i in range(N_RECOMMENDATIONS):
        # Select acquisition function and parameters
        if ACQ_FUNCTION == 'EI':
            y_best = current_y_cent.max()
            xi = param_val
            x, acq_val, mu, sig = optimize_acq(current_gp, ei_acq, 
                                              {'y_best': y_best, 'xi': xi})
            param_str = f'ξ={xi:.4f}'
        else:  # UCB
            kappa = param_val
            x, acq_val, mu, sig = optimize_acq(current_gp, ucb_acq, 
                                              {'kappa': kappa})
            param_str = f'κ={kappa:.4f}'
        
        x, H, h = enforce_3d(x)
        pred = np.exp(mu + current_y_mean)
        
        recs.append({
            'Beam': i+1, 
            'Method': ACQ_FUNCTION, 
            'Param': param_str,
            'H': H, 'B': B_FIXED, 'b': x[0], 'r': x[1], 'h': h, 'dH': x[2],
            'Pred': pred, 'Var': sig, 'AcqVal': acq_val
        })
        
        print(f"  Beam {i+1}: b={x[0]:.2f}mm, r={x[1]:.2f}mm, ΔH={x[2]:.2f}mm "
              f"→ Pred={pred:.2f}, σ={sig:.3f}, Acq={acq_val:.4f}")
        
        # Update GP for next iteration (if sequential)
        if FANTASY_MODE == 'sequential' and i < N_RECOMMENDATIONS - 1:
            current_X = np.vstack([current_X, [x[0], x[1], x[2]]])
            current_y = np.append(current_y, pred)
            current_gp, _, current_y_cent, current_y_mean = train_gp(current_X, current_y)
            print(f"    → GP updated with fantasy observation")
        elif FANTASY_MODE == 'none' and i == 0:
            print(f"    → No fantasy updates (single recommendation only)")
            break
    
    return pd.DataFrame(recs)

# ==========================================
# DATA LOADING WITH SELECTION
# ==========================================
def load_and_select_data():
    """Load data from GitHub and apply DATA_MODE selection"""
    import urllib.request
    import io

    DATA_URL = "https://raw.githubusercontent.com/andrewvoss8-boop/core-me-data-science-activities-public/main/data/I_beam_data.csv"

    print(f"📥 Downloading data from GitHub...")
    with urllib.request.urlopen(DATA_URL) as response:
        csv_data = response.read().decode('utf-8')

    df = pd.read_csv(io.StringIO(csv_data))
    print(f"✓ Loaded {len(df)} total beams from GitHub")

    # Clean and filter
    param_names_4d = ['H_web_height', 'B_flange_width', 'b_web_thick', 'r_fillet']
    required_cols = param_names_4d + ['Str/w (N/g)']
    df_clean = df[required_cols].dropna()

    def meets_constraints(row):
        H = row['H_web_height']
        B = row['B_flange_width']
        b = row['b_web_thick']
        r = row['r_fillet']
        h = (TOTAL_HEIGHT - H) / 2.0
        if B < MIN_FLANGE_WIDTH or b < MIN_WEB_THICKNESS or b > MAX_WEB_RATIO * B:
            return False
        if r < 0 or r > (B - b) / 2.0:
            return False
        if h < 0 or h > 6.5:
            return False
        return True

    df_constrained = df_clean[df_clean.apply(meets_constraints, axis=1)].copy()
    
    # Apply DATA_MODE selection
    print(f"\n📊 Data Selection Mode: {DATA_MODE}")
    if DATA_MODE == 'lhs_only':
        df_selected = df_constrained.iloc[:15].copy()
        print(f"  Using first 15 beams (LHS initial samples)")
    elif DATA_MODE == 'custom_range':
        start, end = CUSTOM_DATA_RANGE
        df_selected = df_constrained.iloc[start:end].copy()
        print(f"  Using beams [{start}:{end}] = {len(df_selected)} beams")
    elif DATA_MODE == 'top_performers':
        df_selected = df_constrained.nlargest(TOP_N_PERFORMERS, 'Str/w (N/g)').copy()
        print(f"  Using top {TOP_N_PERFORMERS} performing beams")
    else:  # 'all'
        df_selected = df_constrained.copy()
        print(f"  Using all {len(df_selected)} valid beams")
    
    print(f"  Str/w range: [{df_selected['Str/w (N/g)'].min():.2f}, "
          f"{df_selected['Str/w (N/g)'].max():.2f}] N/g")
    
    return df_selected

# ==========================================
# PLOTTING FUNCTIONS (keeping existing protocols)
# ==========================================
def get_point_sizes(X_norm, slice_point_norm, max_distance=0.5):
    distances = np.linalg.norm(X_norm - slice_point_norm, axis=1)
    sizes = np.zeros_like(distances)
    colors = np.zeros_like(distances)

    bucket1 = distances < 0.15
    bucket2 = (distances >= 0.15) & (distances < 0.30)
    bucket3 = (distances >= 0.30) & (distances < 0.50)
    bucket4 = (distances >= 0.50) & (distances < 0.75)
    bucket5 = distances >= 0.75

    sizes[bucket1] = 250
    sizes[bucket2] = 180
    sizes[bucket3] = 120
    sizes[bucket4] = 70
    sizes[bucket5] = 30

    colors[bucket1] = 0.9
    colors[bucket2] = 0.7
    colors[bucket3] = 0.5
    colors[bucket4] = 0.3
    colors[bucket5] = 0.1

    return sizes, distances, colors

def plot_1d_marginal(gp, X_norm, y, y_mean, recommendations):
    """Plot 1D marginal effects by averaging over random samples"""
    if not PLOT_1D_MARGINAL:
        return
        
    print("\nPlotting 1D marginal effects (averaged across design space)...")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f'I-Beam Design: Marginal Effects\n' +
                 f'Data: {DATA_MODE}, Noise: {NOISE_LEVEL:.0e}, {ACQ_FUNCTION} (dial={EXPLORE_EXPLOIT_DIAL:.2f})',
                 fontsize=14, weight='bold')

    for dim in range(3):
        ax = axes[dim]
        x_vals_norm = np.linspace(0, 1, 100)

        mu_samples_all = []
        sig_samples_all = []

        for x_val in x_vals_norm:
            X_samples = np.random.rand(MARGINAL_SAMPLES, 3)
            X_samples[:, dim] = x_val

            valid_samples = []
            for sample in X_samples:
                b, r, dH = denormalize(sample.reshape(1, -1))[0]
                if check_3d(b, r, dH):
                    valid_samples.append(sample)

            if len(valid_samples) > 0:
                valid_samples = np.array(valid_samples)
                mu, sig = gp.predict(valid_samples, return_std=True)
                mu_samples_all.append(mu)
                sig_samples_all.append(sig)
            else:
                mu_samples_all.append(np.array([np.nan]))
                sig_samples_all.append(np.array([np.nan]))

        mu_avg = np.array([np.nanmean(m) for m in mu_samples_all])
        mu_std = np.array([np.nanstd(m) for m in mu_samples_all])
        sig_avg = np.array([np.nanmean(s) for s in sig_samples_all])

        mu_r = np.exp(mu_avg + y_mean)
        epistemic_std = np.exp(mu_avg + y_mean) * sig_avg
        aleatory_std = np.exp(mu_avg + y_mean) * np.sqrt(NOISE_LEVEL)
        total_std = np.sqrt(epistemic_std**2 + aleatory_std**2)

        keys = list(BOUNDS_3D.keys())
        x_vals = x_vals_norm * (BOUNDS_3D[keys[dim]][1] - BOUNDS_3D[keys[dim]][0]) + BOUNDS_3D[keys[dim]][0]

        ax.plot(x_vals, mu_r, 'b-', lw=2, label='Marginal mean')
        ax.fill_between(x_vals, mu_r - 2*total_std, mu_r + 2*total_std,
                        alpha=0.25, color='orange', label='±2σ aleatory')
        ax.fill_between(x_vals, mu_r - 2*epistemic_std, mu_r + 2*epistemic_std,
                        alpha=0.3, color='blue', label='±2σ epistemic')

        X_den = denormalize(X_norm)
        ax.scatter(X_den[:, dim], y, c='red', s=50, alpha=0.6, ec='black', lw=1,
                  label='Data', zorder=5)

        if recommendations is not None:
            rec_3d = recommendations[['b','r','dH']].values
            ax.scatter(rec_3d[:, dim], recommendations['Pred'], c='lime', s=150, marker='*',
                      ec='black', lw=1.5, label='Recommended', zorder=10)

        if dim == 2:
            ax.axvline(0, color='green', ls='--', alpha=0.5, lw=2, label='Physics opt')

        ax.set_xlabel(PARAM_NAMES_3D[dim], fontsize=11)
        ax.set_ylabel('Str/w (N/g)', fontsize=11)
        ax.set_title(PARAM_NAMES_3D[dim], fontsize=12, weight='bold')
        ax.legend(fontsize=8, loc='best')
        ax.grid(alpha=0.3)

    plt.tight_layout()
    filename = f'teaching_1d_marginal_{DATA_MODE}_noise{NOISE_LEVEL:.0e}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: {filename}")
    plt.show()

def plot_2d_marginal(gp, X_norm, y, y_mean, recommendations):
    """Plot 2D marginal contours"""
    if not PLOT_2D_MARGINAL:
        return
        
    print("\nPlotting 2D marginal contours...")

    combos = [(0,1,'b_web','r_fillet',2), (0,2,'b_web','ΔH',1), (1,2,'r_fillet','ΔH',0)]

    for d1, d2, n1, n2, d_fixed in combos:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'I-Beam: Marginal {n1} vs {n2}\n' +
                     f'Data: {DATA_MODE}, Noise: {NOISE_LEVEL:.0e}, {ACQ_FUNCTION}',
                     fontsize=14, weight='bold')

        res = 40
        grid_x = np.linspace(0, 1, res)
        grid_y = np.linspace(0, 1, res)

        mu_grid = np.zeros((res, res))
        sig_grid = np.zeros((res, res))

        for i, x_val in enumerate(grid_x):
            for j, y_val in enumerate(grid_y):
                X_samples = np.random.rand(MARGINAL_SAMPLES, 3)
                X_samples[:, d1] = x_val
                X_samples[:, d2] = y_val

                valid_samples = []
                for sample in X_samples:
                    b, r, dH = denormalize(sample.reshape(1, -1))[0]
                    if check_3d(b, r, dH):
                        valid_samples.append(sample)

                if len(valid_samples) > 0:
                    valid_samples = np.array(valid_samples)
                    mu, sig = gp.predict(valid_samples, return_std=True)
                    mu_grid[j, i] = np.mean(mu)
                    sig_grid[j, i] = np.mean(sig)
                else:
                    mu_grid[j, i] = np.nan
                    sig_grid[j, i] = np.nan

        mu_r = np.exp(mu_grid + y_mean)
        sig_r = sig_grid

        keys = list(BOUNDS_3D.keys())
        x_vals = grid_x * (BOUNDS_3D[keys[d1]][1] - BOUNDS_3D[keys[d1]][0]) + BOUNDS_3D[keys[d1]][0]
        y_vals = grid_y * (BOUNDS_3D[keys[d2]][1] - BOUNDS_3D[keys[d2]][0]) + BOUNDS_3D[keys[d2]][0]
        ext = [x_vals[0], x_vals[-1], y_vals[0], y_vals[-1]]

        # Mean
        im1 = axes[0].imshow(mu_r, origin='lower', extent=ext, aspect='auto', cmap='viridis')
        axes[0].contour(mu_r, origin='lower', extent=ext, colors='white', alpha=0.4, levels=10)
        axes[0].set_xlabel(n1+' (mm)', fontsize=12)
        axes[0].set_ylabel(n2+' (mm)', fontsize=12)
        axes[0].set_title('Marginal Mean', fontsize=13, weight='bold')

        X_den = denormalize(X_norm)
        axes[0].scatter(X_den[:, d1], X_den[:, d2], c='red', s=80, ec='white', lw=2,
                       label='Data', zorder=10)

        if recommendations is not None:
            rec_3d = recommendations[['b','r','dH']].values
            axes[0].scatter(rec_3d[:, d1], rec_3d[:, d2], c='lime', s=150, marker='*',
                          ec='black', lw=1.5, label='Recommended', zorder=11)

        if d2 == 2: axes[0].axhline(0, color='green', ls='--', alpha=0.7, lw=2)
        if d1 == 2: axes[0].axvline(0, color='green', ls='--', alpha=0.7, lw=2)
        axes[0].legend(fontsize=9)
        plt.colorbar(im1, ax=axes[0], label='Str/w (N/g)')

        # Uncertainty
        im2 = axes[1].imshow(sig_r, origin='lower', extent=ext, aspect='auto', cmap='hot')
        axes[1].contour(sig_r, origin='lower', extent=ext, colors='white', alpha=0.4, levels=10)
        axes[1].set_xlabel(n1+' (mm)', fontsize=12)
        axes[1].set_ylabel(n2+' (mm)', fontsize=12)
        axes[1].set_title('Marginal Uncertainty (σ)', fontsize=13, weight='bold')
        axes[1].scatter(X_den[:, d1], X_den[:, d2], c='cyan', s=80, ec='white', lw=2, zorder=10)

        if recommendations is not None:
            rec_3d = recommendations[['b','r','dH']].values
            axes[1].scatter(rec_3d[:, d1], rec_3d[:, d2], c='lime', s=150, marker='*',
                          ec='black', lw=1.5, zorder=11)

        if d2 == 2: axes[1].axhline(0, color='green', ls='--', alpha=0.7, lw=2)
        if d1 == 2: axes[1].axvline(0, color='green', ls='--', alpha=0.7, lw=2)
        plt.colorbar(im2, ax=axes[1], label='Std Dev (σ)')

        plt.tight_layout()
        filename = f'teaching_2d_marginal_{n1}_{n2}_{DATA_MODE}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.show()

def plot_1d_global(gp, X_norm, y, y_mean, recommendations):
    """Plot 1D slices at mean values"""
    if not PLOT_1D_GLOBAL:
        return
        
    print("\nPlotting 1D global slices...")
    slice_pt = np.mean(X_norm, axis=0)
    slice_real = denormalize(slice_pt.reshape(1, -1))[0]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f'I-Beam: Global 1D Slices at Mean\n' +
                 f'Fixed: b={slice_real[0]:.2f}, r={slice_real[1]:.2f}, ΔH={slice_real[2]:.2f}',
                 fontsize=14, weight='bold')

    for dim in range(3):
        ax = axes[dim]
        X_test = np.tile(slice_pt, (100, 1))
        X_test[:, dim] = np.linspace(0, 1, 100)

        mu, sig = gp.predict(X_test, return_std=True)
        mu_r = np.exp(mu + y_mean)
        epistemic_std = np.exp(mu + y_mean) * sig
        aleatory_std = np.exp(mu + y_mean) * np.sqrt(NOISE_LEVEL)
        total_std = np.sqrt(epistemic_std**2 + aleatory_std**2)

        x_vals = denormalize(X_test)[:, dim]

        ax.plot(x_vals, mu_r, 'b-', lw=2, label='Mean prediction')
        ax.fill_between(x_vals, mu_r - 2*total_std, mu_r + 2*total_std,
                        alpha=0.25, color='orange', label='±2σ aleatory')
        ax.fill_between(x_vals, mu_r - 2*epistemic_std, mu_r + 2*epistemic_std,
                        alpha=0.3, color='blue', label='±2σ epistemic')

        X_den = denormalize(X_norm)
        ax.scatter(X_den[:, dim], y, c='red', s=50, alpha=0.6, ec='black', lw=1,
                  label='Data', zorder=5)

        if recommendations is not None:
            rec_3d = recommendations[['b','r','dH']].values
            ax.scatter(rec_3d[:, dim], recommendations['Pred'], c='lime', s=150, marker='*',
                      ec='black', lw=1.5, label='Recommended', zorder=10)

        if dim == 2:
            ax.axvline(0, color='green', ls='--', alpha=0.5, lw=2, label='Physics opt')

        ax.set_xlabel(PARAM_NAMES_3D[dim], fontsize=11)
        ax.set_ylabel('Str/w (N/g)', fontsize=11)
        ax.set_title(PARAM_NAMES_3D[dim], fontsize=12, weight='bold')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    filename = f'teaching_1d_global_{DATA_MODE}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.show()

def plot_2d_global(gp, X_norm, y, y_mean, recommendations):
    """Plot 2D contours at mean values"""
    if not PLOT_2D_GLOBAL:
        return
        
    print("\nPlotting 2D global contours...")
    slice_pt = np.mean(X_norm, axis=0)
    slice_real = denormalize(slice_pt.reshape(1, -1))[0]

    combos = [(0,1,'b_web','r_fillet',2), (0,2,'b_web','ΔH',1), (1,2,'r_fillet','ΔH',0)]

    for d1, d2, n1, n2, d_fixed in combos:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'I-Beam: {n1} vs {n2} at Mean\n' +
                     f'Fixed: {PARAM_NAMES_3D[d_fixed]}={slice_real[d_fixed]:.2f}mm',
                     fontsize=14, weight='bold')

        grid_x, grid_y = np.meshgrid(np.linspace(0, 1, 50), np.linspace(0, 1, 50))
        X_test = np.tile(slice_pt, (2500, 1))
        X_test[:, d1], X_test[:, d2] = grid_x.ravel(), grid_y.ravel()

        mu, sig = gp.predict(X_test, return_std=True)
        mu_r = np.exp(mu + y_mean).reshape(50, 50)
        sig_r = sig.reshape(50, 50)

        keys = list(BOUNDS_3D.keys())
        x_v = np.linspace(0, 1, 50) * (BOUNDS_3D[keys[d1]][1] - BOUNDS_3D[keys[d1]][0]) + BOUNDS_3D[keys[d1]][0]
        y_v = np.linspace(0, 1, 50) * (BOUNDS_3D[keys[d2]][1] - BOUNDS_3D[keys[d2]][0]) + BOUNDS_3D[keys[d2]][0]
        ext = [x_v[0], x_v[-1], y_v[0], y_v[-1]]

        # Mean
        im1 = axes[0].imshow(mu_r, origin='lower', extent=ext, aspect='auto', cmap='viridis')
        axes[0].contour(mu_r, origin='lower', extent=ext, colors='white', alpha=0.4, levels=10)
        axes[0].set_xlabel(n1+' (mm)', fontsize=12)
        axes[0].set_ylabel(n2+' (mm)', fontsize=12)
        axes[0].set_title('Mean Prediction', fontsize=13, weight='bold')

        X_den = denormalize(X_norm)
        axes[0].scatter(X_den[:, d1], X_den[:, d2], c='red', s=80, ec='white', lw=2,
                       label='Data', zorder=10)

        if recommendations is not None:
            rec_3d = recommendations[['b','r','dH']].values
            axes[0].scatter(rec_3d[:, d1], rec_3d[:, d2], c='lime', s=150, marker='*',
                          ec='black', lw=1.5, label='Recommended', zorder=11)

        if d2 == 2: axes[0].axhline(0, color='green', ls='--', alpha=0.7, lw=2)
        if d1 == 2: axes[0].axvline(0, color='green', ls='--', alpha=0.7, lw=2)
        axes[0].legend(fontsize=9)
        plt.colorbar(im1, ax=axes[0], label='Str/w (N/g)')

        # Uncertainty
        im2 = axes[1].imshow(sig_r, origin='lower', extent=ext, aspect='auto', cmap='hot')
        axes[1].contour(sig_r, origin='lower', extent=ext, colors='white', alpha=0.4, levels=10)
        axes[1].set_xlabel(n1+' (mm)', fontsize=12)
        axes[1].set_ylabel(n2+' (mm)', fontsize=12)
        axes[1].set_title('Uncertainty (σ)', fontsize=13, weight='bold')
        axes[1].scatter(X_den[:, d1], X_den[:, d2], c='cyan', s=80, ec='white', lw=2, zorder=10)

        if recommendations is not None:
            rec_3d = recommendations[['b','r','dH']].values
            axes[1].scatter(rec_3d[:, d1], rec_3d[:, d2], c='lime', s=150, marker='*',
                          ec='black', lw=1.5, zorder=11)

        if d2 == 2: axes[1].axhline(0, color='green', ls='--', alpha=0.7, lw=2)
        if d1 == 2: axes[1].axvline(0, color='green', ls='--', alpha=0.7, lw=2)
        plt.colorbar(im2, ax=axes[1], label='Std Dev (σ)')

        plt.tight_layout()
        filename = f'teaching_2d_global_{n1}_{n2}_{DATA_MODE}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.show()

def plot_slice_1d(gp, X_norm, y, y_mean, slice_point_norm, slice_name, slice_idx):
    """Plot 1D slices at specific point"""
    slice_real = denormalize(slice_point_norm.reshape(1, -1))[0]
    point_sizes, point_distances, point_colors = get_point_sizes(X_norm, slice_point_norm)
    on_slice = point_distances < 0.1

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f'Slice {slice_idx}: {slice_name}\n' +
                 f'(b={slice_real[0]:.2f}, r={slice_real[1]:.2f}, ΔH={slice_real[2]:.2f})',
                 fontsize=14, weight='bold')

    for dim in range(3):
        ax = axes[dim]
        X_test = np.tile(slice_point_norm, (100, 1))
        X_test[:, dim] = np.linspace(0, 1, 100)

        mu, sig = gp.predict(X_test, return_std=True)
        mu_r = np.exp(mu + y_mean)
        epistemic_std = np.exp(mu + y_mean) * sig
        aleatory_std = np.exp(mu + y_mean) * np.sqrt(NOISE_LEVEL)
        total_std = np.sqrt(epistemic_std**2 + aleatory_std**2)

        x_vals = denormalize(X_test)[:, dim]

        ax.plot(x_vals, mu_r, 'b-', lw=2, label='Mean')
        ax.fill_between(x_vals, mu_r - 2*total_std, mu_r + 2*total_std,
                        alpha=0.25, color='orange', label='±2σ aleatory')
        ax.fill_between(x_vals, mu_r - 2*epistemic_std, mu_r + 2*epistemic_std,
                        alpha=0.3, color='blue', label='±2σ epistemic')

        X_den = denormalize(X_norm)
        ax.scatter(X_den[:, dim], y, s=point_sizes, c=point_colors, cmap='Reds',
                  vmin=0, vmax=1, alpha=0.6, ec='black', lw=0.5, zorder=5,
                  label='Data (sized by distance)')

        if np.any(on_slice):
            ax.scatter(X_den[on_slice, dim], y[on_slice], s=400, marker='*',
                      c='yellow', ec='black', lw=2, zorder=10, label='On slice')

        if dim == 2:
            ax.axvline(0, color='green', ls='--', alpha=0.5, lw=2, label='Physics opt')

        ax.set_xlabel(PARAM_NAMES_3D[dim], fontsize=11)
        ax.set_ylabel('Str/w (N/g)', fontsize=11)
        ax.set_title(PARAM_NAMES_3D[dim], fontsize=12, weight='bold')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    clean_name = slice_name.replace('#', 'num').replace('(', '').replace(')', '').replace('=', '').replace(':', '').replace('/', '_').replace(' ', '_')
    filename = f'teaching_slice_{slice_idx:02d}_{clean_name}_1d.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.show()

def plot_slice_2d(gp, X_norm, y, y_mean, slice_point_norm, slice_name, slice_idx):
    """Plot 2D contours at specific point"""
    slice_real = denormalize(slice_point_norm.reshape(1, -1))[0]
    point_sizes, point_distances, point_colors = get_point_sizes(X_norm, slice_point_norm)
    on_slice = point_distances < 0.1

    combos = [(0,1,'b_web','r_fillet',2), (0,2,'b_web','ΔH',1), (1,2,'r_fillet','ΔH',0)]

    for d1, d2, n1, n2, d_fixed in combos:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'Slice {slice_idx}: {slice_name} - {n1} vs {n2}\n' +
                     f'(Fixed: {PARAM_NAMES_3D[d_fixed]}={slice_real[d_fixed]:.2f}mm)',
                     fontsize=14, weight='bold')

        grid_x, grid_y = np.meshgrid(np.linspace(0, 1, 50), np.linspace(0, 1, 50))
        X_test = np.tile(slice_point_norm, (2500, 1))
        X_test[:, d1], X_test[:, d2] = grid_x.ravel(), grid_y.ravel()

        mu, sig = gp.predict(X_test, return_std=True)
        mu_r = np.exp(mu + y_mean).reshape(50, 50)
        sig_r = sig.reshape(50, 50)

        keys = list(BOUNDS_3D.keys())
        x_v = np.linspace(0, 1, 50) * (BOUNDS_3D[keys[d1]][1] - BOUNDS_3D[keys[d1]][0]) + BOUNDS_3D[keys[d1]][0]
        y_v = np.linspace(0, 1, 50) * (BOUNDS_3D[keys[d2]][1] - BOUNDS_3D[keys[d2]][0]) + BOUNDS_3D[keys[d2]][0]
        ext = [x_v[0], x_v[-1], y_v[0], y_v[-1]]

        # Mean
        im1 = axes[0].imshow(mu_r, origin='lower', extent=ext, aspect='auto', cmap='viridis')
        axes[0].contour(mu_r, origin='lower', extent=ext, colors='white', alpha=0.4, levels=10)
        axes[0].set_xlabel(n1+' (mm)', fontsize=12)
        axes[0].set_ylabel(n2+' (mm)', fontsize=12)
        axes[0].set_title('Mean Prediction', fontsize=12, weight='bold')

        X_den = denormalize(X_norm)
        axes[0].scatter(X_den[:, d1], X_den[:, d2], s=point_sizes, c=point_colors,
                       cmap='Reds', vmin=0, vmax=1, alpha=0.6, ec='white', lw=1, zorder=5)

        if np.any(on_slice):
            axes[0].scatter(X_den[on_slice, d1], X_den[on_slice, d2], s=400, marker='*',
                           c='yellow', ec='black', lw=2, zorder=10, label='On slice')
            axes[0].legend()

        if d2 == 2: axes[0].axhline(0, color='green', ls='--', alpha=0.7, lw=2)
        if d1 == 2: axes[0].axvline(0, color='green', ls='--', alpha=0.7, lw=2)
        plt.colorbar(im1, ax=axes[0], label='Str/w (N/g)')

        # Uncertainty
        im2 = axes[1].imshow(sig_r, origin='lower', extent=ext, aspect='auto', cmap='hot')
        axes[1].contour(sig_r, origin='lower', extent=ext, colors='white', alpha=0.4, levels=10)
        axes[1].set_xlabel(n1+' (mm)', fontsize=12)
        axes[1].set_ylabel(n2+' (mm)', fontsize=12)
        axes[1].set_title('Uncertainty (σ)', fontsize=12, weight='bold')

        axes[1].scatter(X_den[:, d1], X_den[:, d2], s=point_sizes, c=point_colors,
                       cmap='Blues', vmin=0, vmax=1, alpha=0.6, ec='white', lw=1, zorder=5)

        if np.any(on_slice):
            axes[1].scatter(X_den[on_slice, d1], X_den[on_slice, d2], s=400, marker='*',
                           c='yellow', ec='black', lw=2, zorder=10, label='On slice')
            axes[1].legend()

        if d2 == 2: axes[1].axhline(0, color='green', ls='--', alpha=0.7, lw=2)
        if d1 == 2: axes[1].axvline(0, color='green', ls='--', alpha=0.7, lw=2)
        plt.colorbar(im2, ax=axes[1], label='Std Dev (σ)')

        plt.tight_layout()
        clean_name = slice_name.replace('#', 'num').replace('(', '').replace(')', '').replace('=', '').replace(':', '').replace('/', '_').replace(' ', '_')
        filename = f'teaching_slice_{slice_idx:02d}_{clean_name}_{n1}_{n2}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.show()

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("="*70)
    print("I-BEAM BAYESIAN OPTIMIZATION TEACHING TOOL")
    print("="*70)
    print(f"Configuration:")
    print(f"  Data Mode: {DATA_MODE}")
    print(f"  Noise Level: {NOISE_LEVEL:.0e}")
    print(f"  Length Scale Mode: {LENGTH_SCALE_MODE}")
    print(f"  Acquisition: {ACQ_FUNCTION}")
    print(f"  Explore/Exploit: {EXPLORE_EXPLOIT_DIAL:.2f}")
    print(f"  Recommendations: {N_RECOMMENDATIONS} ({FANTASY_MODE})")
    print("="*70)

    # Load and select data
    df = load_and_select_data()
    
    X_4d = df[['H_web_height', 'B_flange_width', 'b_web_thick', 'r_fillet']].values
    y = df['Str/w (N/g)'].values

    # Transform & train
    print("\nTransforming to 3D search space...")
    X_3d = transform_4d_to_3d(X_4d)
    
    print(f"\nTraining GP (noise={NOISE_LEVEL:.0e}, length_scale={LENGTH_SCALE_MODE})...")
    gp, X_norm, y_cent, y_mean = train_gp(X_3d, y)

    # Find best beam
    best_idx = np.argmax(y)
    print(f"\nCurrent best beam (index {best_idx}):")
    print(f"  b={X_3d[best_idx, 0]:.2f}mm, r={X_3d[best_idx, 1]:.2f}mm, " +
          f"ΔH={X_3d[best_idx, 2]:.2f}mm → Str/w={y[best_idx]:.2f} N/g")

    # Generate recommendations
    recommendations = generate_recommendations(gp, y_cent, y_mean, X_3d, y)
    print(f"\n{recommendations.to_string(index=False)}")
    
    filename = f'recommendations_{DATA_MODE}_{ACQ_FUNCTION}_dial{EXPLORE_EXPLOIT_DIAL:.2f}.csv'
    recommendations.to_csv(filename, index=False)
    print(f"\n✓ Saved recommendations to: {filename}")

    # Generate visualizations
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70)
    
    # Marginal plots
    plot_1d_marginal(gp, X_norm, y, y_mean, recommendations)
    plot_2d_marginal(gp, X_norm, y, y_mean, recommendations)
    
    # Global slice plots
    plot_1d_global(gp, X_norm, y, y_mean, recommendations)
    plot_2d_global(gp, X_norm, y, y_mean, recommendations)

    # Slice-specific plots
    if PLOT_SLICES:
        print("\n" + "="*70)
        print("GENERATING SLICE-SPECIFIC PLOTS")
        print("="*70)
        
        slices = []
        
        # Add selections based on SLICE_SELECTIONS
        for selection in SLICE_SELECTIONS:
            if selection == 'top_3':
                top3_indices = np.argsort(y)[-3:][::-1]
                for i, idx in enumerate(top3_indices):
                    slice_name = f"Top #{i+1} (Str/w={y[idx]:.2f} N/g)"
                    slices.append((X_3d[idx], slice_name))
                    
            elif selection == 'worst_3':
                worst3_indices = np.argsort(y)[:3]
                for i, idx in enumerate(worst3_indices):
                    slice_name = f"Worst #{i+1} (Str/w={y[idx]:.2f} N/g)"
                    slices.append((X_3d[idx], slice_name))
                    
            elif selection == 'recommendations':
                for i, row in recommendations.iterrows():
                    slice_name = f"Recommended Beam {row['Beam']} ({row['Method']})"
                    slices.append((np.array([row['b'], row['r'], row['dH']]), slice_name))
                    
            elif selection == 'random_5':
                np.random.seed(42)
                random_indices = np.random.choice(len(X_3d), min(5, len(X_3d)), replace=False)
                for i, idx in enumerate(random_indices):
                    slice_name = f"Random #{i+1}"
                    slices.append((X_3d[idx], slice_name))
                    
            elif selection == 'custom':
                for i, idx in enumerate(CUSTOM_SLICE_INDICES):
                    if idx < len(X_3d):
                        slice_name = f"Custom #{i+1} (index {idx})"
                        slices.append((X_3d[idx], slice_name))
        
        # Generate slice plots
        for idx, (slice_point_3d, slice_name) in enumerate(slices):
            slice_point_norm = normalize(slice_point_3d.reshape(1, -1))[0]
            print(f"\nProcessing slice {idx+1}/{len(slices)}: {slice_name}")
            plot_slice_1d(gp, X_norm, y, y_mean, slice_point_norm, slice_name, idx+1)
            plot_slice_2d(gp, X_norm, y, y_mean, slice_point_norm, slice_name, idx+1)

    print("\n" + "="*70)
    print("✓ COMPLETE!")
    print("="*70)
    print(f"\nConfiguration summary:")
    print(f"  Data: {DATA_MODE} ({len(y)} beams)")
    print(f"  Noise: {NOISE_LEVEL:.0e}")
    print(f"  Length scales: {LENGTH_SCALE_MODE}")
    print(f"  Acquisition: {ACQ_FUNCTION} (dial={EXPLORE_EXPLOIT_DIAL:.2f})")
    print(f"  Fantasy: {FANTASY_MODE}")
    print(f"  Recommendations: {N_RECOMMENDATIONS}")
    
    if PLOT_SLICES:
        print(f"  Slices: {len(slices)} locations")
    
    print("\nRecommended next beams to test:")
    for i, row in recommendations.iterrows():
        print(f"  {i+1}. H={row['H']:.2f}, B={row['B']:.2f}, b={row['b']:.2f}, "
              f"r={row['r']:.2f} → Predicted Str/w={row['Pred']:.2f} N/g")
    print("="*70)
