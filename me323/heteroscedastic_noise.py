"""
Optional heteroscedastic GP noise as a function of stability ratio R = Mcr/My.

This is a small, physics-motivated knob (noise peaks near R ~ 1). On the current
dataset it barely moves log-marginal-likelihood or LOO error vs a good constant
alpha; keep it out of the student path for simplicity unless you explicitly
want to teach input-dependent noise.

Use with sklearn GaussianProcessRegressor(..., alpha=alpha_array) where
alpha_array[i] = get_noise_variance(R_i) for each training point (target in
log Str/w space).

Calibration notes and repeat-beam motivation: see heteroscedastic_test.py.
"""

from __future__ import annotations

import numpy as np

E = 2.74e9
SIGMA_Y = 81.8e6
G = E / 2.6
L = 0.2023
C1 = 1.35
TOTAL_H = 25.0
B_F = 16.0
Y_MAX = TOTAL_H / 2e3

SIGMA_BASE = 0.003
SIGMA_PEAK = 0.005
WIDTH = 0.4


def _beta(t, a):
    if a <= 0 or t <= 0:
        return 1.0 / 3.0
    r = min(t, a) / max(t, a)
    return (1.0 / 3.0) * (1.0 - 0.63 * r + 0.052 * r**5)


def calc_R(b_mm: float, H_mm: float) -> float:
    """Stability ratio Mcr/My (same geometry convention as beam_strength_comparison)."""
    H, b, Bf = H_mm / 1e3, b_mm / 1e3, B_F / 1e3
    h = (TOTAL_H / 1e3 - H) / 2.0
    if h <= 0:
        return 0.0
    Ix = (b * H**3) / 12 + 2 * (Bf * h**3 / 12 + Bf * h * ((H + h) / 2) ** 2)
    Iy = (H * b**3) / 12 + 2 * (h * Bf**3) / 12
    J_web = _beta(min(b, H), max(b, H)) * max(b, H) * min(b, H) ** 3
    J_fl = _beta(min(h, Bf), max(h, Bf)) * max(h, Bf) * min(h, Bf) ** 3
    J = J_web + 2 * J_fl
    My = SIGMA_Y * Ix / Y_MAX
    Mcr = (C1 * np.pi / L) * np.sqrt(E * Iy * G * J)
    return float(Mcr / My) if My > 0 else 0.0


def get_noise_variance(R: float) -> float:
    """Variance of additive noise on log(Str/w) at stability ratio R."""
    log_R = np.log(max(float(R), 1e-6))
    bump = np.exp(-0.5 * (log_R / WIDTH) ** 2)
    return float((SIGMA_BASE + SIGMA_PEAK * bump) ** 2)


def alpha_array_for_beams(b_mm: np.ndarray, H_mm: np.ndarray) -> np.ndarray:
    """Per-row alpha for sklearn GPR when y is log(Str/w)."""
    R = np.array([calc_R(float(b), float(h)) for b, h in zip(b_mm, H_mm)])
    return np.array([get_noise_variance(r) for r in R])
