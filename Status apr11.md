# Status / lessons learned — Apr 11, 2026

Notes from the last ~48 hours of work on the ME323 2-variable beam GP / Bayes opt lab (repo: `core-me-data-science-activities-public`). Focus: what we learned for **student-facing project design**, not a full code changelog.

---

## Lessons learned

### Data and reproducibility

- **Load training data from GitHub raw URLs** when you want Colab / any machine to run without a local `../data/` tree. Pattern is in `beam_strength_comparison.ipynb` and related notebooks.
- **LHS subset for stress tests:** `data/lhs16_subset_bH_even_n13.csv` is 13 beams from LHS 1–16, **excluding beam 15** (Str/w ~31.9), chosen by farthest-point sampling in normalized `(b,H)`. Rows are **verbatim** from `I_beam_data_2var.csv`. Regenerate with `me323/build_lhs16_subset_even_bH.py` if the master CSV changes.

### Physics vs what the GP sees

- **Bending + elastic LTB alone miss web shear** for very thin webs. A simple **web shear yield** cap (`V_n ≈ (σ_y/√3)·b·H`, `P = 2V_n` for 3-point bend) tracks **beam 13** much better than `P_bend` / `P_ltb`; it still **overpredicts** test load (~11% high), which is consistent with **non-uniform τ**, **FDM interlayer shear**, and **stress concentrations**, not “tuned to fit.”
- **Elastic `M_cr` is not ultimate capacity**; fixture / post-buckling / inelastic behavior inflate real strength above the textbook line. **`k = P_actual / P_ltb` is not constant** across the dataset; **`J`** (and related geometry) correlates with **`k`** in exploratory stats. Teach: the scalar **`R`** is useful intuition but not a complete story for every failure mode.
- **Shear buckling** (isotropic plate-style estimate) was **not governing** for the beam we checked vs shear yield; still flag **slender webs** as a domain where buckling could enter.

### Ablation / methodology (v2 and v3)

- **Training subset dominates** many conclusions. Jackknife-style `sub12_*` splits in v2 showed **large** swings in scored recommendations. **Purdue pilot LHS (Option A in Status apr7)** matters if you want stable “default” knobs; **Option B** is OK if grading **reasoning** and you say explicitly: *your 12–16 points define the surface.*
- **Noise vs performance has no universal monotonic trend** in v2 when you pool kernels, acquisitions, and subsets. Pooled averages can show “more noise looks better” while slice **`all_16` + EI + Matern** is **U-shaped** in α. **Do not canonize one α** from McCallie; tie **`alpha` to repeat-beam calibration** on local data.
- **Repeat beams (same geometry, different color):** pooled log-Str/w noise suggests **α ~ 7×10⁻⁵ to ~10⁻⁴** as a ballpark for a **single global** GP on log Str/w. One pair **(3.5, 14.5)** is much noisier than the others (possible **mode / n=2** issue). **Heteroscedastic** `α(R)` is implemented in **`me323/heteroscedastic_noise.py`**; smoke test in **`heteroscedastic_test.py`**. On full data it **barely moves** marginal likelihood or LOO vs a decent constant α — treat as **optional teaching knob**, not a default for v1 simplicity.
- **EI vs UCB:** v2 pooled **`gt_strw`** favors **EI** over **UCB**. High **UCB κ** pushes candidates into **thin-web badlands** (easy classroom demo).
- **v3** (13-beam subset, **EI**, **α = 1e-4**, Matern + RBF):  
  - **Matern + `b_dH_Pltb_Pbend`** is the stand-out on **`n13_all`** (high **`gt_strw`**, often in strong zone, lower **`gt_var`**).  
  - **RBF** can win with **`(b,H)`** or **`Pltb_Pbend`** on the same data — **kernel choice interacts with parameterization**.  
  - **Dropping all `b < 2` training points and constraining BO to `b ≥ 2`** (`n10_b2`: only **10** beams remain; beams **7, 12, 13** out) **collapses** performance: Matern recommendations cluster near **`b ≈ 2`, `H ≈ 12`** and **miss** the strong region. **Thin-web contrast points are load-bearing for learning the surface**; do not sanitize them out of the training set for “safety.”

### Bounds consistency

- **Ablation notebooks** use a **fixed box** **`b ∈ [1, 8]` mm**, **`H ∈ [12, 23]` mm** (with inner **`find_H_opt`** sometimes using **`H` up to 23.4**).  
- **`beam_lab_student.ipynb`** uses **data-driven** bounds **`min/max ± 0.5`** per column.  
- Align messaging for students: **“design box” vs “plot bounds from data.”**

---

## Essential questions (for design and rubric)

1. **What is the canonical design box** for the course (fixed vs data-driven bounds), and do we align **ablation**, **student notebook**, and **print constraints**?
2. **Pilot data (Purdue):** Option A vs B — do we require a small LHS before semester, or explicitly grade **process** when transfer from McCallie/Purdue is unknown?
3. **Which failure modes must Phase 1 mention** (LTB, bending, web shear, bearing) so students do not trust a single scalar **`R`** or a single GP feature set?
4. **Kernel and acquisition:** Do students **choose** Matern vs RBF and EI vs UCB with a short **“why”**, or do we fix defaults and only vary noise / features?
5. **Heteroscedastic noise:** In or out of v1? If in, is it **extra credit** or a **guided cell** with clear “small effect on scores, large effect on reasoning” framing?
6. **Strong zone / GT scoring:** Are instructor-facing ablation metrics (`gt_strw`, `dist_to_strong`, `in_strong_zone`) ever shown to students, or kept for **baseline beam** selection only?
7. **LLM policy** (from apr7): still open — spreadsheets only, or full allow with rubric on reasoning?

---

## Next steps (project design)

1. **Lock the student data path:** GitHub raw URL + one **authoritative** CSV revision per term; document hash or release tag if needed.
2. **Decide v1 defaults** from v3 + v2: e.g. **Matern + EI + α from repeat calibration**; **rich physics features** as Phase 3 goal with **“wrong code hurts”** check vs plain `(b,H)`.
3. **Keep thin-web LHS points** in the training set; if the lab adds a **“no print below b_min”** rule, **still show** those designs in data or in a **counterfactual** plot so the surface is not misleading.
4. **One short instructor note** tying **beam_strength_comparison** insights to **CDR prompts** (why **`k`** varies, beam 13, web shear one-liner).
5. **Reconcile Status apr7** “McCallie winner” language with **v2/v3**: emphasize **local ablation** and **subset sensitivity** instead of a single global recipe.
6. **Optional:** add **`ablation_study_2var_v3.py`** (or a thin notebook wrapper) to the instructor path as the **minimal** sweep script for the 13-beam subset.

---

## Files touched or added (for traceability)

- `me323/beam_strength_comparison.ipynb` — `P_shear`, `P_triple`, beam 13 check; GitHub data URL.  
- `me323/heteroscedastic_noise.py`, `me323/heteroscedastic_test.py`  
- `data/lhs16_subset_bH_even_n13.csv`, `me323/build_lhs16_subset_even_bH.py`  
- `me323/ablation_study_2var_v3.py`, `me323/ablation_results_2var_v3.csv`  
- Prior thread work also referenced: `ablation_study_2var_v2.ipynb`, `ablation_results_2var_v2.csv`

This document is a **project design memo**, not a promise that every number above will replicate after CSV or sklearn version changes; re-run the named scripts and notebooks to verify.
