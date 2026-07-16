# ME 323 Module 1 — Instructor Guide (DRAFT)
*Beam design under uncertainty: physics, machine learning, print, test, reflect.*

This is the master doc for the module. It holds the schedule, the learning objectives, the design of the two-query ground-truth step (the one piece with logistics to get right), and notes on each artifact. The other files in this folder are the two lecture decks, the four student notebooks (two pre-labs, two submissions), and the rubric.

**Slide formats.** Each lecture ships as both a Marp markdown source (`ME323_Lecture{1,2}_slides.md`) and a built PowerPoint (`ME323_Module1_Lecture{1,2}.pptx`, 16:9). The GIFs are embedded as native `image/gif`, so they animate in PowerPoint 365 / 2019 slideshow mode. Slide text is duplicated in `build_pptx.py`; edit both sources, then rebuild with `python3 build_pptx.py`.

**Module configuration.** Flange width 10 mm, total height 18 mm, test span 150 mm, printed length 172 mm (11 mm overhang past each support). Design space: web thickness `b` in [1.25, 7] mm, web height `H_web` in [5, 16] mm. The nominal-geometry mass estimate is `mass_est_g = 0.2045 A`; the handout also retains `weight_g`, the measured printed-beam mass. Those columns should differ. Strength-to-weight models and pre-print optimizations use estimated mass so every candidate has a denominator before it is printed. The staff oracle provenance contains 63 tests: the initial 44-beam campaign plus 19 follow-up tests.

**What students see.** The notebooks load the frozen 14-beam `student_beams_B10_L150.csv` handout. Students do not get the full oracle dataset. The two common query results extend their table to 15 and then 16 beams. Changing the subset changes every GP checkpoint and requires a full regeneration.

---

## The idea in one paragraph

Students design a 3D-printed I-beam for strength-to-weight. The catch is that the physics is incomplete: printed beams can fracture along the layer lines at loads no equation flags, lateral-torsional buckling depends on fixture assumptions, and the failure modes overlap. So the equations cannot hand them the answer. They build a physics model, see where it strains against real data, then bring in a Gaussian Process and Bayesian optimization to design under uncertainty with very few tests. They print, test, and reflect. The point is engineering judgment under uncertainty, not ML theory.

---

## Schedule

| # | Piece | Format | Out of class? |
|---|---|---|---|
| 1 | **Lecture 1** — framing + failure modes and models | ~50 min | in class |
| 2 | **Pre-lab 1** — process data, fit failure modes, optimize str/w | notebook | homework |
| 3 | **Lecture 2** — the ML sequence, built up from ME 239 | ~50 min | in class |
| 4 | **Pre-lab 2** — GP and Bayesian optimization in this context | notebook | homework |
| 5 | **Two-query test** — synthetically test the equation design and the vanilla-GP design against the ground-truth model | in notebook | in lab |
| 6 | **Design + Submission 1** — pick a beam from physics + ML + the 2 new points; turn in design, rationale, notebooks; this beam gets printed and tested | notebook + memo | submission |
| 7 | **Print + test** | ~3 weeks | staff/UG |
| 8 | **Reflect + Submission 2** — recall, reflect on the test result, then the lightweight-bending challenge: lightest beam that confidently holds `P_TARGET` N (not tested; rationale graded) | memo + notebook | submission |

Students already have ME 239, so Lecture 2 points back to it rather than reteaching Bayes, Gaussians, or multivariate Gaussians.

---

## Learning objectives

A student who finishes the module can:
1. Process raw three-point-bend data into strength and strength-to-weight, and record the failure mode.
2. Compute flexural yield, the empirical bending/average-web-shear interaction, and LTB; contrast the interaction surrogate with a pointwise von Mises first-yield check; and compare the mode proxies with observed failures.
3. Explain where the physics is incomplete or fixture-dependent, and stop trusting a number when the data says to.
4. Fit a log-response GP; distinguish posterior median, epistemic uncertainty, aleatory observation noise, and total posterior-predictive uncertainty.
5. Use MUI and EI to choose the next test, and explain why acquisition uses epistemic rather than total uncertainty.
6. Combine physics and ML to recommend a beam under uncertainty, and defend it in a memo.
7. Reflect on a real test result and revise the design.

---

## The two-query ground-truth step (the part with logistics)

After the two pre-labs, each group has produced two designs: an **equation-optimal** beam (from Pre-lab 1) and a **vanilla-GP** beam (from Pre-lab 2). They get to "test" those two against a ground-truth model, and only those two. Those two new data points then feed their final design.

**Recommended approach: force every group to the same two beams.** Simpler and fairer than per-group gating, and grading stays uniform.

How to make it deterministic so everyone lands on the same two beams:
- Pre-lab 1 fixes the design space, constants, and mass model, so the str/w optimization has one answer. Everyone's equation-optimal beam is identical: **b = 1.25 mm, H_web = 13.4 mm** (LTB proxy, predicted capacity ≈ 599 N, str/w ≈ 46.6 N/g at σ_y = 66.5 MPa, k = 0.377, cs = 2.25). The capacity is the minimum of `P_LTB` and `P_interaction_surrogate`; the latter combines outer-fiber bending with whole-web average shear and must not be described as a pointwise von Mises calculation.
- Pre-lab 2 fixes the GP kernel, the noise, the optimizer seed, and the candidate grid, so the GP recommendation is identical. **After the campaign, cut the student subset, run Pre-lab 2 once on it, and freeze the resulting (b, H_web) in `ground_truth.py`.** The frozen design is subset-dependent: change the subset and the GP recommendation moves.
- The two frozen results are inserted directly into the next notebook. Students do not import the staff oracle or submit arbitrary coordinates, so there is no third class-wide query.

**What the ground-truth model is.** An oracle fit to the tested module beams and frozen after the follow-up campaign. Its returned strengths at the two class designs are hardcoded into the student sequence, so every group sees the same result. Their reported N/g values use estimated mass, not a hidden measured mass. `ground_truth.py` is the staff provenance record; students do not receive the full data or model.

> Why an oracle built from real data, not the physics model: the physics model is the thing the students are testing, so using it as the answer key would be circular. A GP on the tested beams is the best stand-in for reality we have, and it carries whatever the equations miss, including abrupt layer-line fractures.

**Fallback if you want per-group designs instead:** gate each query with a one-time code tied to the group, logged server-side, that returns the oracle value at the group's submitted (b, H_web). More flexible, more to build and monitor. Not recommended for the first run.

---

## Notes on each artifact

**Lecture 1 (`ME323_Lecture1_slides.md`).** Frame the challenge, introduce bending, the empirical bending/average-web-shear interaction, and LTB, then compare model proxies with observed failure morphology. The two-optima illustration uses the handbook starting value `k = 0.33` versus textbook `k = 1`; the current class calibration is `k = 0.377`, with equation design `(1.25, 13.40)`. The interaction surrogate must not be called a pointwise von Mises calculation. For a live walkthrough, use the current Pre-lab 1 KEY. Its KEY-only LTB block compares a basic full-span model with the current fixture-aware branch on the B10/L150 geometry. Do not live-run `ME323_Failure_Modes_Educational.ipynb`; it uses historical geometry, data, mass, and interaction terminology.

**Pre-lab 1 (`ME323_Module1_Prelab1_FailureModes_student.ipynb`).** Students load the subset, compute str/w, interpret every section property, fill in flexural yield and the average-web-shear interaction surrogate, and compare that surrogate with a provided pointwise `My/I + VQ/(It)` first-yield calculation. A four-panel parity diagnostic labels beam IDs, predicted mode proxies, and observed failure-note categories. Students tune σ_y, k, and cs manually before automated calibration, then optimize str/w. The interaction surrogate remains in `capacity()` to preserve the calibrated class flow; it is explicitly not called pointwise von Mises. The KEY adds an instructor comparison of basic and fixture-aware LTB assumptions and their resulting optima.

**Lecture 2 (`ME323_Lecture2_slides.md`).** Builds the ML ladder from ME 239 following the Bilionis lecturebook flow (`Bilionis lecturebook/`): Bayes, Gaussian (the 3% repeats), covariance between neighboring beams, conditioning (animated), the MVN-to-GP leap (animated), GP prior vs posterior, the kernel and noise as modeling choices, explore/exploit, the BO loop (animated MUI), EI, OED, and the physics-informed GP. Every concept lands on the beam problem. Visual sourcing, for honesty in front of the class: `gif_gp_learning_beams.gif` and `gif_pigp_vs_gp.gif` come from the earlier span-200 campaign (the slides say so); `fig_gp_prior_posterior`, `fig_kernel_lengthscale`, `fig_noise_fits`, `fig_explore_exploit`, and `gif_bo_mui` are labeled illustrations built from the physics model plus synthetic 3% noise; `gif_conditioning` and `gif_mvn_to_gp` are pure concept graphics. Rebuild the illustrations and the two campaign GIFs from the real 44-beam data when it lands.

**Pre-lab 2 (`ME323_Module1_Prelab2_ML_student.ipynb`).** Students compare only vanilla, data-driven GP choices: raw versus log str/w, scaled versus unscaled inputs, RBF versus Matérn-5/2, and shared versus ARD length scales. Common plot scales and physical-unit length scales expose how each assumption changes the surface. Orthogonal slices through the equation-query point show the posterior median with nested epistemic and total-predictive bands, followed by explicit sigma-decomposition plots. Students refit at 1/3/10% noise and compare full-2D MUI and EI scans. Acquisition uses epistemic sigma; a bound for one future observation uses total sigma. The final section resets everyone to the frozen class recipe: z-scored `(b,H_web)`, centered log str/w, ARD RBF, 3% noise, MUI ψ=1, fixed seed/grid/exclusion rule. It must return (1.44, 13.39), regardless of which exploratory setup a student preferred.

**Submission 1 (`ME323_Module1_Submission1_Design_student.ipynb`).** The final design notebook adds the two common query results, prints the failure-note evidence again, and clearly distinguishes those query beams from the group's third, printed design. Students compare four lanes on leave-one-out RMSE: A, the plain Pre-lab 2 GP; B, log strength divided by estimated mass afterward; C, extra features `logP` and `P_LTB/P_bend`; and D, a GP correction to calibrated physics. The chosen lane rebuilds posterior-median and epistemic-sigma maps. The final cell computes the default MUI design and prints the evidence required by the memo.

**Submission 2 (`ME323_Module1_Submission2_Lightweight_student.ipynb`).** Three parts. (1) Recall from memory. (2) Reflection: students enter strength, measured mass, observed failure note, posterior median, and epistemic sigma. The code reports measured and estimated mass separately and checks the result against a total-uncertainty interval using the same estimated-mass denominator as the GP. (3) The lightweight challenge: design the lightest nominal geometry whose lower posterior-predictive bound for one future beam clears 700 N. The bound combines epistemic sigma with 3% aleatory noise. Output includes the posterior median, uncertainty allowance, calibrated-physics check, closest-in-mass lighter infeasible point, and 1/3/10% noise sensitivity table.

**GT selection & noise, faculty notebook (`ME323_Module1_GT_Selection_and_Noise_FACULTY.ipynb`).** Staff-only receipts for the frozen ground truth, shareable with reviewing faculty. Self-contained: loads the two committed campaign CSVs (`data/ground_truth_B10_L150.csv`, 44 beams; `data/ibeam150_additional_tests.csv`, 19 follow-up tests), measures print-to-print noise from the repeat groups (3.5% pooled; the 3% classroom assumption stands), runs the leave-one-location-out model-formulation ablation (winner `gpf_sw_matern`, LOLO RMSE 2.53 N/g — reproduces `gt_model_choice.json` exactly), retrains and maps the GT with its uncertainty, and records the caveats (corrected-support confound, thin-web frontier, noise sensitivity). It distills notebooks 15–16 of the local `ibeam150_analysis/` pipeline. **It and the two campaign CSVs must come off the public repo before the course goes live** — they reveal the answer surface students are graded against.

**Shear model selection, faculty notebook (`ME323_Module1_Shear_Model_Selection_FACULTY.ipynb`).** Staff-only case for replacing the physics layer's shear term, for senior-faculty review before any downstream change. The fracture notes show every non-buckling "shear" failure is a flange–web separation — an interlayer failure of the printed joint. The notebook states four candidate models with their equations (average web shear at bulk yield, the current `P_shear`; peak VQ/It at the neutral axis; junction shear flow at bulk yield; junction shear flow against a calibrated interface strength) and tests them by back-calculating the implied strength at each measured separation load: the junction measure returns a near-constant τᵢ = 17.5 MPa (CoV 15%) where the current measure scatters 22–53 MPa (CoV 41%); no bend beam ever exceeded τᵢ; the genuine pointwise von Mises alternative is tested and rejected (at bulk yield it never governs anywhere in the box, degenerating to flexure-only; calibrated, 18 of 37 bend beams violate its envelope without separating — bending stress runs parallel to the interface and cannot fail it); mode identification improves 89% → 93%; worst separation strength error drops 41% → 18%; later batches validate the geometry scaling out-of-sample while showing τᵢ drifts to 11–15 MPa with print session and support quality (carry it as a distribution, not a constant). Self-contained from committed CSVs: the two campaign files above plus `data/ibeam150_campaign_notes.csv` (verbatim fracture notes), `data/ibeam150_support_experiment.csv` (the 10-beam interleaved support test), and `data/ibeam150_traces_downsampled.csv` (force–displacement traces). **These also come off the public repo before go-live** (they reveal campaign strengths). Adopting the recommendation touches `ibeam150_common.py`, the Pre-lab 1 physics lane (c_s becomes τᵢ), the GT-model features, and the frozen class numbers — none of that is changed yet.

---

## Before the first run (staff checklist)

- Keep the 14-beam student subset frozen unless you intend to regenerate every checkpoint and both class query coordinates.
- Verify that the public handout keeps both `weight_g` and the notebook-computed `mass_est_g`; do not replace one with the other.
- Recheck the fixture before relying on calibrated `k = 0.377`. It is a fixture-specific effective parameter, not transferable material data.
- Confirm the two common query results in `ground_truth.py`: equation `(1.25, 13.40)` and locked GP `(1.44, 13.39)`.
- Rebuild both PowerPoints after slide-source changes and spot-check the native GIFs in slideshow mode.
- Keep `P_TARGET = 700 N` synchronized across the notebook, guide, rubric, and lab announcement.
- **Hand each group their test result** for Submission 2: measured peak load, the observed failure mode (recorded on test day), and a photo of the broken beam. The reflection section cannot run without it.

## Common pitfalls to watch

- Students trusting the equation optimum because it is precise. The point of Pre-lab 1 is that it sits at the LTB boundary, where the model rests on the most assumptions.
- Calling `exp(mu_log)` a mean. It is the posterior median on the response scale.
- Using total predictive sigma as an exploration bonus, or epistemic sigma alone as a future-beam reliability bound.
- Comparing strength-to-weight values with measured-mass and estimated-mass denominators without naming the difference.
- Over-tuning the noise to fit. Flag that a somewhat inflated noise can generalize better, and that there is no single correct value.

---

## Assessment

Two graded submissions, weighted toward the memos. See `ME323_Module1_Rubric.md`. The notebooks are checked for correctness and for the required code, but the reasoning in the memo carries the grade.
