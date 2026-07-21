# ME 323 Module 1 — Instructor Guide (DRAFT)
*Beam design under uncertainty: physics, machine learning, print, test, reflect.*

This is the master doc for the module. It holds the schedule, the learning objectives, the design of the two-query ground-truth step (the one piece with logistics to get right), and notes on each artifact. The other files in this folder are the two lecture decks, the four student notebooks (two pre-labs, two submissions), the rubric, the decision card (`ME323_Module1_DecisionCard.md` — the recurring one-page reasoning scaffold plus the preregistration table), the student-run build/test lab spec (`ME323_Module1_Lab_BuildTest.md`), and the raw-trace pack (`student_traces_4beams.csv`, reduced by students in Pre-lab 1).

**Slide formats.** Each lecture ships as both a Marp markdown source (`ME323_Lecture{1,2}_slides.md`) and a built PowerPoint (`ME323_Module1_Lecture{1,2}.pptx`, 16:9). The GIFs are embedded as native `image/gif`, so they animate in PowerPoint 365 / 2019 slideshow mode. Slide text is duplicated in `build_pptx.py`; edit both sources, then rebuild with `python3 build_pptx.py`.

**Module configuration.** Flange width 10 mm, total height 18 mm, test span 150 mm, printed length 172 mm (11 mm overhang past each support). Design space: web thickness `b` in [1.0, 7] mm (widened from [1.25, 7] on 2026-07-20), web height `H_web` in [5, 16] mm. The nominal-geometry mass estimate is `mass_est_g = 0.2045 A`; the handout also retains `weight_g`, the measured printed-beam mass. Those columns should differ. Strength-to-weight models and pre-print optimizations use estimated mass so every candidate has a denominator before it is printed. The staff ground-truth-model provenance contains 85 usable tests: the initial 44-beam campaign, 19 follow-up tests, and 22 proper-supports recalibration prints (one further LTB test was stopped early and is excluded as censored; the 10-test interleaved support experiment is deliberately held out of training — see the faculty GT notebook).

**What students see.** The notebooks load the frozen 15-beam `student_beams_B10_L150.csv` handout — the 14 ridge_blind14 prints plus the real b = 1.0 seed test at (1.0, 12.5), 475.0 N, added 2026-07-20 to anchor the widened box. Students do not get the full ground-truth dataset. The two common query results extend their table to 16 and then 17 beams. Changing the subset changes every GP checkpoint and requires a full regeneration.

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
| 5 | **Two-query results** — the equation design and the vanilla-GP design were queried against the ground-truth model by staff; the frozen results are baked into the Pre-lab 2 and Submission 1 headers | in notebook | (no live event) |
| 6 | **Design + Submission 1** — pick a beam from physics + ML + the 2 new points; turn in design, rationale, notebooks, and the decision card with its preregistration table; this beam gets printed and tested | notebook + memo + card | submission |
| 7 | **Build + test (student-run)** — groups CAD, slice, print, weigh, test, photograph, and reduce their own raw trace, with Purdue-team guidance and UG supervision; see `ME323_Module1_Lab_BuildTest.md` | ≥4 weeks, interleaved with other lab activities | lab |
| 8 | **Reflect + Submission 2** — recall, reflect on the test result, the lightweight-bending challenge (lightest beam that confidently holds `P_TARGET` N; not tested, rationale graded), then refit the model with the group's own result and report what it changes | memo + notebook | submission |

Students already have ME 239, so Lecture 2 points back to it rather than reteaching Bayes, Gaussians, or multivariate Gaussians.

---

## Learning objectives

A student who finishes the module can:
1. Process raw three-point-bend data into strength and strength-to-weight, and record the failure mode. (Exercised twice: Pre-lab 1 section 1b reduces four campaign force–displacement traces — including deciding whether the LTB beam's peak is a material strength or a fixture artifact — and each group reduces its own beam's trace after test day.)
2. Compute flexural yield, the junction shear-flow separation check, and LTB; calibrate (σ_y, k, τᵢ) against test data and judge whether each fitted value is a correction to a handbook number or the measurement of a property no handbook lists; and compare the mode proxies with observed failures.
3. Explain where the physics is incomplete or fixture-dependent, and stop trusting a number when the data says to.
4. Fit a log-response GP; distinguish posterior median, epistemic uncertainty, aleatory observation noise, and total posterior-predictive uncertainty.
5. Use MUI and EI to choose the next test, and explain why acquisition uses epistemic rather than total uncertainty.
6. Combine physics and ML to recommend a beam under uncertainty, and defend it in a memo.
7. Reflect on a real test result and revise the design — Submission 2 section 3 refits the class model with the group's own tested beam and asks what moved.

The through-line the module keeps returning to, stated once so every artifact can point at it: **physics says what should happen and where failure lives; the GP says what the data support and where we're still uncertain; engineering judgment decides what to build; the test says what we got wrong.** The decision card is that four-sentence loop as a form.

---

## Group and individual structure

Groups submit one set of notebooks, one decision card, one preregistration
table, one beam, and one memo per submission; the group must converge on one
model and one design (internal disagreement goes in the memo as the rejected
alternative, card row 9). Individual components: Submission 2's recall answers
and a short individual postscript. The split (85% group / 15% individual) and
the postscript spec live in `ME323_Module1_Rubric.md`. Grade the decision, not
the beam: realized strength enters only as a small bonus.

## Why 700 N

`P_TARGET = 700 N` is an instructional spec, not a customer requirement, and
the materials should say so if asked. It was chosen so the feasibility
boundary crosses the middle of the tested design space — the handout strengths
run 314–949 N, so at 700 N some tested beams pass and some fail, the
lower-bound constraint actually binds, and the lightest feasible design is a
genuine trade rather than a corner of the box. Treat it the way practicing
engineers treat a spec they didn't set: as fixed, with the reasoning graded
against it.

---

## The two-query ground-truth step (the part with logistics)

After the two pre-labs, each group has produced two designs: an **equation-optimal** beam (from Pre-lab 1) and a **vanilla-GP** beam (from Pre-lab 2). They get to "test" those two against a ground-truth model, and only those two. Those two new data points then feed their final design.

**Recommended approach: force every group to the same two beams.** Simpler and fairer than per-group gating, and grading stays uniform.

How to make it deterministic so everyone lands on the same two beams:
- Pre-lab 1 fixes the design space, constants, and mass model, so the str/w optimization has one answer. Everyone's equation-optimal beam is identical: **b = 1.10 mm, H_web = 13.25 mm** (predicted 48.7 N/g at the class calibration σ_y = 66.8 MPa, k = 0.377, τᵢ = 16.76 MPa). The capacity is the minimum of `P_bend`, `P_sep` (junction shear flow against the calibrated interface strength), and `P_LTB`. The printed proxy there is "LTB", but all three mode capacities tie within ~1% (roughly 621 / 623 / 618 N) — the optimum sits on a three-way mode knife edge, which the notebook now prints explicitly.
- Pre-lab 2 fixes the GP kernel, the noise, the optimizer seed, and the candidate grid, so the GP recommendation is identical. **After the campaign, cut the student subset, run Pre-lab 2 once on it, and freeze the resulting (b, H_web) in `ground_truth.py`.** The frozen design is subset-dependent: change the subset and the GP recommendation moves.
- The two frozen results are inserted directly into the next notebook's header: the equation-query result opens Pre-lab 2 and the GP-query result opens Submission 1. There is no live in-lab query event. Accepted trade-off: a student who opens Pre-lab 2 early reads the Pre-lab 1 answer. Students do not import the staff ground truth model or submit arbitrary coordinates, so there is no third class-wide query.

**What the ground truth model is.** A statistical model fit to the tested module beams and frozen after the follow-up campaign. Its returned strengths at the two class designs are hardcoded into the student sequence, so every group sees the same result. Their reported N/g values use estimated mass, not a hidden measured mass. `ground_truth.py` is the staff provenance record; students do not receive the full data or model. The student materials say plainly what the ground truth model is — a staff model fit to the prior campaign, standing in for the testing machine — in Pre-lab 1's closing cell, the Pre-lab 2 header, and the Submission 1 header, along with the fact that the only physically printed beam is the group's Submission 1 design. Expect the "is 482.6 N a real broken beam?" question anyway, and answer it the same way.

> Why a ground truth model built from real data, not the physics model: the physics model is the thing the students are testing, so using it as the answer key would be circular. A GP on the tested beams is the best stand-in for reality we have, and it carries whatever the equations miss, including abrupt layer-line fractures.

**Fallback if you want per-group designs instead:** gate each query with a one-time code tied to the group, logged server-side, that returns the ground-truth value at the group's submitted (b, H_web). More flexible, more to build and monitor. Not recommended for the first run.

---

## Notes on each artifact

**Lecture 1 (`ME323_Lecture1_slides.md`).** Frame the challenge, introduce bending, the junction shear-flow separation check (the stress measure is textbook shear flow; the strength τᵢ is a calibrated printed-interface property no handbook lists), and LTB, then compare model proxies with observed failure morphology. The two-optima illustration uses the handbook starting values versus the class calibration (σ_y = 66.8 MPa, k = 0.377, τᵢ = 16.76 MPa), with equation design `(1.10, 13.25)`. For a live walkthrough, use the current Pre-lab 1 KEY. Its KEY-only LTB block compares a basic full-span model with the current fixture-aware branch on the B10/L150 geometry. Do not live-run `ME323_Failure_Modes_Educational.ipynb`; it uses historical geometry, data, mass, and the retired interaction terminology.

**Decision card (`ME323_Module1_DecisionCard.md`).** The recurring one-page scaffold — eleven rows from "what beam" through "what would change your mind," including a model-choice row where the group defends its GP architecture and its sensitivity — plus the preregistration table filed before printing. It concentrates the module's reasoning in one place so it stops being dispersed across notebook prompts, and it is the grader's tool for separating reasoning from post-hoc storytelling. Filed with Submission 1 (rows 1–10 + preregistration) and Submission 2 (row 11).

**Build/test lab (`ME323_Module1_Lab_BuildTest.md`).** The student-run print/test sequence: CAD, slice, print, weigh, preregister, test, reduce the raw trace, document. Purdue-team items are marked `[PURDUE]` and must be filled in before go-live. Includes the photo shot list that replaces the deck's placeholder graphics.

**Pre-lab 1 (`ME323_Module1_Prelab1_FailureModes_student.ipynb`).** Section 1b hands students four real force–displacement traces from the campaign (`student_traces_4beams.csv`, beams 6, 9, 13, 14 of the handout — downsampled ×5 with the peak row preserved, so peaks match `strength_N` exactly) and has them reduce raw data to strength themselves: find the peak, read abrupt fracture versus gradual failure off the curve shape, and decide whether beam 9's 314.4 N is a material strength or a fixture/stability artifact. Then students load the subset, compute str/w, interpret every section property, and fill in flexural yield and the junction shear-flow separation check `P_sep = 2 τᵢ Ix t_w / Q_f`, starting τᵢ at the bulk guess σ_y/√3 = 43.9 MPa. A four-panel parity diagnostic labels beam IDs, predicted mode proxies, and observed failure-note categories; the note classifier deliberately confronts real data quality (the notes spell it "seperation", and beam 7 is a mixed morphology — the notebook teaches matching the data, not the dictionary). Students tune σ_y, k, and τᵢ manually before automated calibration, then optimize str/w; the final cell prints all three mode capacities at the optimum so the bend–LTB knife edge is visible. The KEY adds an instructor comparison of basic and fixture-aware LTB assumptions and their resulting optima.

**Lecture 2 (`ME323_Lecture2_slides.md`).** Builds the ML ladder from ME 239 following the Bilionis lecturebook flow (`Bilionis lecturebook/`): Bayes, Gaussian (the 3% repeats), covariance between neighboring beams, conditioning (animated), the MVN-to-GP leap (animated), GP prior vs posterior, the kernel and noise as modeling choices, explore/exploit, the BO loop (animated MUI), EI, OED, and the physics-informed GP. Every concept lands on the beam problem. Visual sourcing, for honesty in front of the class: `gif_gp_learning_beams.gif` and `gif_pigp_vs_gp.gif` come from the earlier span-200 campaign (the slides say so); `fig_gp_prior_posterior`, `fig_kernel_lengthscale`, `fig_noise_fits`, `fig_explore_exploit`, and `gif_bo_mui` are labeled illustrations built from the physics model plus synthetic 3% noise; `gif_conditioning` and `gif_mvn_to_gp` are pure concept graphics. Open item: rebuild the illustrations and the two campaign GIFs from the real campaign data (the dataset has long since landed; the concept graphics still show the span-200 era and are labeled as such on the slides).

**Pre-lab 2 (`ME323_Module1_Prelab2_ML_student.ipynb`).** Students compare only vanilla, data-driven GP choices: raw versus log str/w, scaled versus unscaled inputs, RBF versus Matérn-5/2, and shared versus ARD length scales. Common plot scales and physical-unit length scales expose how each assumption changes the surface. Orthogonal slices through the equation-query point show the posterior median with nested epistemic and total-predictive bands, followed by explicit sigma-decomposition plots. Students refit at 1/3/10% noise and compare full-2D MUI and EI scans. Acquisition uses epistemic sigma; a bound for one future observation uses total sigma. The final section resets everyone to the frozen class recipe: z-scored `(b,H_web)`, centered log str/w, ARD RBF, 3% noise, MUI ψ=1, fixed seed and grid. There is no tested-point exclusion rule any more — in the widened box the locked rule picks an untested point on its own (and EI agrees with it). It must return (1.00, 13.39), regardless of which exploratory setup a student preferred.

**Submission 1 (`ME323_Module1_Submission1_Design_student.ipynb`).** The final design notebook adds the two common query results, prints the failure-note evidence again, and clearly distinguishes those query beams from the group's third, printed design. A "Your knobs" dashboard names every modeling decision as an explicit assumption: lane (`CHOICE`), kernel (`KERNEL`, RBF vs Matérn — the LOO table scores both), assumed noise (`NOISE_PCT`), acquisition rule (`ACQ`, MUI vs EI), and the explore–exploit dial (ψ for MUI, ξ for EI). Students compare four lanes on leave-one-out RMSE: A, the plain Pre-lab 2 GP; B, log strength divided by estimated mass afterward; C, extra features `logP` and `P_LTB/P_bend`; and D, a GP correction to calibrated physics. The chosen knobs rebuild posterior-median and epistemic-sigma maps. The final cell computes the acquisition pick and prints the evidence required by the memo; the notebook also states explicitly that a near-replicate print must be defended in the memo (the default pick lands 0.25 mm from the tested equation beam, on the b = 1.0 boundary where the separation notes live; at the default knobs MUI and EI now split, which is itself a teaching beat).

**Submission 2 (`ME323_Module1_Submission2_Lightweight_student.ipynb`).** Four parts. (1) Recall from memory. (2) Reflection: students enter strength, measured mass, observed failure note, posterior median, and epistemic sigma. The code reports measured and estimated mass separately and checks the result against a total-uncertainty interval using the same estimated-mass denominator as the GP. (3) The lightweight challenge: design the lightest nominal geometry whose lower posterior-predictive bound for one future beam clears 700 N. The bound combines epistemic sigma with 3% aleatory noise. Output includes the posterior median, uncertainty allowance, calibrated-physics check, closest-in-mass lighter infeasible point, and 1/3/10% noise sensitivity table. (4) Refit with the group's own result: their tested beam joins the 16 frozen beams, the class-default model refits, and the notebook reports whether the lightweight design or the best-str/w pick moved — no checkpoint (it depends on their beam); graded through memo Q7. This closes the print→test→reflect→redesign loop.

**GT selection & noise, faculty notebook (`ME323_Module1_GT_Selection_and_Noise_FACULTY.ipynb`).** Staff-only receipts for the frozen ground truth, shareable with reviewing faculty. Self-contained: loads the three committed CSVs (`data/ground_truth_B10_L150.csv`, 44 campaign beams; `data/ibeam150_additional_tests.csv`, 19 follow-up tests; `data/ibeam150_ps_recalibration.csv`, 23 proper-supports prints, one censored LTB test excluded → 85 usable tests; the 10-test interleaved support experiment is deliberately held out of training and the notebook says why). It measures print-to-print noise from the repeat groups with unbiased pooling (≈4.4%; the 3% classroom α stands as a stated working value — the excess is structured session/printer variation, and the ablation's 3.5% variant does not improve LOLO), runs the leave-one-location-out model-formulation ablation, retrains and maps the GT with its uncertainty, and records the caveats (τᵢ scatter across print conditions, the improper/proper support mix in the training pool, the thin-web frontier, the fitted length scale riding its bound, the GT embedding its own physics). **Junction-shear roll (2026-07-17, commit 6037948):** because the GT winner is physics-informed (it takes `log P_phys` as a feature), the shear model is part of the ground truth. The zoo scored both formulations and the junction-shear physics won with the formulation unchanged — `gpf_sw_matern_sep` in the staff pipeline's records, LOLO 2.216 N/g / 5.30% MAPE on the 85 tests — and every τᵢ tested beat the old-physics incumbent, including the leak-free literature value, so the win is the shear model rather than the fitted constant. One result faculty should see: the uncalibrated `phys_*` lanes got *worse* under the new physics (the old interaction surrogate was an error-cancelling knockdown masking σ_y's ~13% flexure over-prediction — a GP does not need that crutch, a hand-calc does). **The re-freeze is complete**: `ground_truth.py`, the frozen class queries, and the student notebooks all carry the junction physics. (Those 2026-07-17 coordinates — equation (1.25, 13.20) → 39.09 N/g; GP (1.44, 13.20) → 38.90 N/g — were superseded on 2026-07-20 by the widened-box re-freeze: equation (1.10, 13.25) → 38.02 N/g; GP (1.00, 13.39) → 36.06 N/g, same GT model.) **This notebook and the three CSVs must come off the public repo before the course goes live** — see the go-live section below.

**Shear model selection, faculty notebook (`ME323_Module1_Shear_Model_Selection_FACULTY.ipynb`).** Staff-only case for replacing the physics layer's shear term, for senior-faculty review before any downstream change. The fracture notes show every non-buckling "shear" failure is a flange–web separation — a failure along the printed layer lines, which are weaker than solid material. The notebook states four candidate models with their equations (average web shear at bulk yield — the retired `P_shear`; peak VQ/It at the neutral axis; junction shear flow at bulk yield; junction shear flow against a calibrated interface strength) and tests them by back-calculating the implied strength at each measured separation load: the junction measure returns a near-constant τᵢ = 17.5 MPa (CoV 15%) where the current measure scatters 22–53 MPa (CoV 41%); no bend beam ever exceeded τᵢ; the genuine pointwise von Mises alternative is tested and rejected (at bulk yield it never governs anywhere in the box, degenerating to flexure-only; calibrated, 18 of 37 bend beams violate its envelope without separating — bending stress runs parallel to the interface and cannot fail it); mode identification improves 89% → 93%; worst separation strength error drops 41% → 18%; later batches validate the geometry scaling out-of-sample while showing τᵢ scatters 9.6–20.8 MPa with print condition (carry it as a distribution, not a constant); the new section 8c scores the proper-supports batch as a second out-of-sample pass (scaling holds, the single-strength envelope degrades to a band, mode-ID 78% vs the in-sample 93%). Self-contained from committed CSVs: the three campaign files above plus `data/ibeam150_campaign_notes.csv` (verbatim fracture notes), `data/ibeam150_support_experiment.csv` (the 10-beam interleaved support test), and `data/ibeam150_traces_downsampled.csv` (force–displacement traces). **These also come off the public repo before go-live** (they reveal campaign strengths). **The recommendation was adopted and rolled project-wide on 2026-07-17 (commit 6037948):** `ibeam150_common.py`, the Pre-lab 1 physics lane (c_s became τᵢ), the GT-model features, and the frozen class numbers all carry the junction model. This notebook is now the decision record rather than a pending proposal.

---

## Before the first run (staff checklist)

- Keep the 15-beam student subset frozen unless you intend to regenerate every checkpoint and both class query coordinates.
- Verify that the public handout keeps both `weight_g` and the notebook-computed `mass_est_g`; do not replace one with the other.
- Recheck the fixture before relying on calibrated `k = 0.377`. It is a fixture-specific effective parameter, not transferable material data.
- Confirm the two common query results in `ground_truth.py`: equation `(1.10, 13.25)` → 482.6 N / 38.02 N/g and locked GP `(1.00, 13.39)` → 438.7 N / 36.06 N/g.
- Rebuild both PowerPoints after slide-source changes and spot-check the native GIFs in slideshow mode.
- Keep `P_TARGET = 700 N` synchronized across the notebook, guide, rubric, and lab announcement.
- **Collect each group's decision card and preregistration table with Submission 1, before any print starts.** No preregistration, no test slot — the interpretation dimension of the rubric grades against it.
- **Hand each group their test result** for Submission 2: the raw force–displacement CSV (they reduce it themselves), the observed failure mode (recorded on test day), measured mass, and a photo of the broken beam. The reflection section cannot run without it.
- `ibeam150_analysis/run13_build_student_notebooks.py` is the source of truth for all eight student/KEY notebooks (re-synced 2026-07-21, including the trace section, decision-card wiring, and four-panel map). Edit the builder's templates, then regenerate; hand edits to the notebooks get overwritten by the next build.

## Common pitfalls to watch

- Students trusting the equation optimum because it is precise. The point of Pre-lab 1 is that it sits on a bend–LTB knife edge (the two capacities tie within ~1%; the printed proxy says "bend" only by a 0.999 threshold), where the model rests on the most assumptions.
- Calling `exp(mu_log)` a mean. It is the posterior median on the response scale.
- Using total predictive sigma as an exploration bonus, or epistemic sigma alone as a future-beam reliability bound.
- Comparing strength-to-weight values with measured-mass and estimated-mass denominators without naming the difference.
- Over-tuning the noise to fit. Flag that a somewhat inflated noise can generalize better, and that there is no single correct value.

---

## Assessment

Two graded submissions, weighted toward the memos and the decision card. See `ME323_Module1_Rubric.md` — the grade is organized as five module-level dimensions (physics 20%, data/ML 20%, synthesis 25%, preregistration 15%, test interpretation 20%) mapped onto the two submissions, with an 85/15 group/individual split and realized beam performance as a small bonus only. The notebooks are checked for correctness and for the required code, but the reasoning carries the grade.

**Memo format.** Each submission's memo is written in markdown cells at the end of that submission notebook, answering only that submission's numbered prompts, in order. Submission 1's memo covers its four prompts in about half a page; Submission 2's memo is the primary assessed artifact of the module, 400–800 words. The pre-lab memo questions are answered at the end of each pre-lab notebook and graded there, under the corresponding Submission 1 criteria. There is no separate memo document.

---

## Go-live: answer leakage (BLOCKER — needs a decision)

The public repo currently serves the students their data **and** the answers. Before go-live, the following must come off the public repo:

- `Module1_drafts/ME323_Module1_Prelab1_FailureModes_KEY.ipynb`, `..._Prelab2_ML_KEY.ipynb`, `..._Submission1_Design_KEY.ipynb`, `..._Submission2_Lightweight_KEY.ipynb`
- `Module1_drafts/ME323_Module1_GT_Selection_and_Noise_FACULTY.ipynb` and `..._Shear_Model_Selection_FACULTY.ipynb`
- `Module1_drafts/ground_truth.py` (the frozen answers and full provenance — its own docstring says to keep it away from students)
- `ibeam150_analysis/run13_build_student_notebooks.py` (the notebook builder — it embeds every FILL-IN solution and the frozen class values)
- `data/ground_truth_B10_L150.csv`, `data/ibeam150_additional_tests.csv`, `data/ibeam150_ps_recalibration.csv`, `data/ibeam150_campaign_notes.csv`, `data/ibeam150_support_experiment.csv`, `data/ibeam150_traces_downsampled.csv`, `data/ibeam150_master.csv`

(`data/student_beams_B10_L150.csv` and `data/student_traces_4beams.csv` stay public — the trace pack contains only beams already in the student handout, verified peak-for-peak against `strength_N`.)

Two structural problems make this more than a deletion checklist:

1. **The student notebooks fetch raw.githubusercontent URLs from this same repo** (`data/student_beams_B10_L150.csv` and the figures). Taking the repo private to hide the answers breaks the student data loads. Options: (a) move the student-facing assets to a separate public data-only repo and update the notebook URLs (one `run13` constant); or (b) keep this repo public for students and move every answer artifact to a private staff repo. Either works; pick one before go-live.
2. **Plain deletion is not enough**: everything above is already in git history. Hiding it requires a history rewrite or the private-repo move.
