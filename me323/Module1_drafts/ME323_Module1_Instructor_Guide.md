# ME 323 Module 1 — Instructor Guide (DRAFT)
*Beam design under uncertainty: physics, machine learning, print, test, reflect.*

This is the master doc for the module. It holds the schedule, the learning objectives, the design of the two-query ground-truth step (the one piece with logistics to get right), and notes on each artifact. The other files in this folder are the two lecture decks, the four student notebooks (two pre-labs, two submissions), and the rubric.

**Slide formats.** Each lecture ships as both a Marp markdown source (`ME323_Lecture{1,2}_slides.md`) and a built PowerPoint (`ME323_Module1_Lecture{1,2}.pptx`, 16:9). The GIFs are embedded as native `image/gif`, so they animate in PowerPoint 365 / 2019 slideshow mode. Rebuild the decks after changing any figure with `python3 build_pptx.py`.

**Module configuration.** Flange width 10 mm, total height 18 mm, test span 150 mm, printed length 172 mm (11 mm overhang past each support). Design space: web thickness `b` in [1.25, 7] mm, web height `H_web` in [5, 16] mm. Mass model: `KMASS = 0.2045` g/mm² of cross-section, which is PLA density times the 172 mm printed length. Dataset: the 44-beam ground-truth set (`ground_truth_B10_L150.csv`), Latin-hypercube over the design space; predicted modes split 40 bend / 2 shear / 2 LTB. The strength column lands when the test campaign finishes; every notebook checks for it and says so if it is missing.

**What students see.** Students never get the full 44. The notebooks load `student_beams_B10_L150.csv`, a 12-to-16-beam subset staff cut after seeing the data. The oracle (`ground_truth.py`) fits all 44, so it knows things the students' GP does not, and the two-query step can surprise them. Which beams go in the subset is a real decision; see the checklist below.

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
4. Fit a GP surrogate and read its mean and its uncertainty.
5. Use an acquisition function to choose the next test, and explain the explore/exploit tradeoff.
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

**What the ground-truth model is.** An oracle fit to the tested module beams and frozen after the follow-up campaign. Its mean values at the two class designs are hardcoded into the student sequence, so every group sees the same result. `ground_truth.py` is the staff provenance record; students do not receive the full data or model.

> Why an oracle built from real data, not the physics model: the physics model is the thing the students are testing, so using it as the answer key would be circular. A GP on the tested beams is the best stand-in for reality we have, and it carries whatever the equations miss, including abrupt layer-line fractures.

**Fallback if you want per-group designs instead:** gate each query with a one-time code tied to the group, logged server-side, that returns the oracle value at the group's submitted (b, H_web). More flexible, more to build and monitor. Not recommended for the first run.

---

## Notes on each artifact

**Lecture 1 (`ME323_Lecture1_slides.md`).** Frame the challenge, walk the three failure modes (bending-stress and web-shear diagrams are in `figures/`), show the failure-mode map, then show two places the physics falls short: the fracture-vs-yield traces (`fig_brittle_traces.png`, from instrumented bend tests) and the two-optima map (`fig_two_optima.png`: swapping the fixture-calibrated `k = 0.33` for the textbook `k = 1` moves the optimum across the design space). The deck carries `<!-- PLACEHOLDER -->` comments for photos and a parity plot that need the new campaign: a hero shot of a beam on the fixture, three failed beams (yielded / split along layers / tipped), an LTB clip, and the 44-beam parity plot. Live-run a few cells from the instructor walkthrough notebook (`ME323_Failure_Modes_Educational.ipynb`) if time allows.

**Pre-lab 1 (`ME323_Module1_Prelab1_FailureModes_student.ipynb`).** Students load the subset, compute str/w, interpret every section property, fill in flexural yield and the average-web-shear interaction surrogate, and compare that surrogate with a provided pointwise `My/I + VQ/(It)` first-yield calculation. A four-panel parity diagnostic labels beam IDs, predicted mode proxies, and observed failure-note categories. Students tune σ_y, k, and cs manually before automated calibration, then optimize str/w. The interaction surrogate remains in `capacity()` to preserve the calibrated class flow; it is explicitly not called pointwise von Mises.

**Lecture 2 (`ME323_Lecture2_slides.md`).** Builds the ML ladder from ME 239 following the Bilionis lecturebook flow (`Bilionis lecturebook/`): Bayes, Gaussian (the 3% repeats), covariance between neighboring beams, conditioning (animated), the MVN-to-GP leap (animated), GP prior vs posterior, the kernel and noise as modeling choices, explore/exploit, the BO loop (animated MUI), EI, OED, and the physics-informed GP. Every concept lands on the beam problem. Visual sourcing, for honesty in front of the class: `gif_gp_learning_beams.gif` and `gif_pigp_vs_gp.gif` come from the earlier span-200 campaign (the slides say so); `fig_gp_prior_posterior`, `fig_kernel_lengthscale`, `fig_noise_fits`, `fig_explore_exploit`, and `gif_bo_mui` are labeled illustrations built from the physics model plus synthetic 3% noise; `gif_conditioning` and `gif_mvn_to_gp` are pure concept graphics. Rebuild the illustrations and the two campaign GIFs from the real 44-beam data when it lands.

**Pre-lab 2 (`ME323_Module1_Prelab2_ML_student.ipynb`).** Students compare only vanilla, data-driven GP choices: raw versus log str/w, scaled versus unscaled inputs, RBF versus Matérn-5/2, and shared versus ARD length scales. Common plot scales and physical-unit length scales expose how each assumption changes the surface. They distinguish epistemic from total predictive uncertainty, refit at 1/3/10% noise, and compare full-2D MUI and EI scans. The final section resets everyone to the frozen class recipe: z-scored `(b,H)`, centered log str/w, ARD RBF, 3% noise, MUI ψ=1, fixed seed/grid/exclusion rule. It must return (1.44, 13.39), regardless of which exploratory setup a student preferred.

**Submission 1 (`ME323_Module1_Submission1_Design_student.ipynb`).** The final design notebook: they load their two new ground-truth points, then section 2 lays out four modeling lanes for the same 16 beams — **A** the plain Pre-lab 2 GP; **B** fit strength in newtons and divide by the deterministic mass afterwards; **C** physics as extra input features (`logP`, the log of the calibrated capacity prediction, and `stab = P_LTB/P_bend`); **D** a residual GP on `log(measured/P_phys)`, so the GP learns only the correction to the calibrated physics. Three "under the surface" figures show each mechanism at work: the target each lane hands the GP (lane B's job is ~3× wider; A's and D's leftovers are the same size — D's payoff is between/beyond the data, not in the scatter), a slice at b = 1.25 mm where lane A sags to the class average between beams while lane D rides the physics shape, and maps of the two lane-C features with the fitted length scales printed (on the full 16 beams the MLE pushes `logP`'s length scale to its bound, i.e. the fit ignores that feature). A leave-one-out block — RMSE table, parity plots, per-beam miss table — then scores all four lanes; students pick one, defend it in the memo, and the chosen lane rebuilds the `MU`/`STD` surfaces their decision code runs on. **Open question for the team: the LOO block is a candidate for deletion.** It is the only out-of-sample scoreboard students get and teaches that a model does not grade its own homework; against it, runtime and the risk that students anchor on "lowest RMSE" instead of the judgment the memo grades. The KEY carries a staff note with the removal recipe if we cut it. Deliverables: the beam spec, a memo with the rationale, and the three notebooks.

**Submission 2 (`ME323_Module1_Submission2_Lightweight_student.ipynb`).** Three parts. (1) Recall from memory. (2) Reflection: students enter their measured beam result plus the central prediction and epistemic sigma recorded in Submission 1; supplied code performs the log-space ±2σ comparison. (3) The lightweight challenge: design the lightest beam whose lower predictive bound clears 700 N. The output prints the selected design, uncertainty allowance, calibrated-physics check, and nearest lighter infeasible grid point so every memo comparison is defined.

**GT selection & noise, faculty notebook (`ME323_Module1_GT_Selection_and_Noise_FACULTY.ipynb`).** Staff-only receipts for the frozen ground truth, shareable with reviewing faculty. Self-contained: loads the two committed campaign CSVs (`data/ground_truth_B10_L150.csv`, 44 beams; `data/ibeam150_additional_tests.csv`, 19 follow-up tests), measures print-to-print noise from the repeat groups (3.5% pooled; the 3% classroom assumption stands), runs the leave-one-location-out model-formulation ablation (winner `gpf_sw_matern`, LOLO RMSE 2.53 N/g — reproduces `gt_model_choice.json` exactly), retrains and maps the GT with its uncertainty, and records the caveats (corrected-support confound, thin-web frontier, noise sensitivity). It distills notebooks 15–16 of the local `ibeam150_analysis/` pipeline. **It and the two campaign CSVs must come off the public repo before the course goes live** — they reveal the answer surface students are graded against.

---

## Before the first run (staff checklist)

- Finish the 44-beam test campaign and add `strength_N` to `ground_truth_B10_L150.csv`. Record the observed failure mode for each beam while testing; the parity-plot discussion and the reflection memos lean on those notes.
- Cut the student subset (12 to 16 beams) into `student_beams_B10_L150.csv`, same schema, after seeing the data. Aims for the cut: cover the design space, include at least one shear-governed and one LTB-governed beam, include a beam that fractured abruptly, and hold back the beams nearest the eventual GP recommendation so the two queries still carry news.
- Confirm `K = 0.33` on the module fixture with a few instrumented tests. `K` is a fixture property; it was fit on a different setup and span, and the equation design sits in the LTB corner, where `K` matters most.
- Run Pre-lab 2 on the frozen student subset and freeze the GP design in `ground_truth.py` (`ALLOWED["gp"]`).
- Regenerate the illustration figures and the two campaign GIFs from the real data, put a real parity plot into Lecture 1's "Does the theory match the data?" slide, and fill the photo placeholders in Lecture 1 (beam on fixture, three failure modes, LTB clip) while testing — shoot them during the campaign, not after.
- **Pick `P_TARGET` for the Submission 2 challenge** after the campaign data is in. Aim for a load where the confident-feasible set is a real region, not a corner: roughly the 40th–60th percentile of measured strengths works, and check that the lightest confident design is bending-governed so the "holds it in bending" framing is clean. Announce it in lab.
- **Hand each group their test result** for Submission 2: measured peak load, the observed failure mode (recorded on test day), and a photo of the broken beam. The reflection section cannot run without it.

## Common pitfalls to watch

- Students trusting the equation optimum because it is precise. The point of Pre-lab 1 is that it sits at the LTB boundary, where the model rests on the most assumptions.
- Treating GP uncertainty as error bars to ignore. The uncertainty is the actionable part for explore/exploit.
- Over-tuning the noise to fit. Flag that a somewhat inflated noise can generalize better, and that there is no single correct value.

---

## Assessment

Two graded submissions, weighted toward the memos. See `ME323_Module1_Rubric.md`. The notebooks are checked for correctness and for the required code, but the reasoning in the memo carries the grade.
