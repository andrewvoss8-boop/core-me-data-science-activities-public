# Grader comments — Pre-lab 2 (ML / GP modeling)

Dimension: **Data/ML model and validation** (20%). Reviewed by a Claude
Fable 5 grader agent against `ME323_Module1_Prelab2_ML_KEY.ipynb`.

## 1. Fill-ins: complete, run, matching

- All code cells executed cleanly in strict order (execution counts 1–9, no
  errors, no stale cells).
- The two designated fill-ins (cell 15) match the key exactly: `mui` returns
  `mu + psi*sigma`; `ei` computes `imp = mu - y_best - xi`, guarded
  `Z = imp/safe`, and the
  `np.where(sigma > 1e-12, imp*norm.cdf(Z)+sigma*norm.pdf(Z), 0.0)` form.
- All checkpoint outputs match the key: fitted kernel
  `0.0778**2 * RBF([1.7, 0.144])` (cell 7); slice crossing median = 36.79,
  σ_epi = 0.0268, σ_total = 0.0402 (cell 10); noise table 1% → (1.58, 14.88),
  3%/10% → (1.00, 13.39) (cell 12); acquisition table (cell 15); locked
  design (1.00, 13.39), 36.7 N/g (cell 20).
- The key's staff-only cells 21–23 (assert + regularized isotropic Matérn
  comparison) are absent from the student notebook, as expected — no
  deduction.
- Grader note: the rubric's "LOO table as 17-point evidence with
  conditional-on-calibration caveat" element does not appear in Pre-lab 2 at
  all (in either version); it is graded from Submission 1 instead.

## 2. Memo answers vs key targets (cell 22)

**Median vs mean in log-space.** Never conflated; "posterior median" used
consistently and each quantity used for its own job. No student-authored
statement of the distinction (it lives in the template cell) — usage is
uniformly correct, statement never made in their own words.

**Epistemic vs aleatory / noise sensitivity (Q5).** "Robust in one direction,
sensitive in the other. The 3% and 10% refits both recommend (1.00, 13.39);
the 1% refit moves to (1.58, 14.88). So the pick survives assuming more noise
but not less. Since the staff campaign's pooled repeat scatter is about 4.4%
(with session structure), the sub-3% branch is the implausible one, which
makes the locked design defensible, but conditionally: it rests on believing
the rig is at least as noisy as claimed, an assumption the 16 beams
themselves (no repeats) cannot check." More granular than the key target, and
correctly ties alpha to both its regularization and predictive-band roles.
Q1 correctly uses σ_epi (not total) for acquisition reasoning.

**Kernel and length-scale sensitivity (Q2).** "Shared length scale vs ARD is
the starkest: ARD fits physical length scales of about 3.4 mm in b and
0.48 mm in H… the shared-scale fit is forced to one number… Sixteen scattered
points cannot strongly identify per-dimension smoothness, so the two surfaces
differ mainly by prior assumption. Matérn-5/2 vs RBF is milder… That the
surfaces differ under equally reasonable assumptions is evidence of what the
data leave undetermined, not evidence that any one option is true." Meets the
key target with printed-kernel evidence.

**Conditioning caveat (Q4).** "The GP design is the argmax of a data
interpolant whose training set includes the equation query itself. Their
agreement on the thin-b region is therefore partly self-referential… Two
models fed the same 16 points agreeing is much weaker than two independent
lines of evidence agreeing." Matches the key's "conditioning, not independent
convergence" target almost exactly, and adds the beam-9 fixture-artifact
observation.

## 3. Errors, misconceptions, standout insights

No substantive errors found.

Standout insights:

- Q3 explains *why* EI jumps to (1.00, 14.88) at every ξ: "the incumbent
  (37.48 N/g, the equation beam) is above the posterior median almost
  everywhere, so EI's expected improvement is dominated by the sigma term and
  behaves like an aggressive explorer… The disagreement is itself
  information: the model thinks no cheap win over 37.48 exists near data."
  The mechanism is correct (grid median max ≈ 36.8 < y_best 37.48) and goes
  beyond the key.
- Q4: "A scalar response cannot distinguish 475 N of ductile yield from
  475 N of brittle interface fracture, and that distinction is exactly what
  matters one step thinner" — the failure-morphology point the key wants,
  sharpened.

Minor gaps: (a) the template invites literally rerunning at 4.4% noise; the
student argued by bracketing (4.4% lies between 3% and 10%, which agree) — a
valid inference, but the explicit rerun is the "real check" the template
names. (b) "psi values a chance at upside directly" is loose phrasing (MUI's
σ bonus is not probabilistic), though the adjacent "prices upside linearly
through psi" is right. (c) Median-vs-mean never stated in their own words.

## 4. Assessment: EXCELLENT (19/20)

All required code complete, executed in order, matching the key; the memo hits
every key target and exceeds several — the EI mechanism, the conditioning
argument, and the directional noise reading that integrates the 4.4% staff
disclosure and the no-repeats limitation. Only cosmetic looseness remains.
