"""
Build a 13-row subset of LHS beams 1–16 from data/I_beam_data_2var.csv.

Rules (all rows are verbatim copies from the CSV):
  - Pool = numeric beams 1..16 only (first LHS block in the file).
  - Exclude beam 15 (Str/w ~ 31.90 N/g; user request).
  - From the remaining 15 rows, select 13 by farthest-point sampling in (b,H)
    normalized to [0,1] using the min/max of those 15 points (space-filling).

Output: data/lhs16_subset_bH_even_n13.csv (same columns as source).

Re-run this script after CSV edits to regenerate the subset.
"""

from __future__ import annotations

import csv
import pathlib

import numpy as np
import pandas as pd


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "data" / "I_beam_data_2var.csv"
OUT = REPO_ROOT / "data" / "lhs16_subset_bH_even_n13.csv"

EXCLUDE_BEAM = 15
N_SELECT = 13


def _lhs16_mask(df: pd.DataFrame) -> pd.Series:
    def is_lhs16(x):
        try:
            v = int(float(str(x).strip()))
            return 1 <= v <= 16
        except (ValueError, TypeError):
            return False

    return df["Beam Number"].map(is_lhs16)


def farthest_point_indices(X: np.ndarray, k: int) -> list[int]:
    """Return indices of k rows of X (n x d) maximizing spread (greedy FPS)."""
    n = X.shape[0]
    if k > n or k < 1:
        raise ValueError("k must be in 1..n")
    centroid = X.mean(axis=0)
    first = int(np.argmax(np.linalg.norm(X - centroid, axis=1)))
    selected = [first]
    dist_min = np.linalg.norm(X - X[first], axis=1)

    while len(selected) < k:
        dist_min = np.minimum(dist_min, np.linalg.norm(X - X[selected[-1]], axis=1))
        dist_min[selected] = -1.0
        nxt = int(np.argmax(dist_min))
        selected.append(nxt)
    return selected


def main():
    df = pd.read_csv(SRC)
    pool = df[_lhs16_mask(df)].copy()
    pool = pool[pool["Beam Number"].astype(int) != EXCLUDE_BEAM].copy()
    if len(pool) != 15:
        raise RuntimeError(f"expected 15 rows after excluding beam {EXCLUDE_BEAM}, got {len(pool)}")

    b = pool["b_web_mm"].astype(float).values
    H = pool["H_web_mm"].astype(float).values
    lo = np.array([b.min(), H.min()])
    hi = np.array([b.max(), H.max()])
    X = (np.column_stack([b, H]) - lo) / (hi - lo)

    idx = farthest_point_indices(X, N_SELECT)
    chosen = sorted(pool.iloc[idx]["Beam Number"].astype(int).tolist())
    chosen_set = set(chosen)

    omitted = sorted(
        int(x) for x in pool["Beam Number"].tolist() if int(x) not in chosen_set
    )

    # Copy exact text cells from source CSV (no pandas float coercion on integers).
    out_rows = []
    with SRC.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row:
                continue
            try:
                bi = int(float(row[0].strip()))
            except (ValueError, TypeError):
                continue
            if 1 <= bi <= 16 and bi != EXCLUDE_BEAM and bi in chosen_set:
                out_rows.append((bi, row))

    out_rows.sort(key=lambda t: t[0])
    if len(out_rows) != N_SELECT:
        raise RuntimeError(f"expected {N_SELECT} CSV rows, got {len(out_rows)}")

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for _, row in out_rows:
            w.writerow(row)

    print("Source:", SRC)
    print("Pool: LHS beams 1–16 excluding", EXCLUDE_BEAM, "→", len(pool), "rows")
    print("Selected", N_SELECT, "beams (sorted):", chosen)
    print("Omitted from pool:", omitted)
    print("Wrote:", OUT)


if __name__ == "__main__":
    main()
