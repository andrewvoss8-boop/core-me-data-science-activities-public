# Grader comments — Pre-lab 2 (ML / GP modeling)

Dimension: **Data/ML model and validation** (20%). Reviewed by a Claude
Fable 5 grader agent against `ME323_Module1_Prelab2_ML_KEY.ipynb`, with
independent recomputation from `student_beams_B10_L150.csv` (md5
`620db004…` — the course copy) using the notebook's own pipeline code
(sklearn 1.6.1).

## 1. Fill-ins: complete, run, matching

- All code cells executed cleanly in strict order (execution counts 1–9, no
  errors, no stale cells).
- The two designated fill-ins (cell 15) match the key exactly: `mui` returns
  `mu + psi*sigma`; `ei` computes `imp = mu - y_best - xi` feeding the guarded
  `np.where(sigma > 1e-12, imp*norm.cdf(Z)+sigma*norm.pdf(Z), 0.0)` form.
- Checkpoint verification (all recomputed independently, not just compared to
  the key's printed outputs):

| Claim (cell) | Notebook value | Recomputed | Verdict |
|---|---|---|---|
| Handout best-of-15 / eq beam (cell 1) | 36.88 / 37.48 N/g | 36.878 / 37.473 | CONFIRMED |
| Official kernel (cells 3, 7) | `0.0778**2 * RBF([1.7, 0.144])`, phys (3.41, 0.48) mm | identical | CONFIRMED |
| Five-option kernels (cell 3) | raw `2.51**2*RBF([1.59,0.135])`; Matérn `[2.07,0.178]`; shared `0.303` | identical | CONFIRMED |
| Slice crossing (cell 10) | median 36.79, σ_epi 0.0268, σ_total 0.0402 | identical | CONFIRMED |
| Noise table (cell 12) | 1% → (1.58, 14.88); 3%/10% → (1.00, 13.39) | identical incl. medians/sigmas | CONFIRMED |
| Acquisition table (cell 15) | all 10 rows | identical incl. acquisition values | CONFIRMED |
| Locked design (cell 20) | (1.00, 13.39), 36.7 N/g, σ 0.032 | identical | CONFIRMED |
| Memo Q1 table | argmax (1.00, 13.20): 36.78 / σ 0.028; strip (1.00, 14.88): 35.61 / σ 0.055 | 36.775 / 0.0277; 35.607 / 0.0553 | CONFIRMED |
| Memo Q2: raw target "moved the argmax prediction from 36.81 to 36.78 and left the location unchanged" | — | raw-option argmax (1.000, 13.203) → 36.810; log-option argmax (1.000, 13.203) → 36.775 | CONFIRMED |
| Memo Q2: shared-scale fit `[0.61, 1.00]` mm, argmax (1.10, 13.39), 36.65 | — | [0.608, 0.998] mm, (1.097, 13.390) → 36.648 | CONFIRMED |
| Memo Q2: beams 14 / 12 at 35.35 / 28.10 N/g | — | 35.346 / 28.095 | CONFIRMED |
| Memo Q3: incumbent 37.47 never beaten; median peaks 36.78 → mean improvement negative everywhere | — | centered-log max μ 0.1148 < y_best 0.1336 | CONFIRMED |
| Memo Q4: "Removing beam 16 would move the GP's peak" | — | refit without beam 16: median argmax (3.23, 14.70), MUI ψ=1 pick (3.13, 14.14) — the peak leaves the thin-b strip entirely | CONFIRMED |
| Memo Q4: "all three capacities tie within 1%" | — | their own Pre-lab 1 prints P_bend=621, P_sep=623, P_LTB=618 N — 0.8% spread | CONFIRMED |
| Memo Q4: interface "strength is 38% of the bulk estimate" | — | their Pre-lab 1 calibrated τᵢ = 16.76 MPa; 16.76/43.9 = 0.382 | CONFIRMED |
| Memo Q5: pick medians 36.42 / 36.67 / 33.50, σ_total 0.049 / 0.044 / 0.103 | — | identical | CONFIRMED |

- The key's staff-only cells 21–23 (assert + regularized isotropic Matérn
  comparison) are absent, as expected — no deduction.
- Template version note: the copy this student worked from predates commit
  `414b6a3`; its cell-2 kernel bullet is the older short form ("RBF assumes a
  very smooth response…") rather than the current failure-mode-prior paragraph.
  Not a student edit and not a deduction — and their Q2 independently supplies
  the physics link that paragraph now teaches (b sets separation capacity via
  shear flow; beams 12/14/15 separated).
- Grader note (as in both precedents): the rubric's "LOO table as 17-point
  evidence" element does not appear in Pre-lab 2 in either version; it is
  graded from Submission 1.

## 2. Memo answers vs key targets (cell 22)

**Uncertainty vocabulary.** Posterior median, epistemic sigma, aleatory noise,
and total uncertainty are each used for their own job throughout; "posterior
median" never conflated with a mean. As with both precedents, the
median-vs-mean distinction lives in template cells and is not restated in the
student's own words.

**Q1 (region where uncertainty changes the action).** Meets the key target and
exceeds it: names the strip at (1.00, 14.88), tabulates median and σ_epi
against the median argmax (both rows recomputed exactly), states the flip
thresholds precisely (MUI flips at ψ=2; EI at every ξ tested — both confirmed
in the table), and gives the right mechanism: nothing is tested in the thin-b
gap between beam 9 at (1.75, 15.80) and the H≈13.3 cluster (confirmed — no
tested beam with b ≤ 1.8 has H between 13.25 and 15.8). "The median map fills
the gap by interpolation and reports a mediocre number with false confidence
in its own smoothness" is exactly the reading the question wants.

**Q2 (setup choices).** Meets the key target fully. Picks the starkest
printed-kernel contrast — ARD [3.41, 0.476] mm vs shared [0.61, 1.00] mm —
and reads it as evidence, with both argmaxes recomputed and correct. The
identifiability argument is the right one: ARD explains the scatter at similar
H_web (beam 14 at 35.35 vs beam 12 at 28.10, both confirmed) by shrinking one
length scale, "a statement about identifiability under sparse data, not about
beam mechanics," then cross-checks against Pre-lab 1 physics that says b does
matter. The quantified null contrast (raw vs log target: 36.81 vs 36.78,
location unchanged — recomputed exactly) is precisely the claim a prior
submission got wrong; this student got it right and used it to say which knob
was load-bearing. Best Q2 of the three submissions reviewed.

**Q3 (MUI vs EI).** Meets and exceeds: correct table citations, correct
reading of ψ as sigmas-of-upside with ψ=0 as pure exploitation, and the
incumbent-pinning mechanism verified — the posterior median peaks at 36.78,
below the 37.47 incumbent, so mean improvement is negative everywhere and ξ
"shifts a threshold that no design was clearing anyway" (confirmed: all five
ξ values pick (1.00, 14.88); only the acquisition value decays 0.0053 →
0.0007). That ξ-insensitivity sentence is the one a precedent grader had to
ask for; here it is unprompted. One overstatement: "That makes it a pure
uncertainty maximizer here" — recomputation says no: the grid's σ argmax is
(1.00, 8.92) with σ=0.078, which EI does not pick; EI still trades median
against sigma (its pick has σ=0.055). The student's own preceding sentence
("ranking by how much probability mass sigma can push above the incumbent")
is the correct mechanism; the "pure" label overshoots it. The closing
observation — both rules land on b=1.00, "the one thing neither rule can tell
you is a problem" — correctly anticipates the section-6.5 edge-pick lesson.

**Q4 (why the designs differ; conditioning).** The key's central target —
agreement is conditioning, not independent convergence — is hit squarely and
in the student's own image: beam 16 is the equation design's own result, the
highest value in the set, sitting under a 0.476 mm length scale, so "the GP
is partly agreeing with the equation model because it was handed the equation
model's answer as data… one shared data point wearing two hats." Their
falsifiable version of it — "Removing beam 16 would move the GP's peak" — was
verified by refit: without beam 16 the peak moves to (3.23, 14.70), out of
the thin-b strip entirely. The failure-notes half is also complete: beams
12/14/15 flange-web separations, beam 15's double-interface loss quoted
accurately from the data, beam 9's fixture tipping, and the synthesis ties
back to their own Pre-lab 1 calibration ("a mechanism whose strength is 38%
of the bulk estimate and drifts between print sessions" — both numbers
traceable and correct). Fully meets, exceeds.

**Q5 (noise robustness).** Meets the key target and adds a decomposition the
key does not ask for: the *location* is stable across 3–10% but not at 1%,
while the *confidence* is sensitive everywhere (medians 36.42/36.67/33.50,
σ_total 0.049/0.044/0.103 — all recomputed exactly; the "3.2 N/g swing" is
36.67−33.50). The closing paragraph is the honest version of the noise
lesson: no repeats in the data, 3% comes from outside it, 4.4% is structured
drift that violates what `alpha` encodes, "the refits bracket a defensible
range; they do not identify a correct value." As in both precedents, the
template's invited 4.4% rerun is not performed; the 3–10% stability argument
implicitly brackets 4.4% but the loop is not explicitly closed.

## 3. Errors, misconceptions, standout insights

No contradicted numerical claims. Four minor slips, none load-bearing:

- "the 17 beams contain no repeated geometry" (Q5) — the notebook's dataset
  has 16 beams (15 handout + equation beam); 17 exists only after
  Submission 1's beam is added. The no-repeats point itself is correct.
- "dropping to 1% moves it 1.7 mm" (Q5) — recomputed distance from
  (1.58, 14.88) to (1.00, 13.39) is 1.60 mm Euclidean (1.49 mm in H alone);
  1.7 matches neither.
- "the predicted median at the pick falls from 36.42 to 36.67 to 33.50" (Q5)
  — the numbers are right but the sequence rises before it falls; "falls" is
  the wrong verb for the first step.
- "pure uncertainty maximizer" (Q3) — overstated, as detailed above; the
  adjacent mechanism sentence is correct.

Standout, all verified: the raw-vs-log null contrast used as evidence of
which assumption is load-bearing (Q2); the beam-16-removal counterfactual
stated as a checkable prediction that checks out dramatically (Q4); the
location-vs-confidence decomposition of "robust" (Q5); and the ξ-decay
reading of EI (Q3).

No integrity issues: no faculty/GT-only values (σ_y = 65.242, k = 0.424578,
τᵢ = 21.056, GT optimum ~42.1 @ (1.4, 12.1), 38.74 / 525.6) appear anywhere
in the notebook; the 4.4% figure is disclosed in the template itself
(cell 13), and the 38% / 16.76 MPa interface figure traces to the student's
own Pre-lab 1 calibration, not the faculty value.

## 4. Card rows 3–5: notebook evidence (graded separately)

- Row 3 (data claim): cell 1 prints 16 beams and the failure-note table; the
  memo's "17 beams" slip is the only count error — check whether the card
  repeats it.
- Row 4 (model choice): Q2 is strong evidence — the ARD-vs-shared
  identifiability argument with printed length scales, plus the physics
  cross-check that ARD's "b is nearly irrelevant" contradicts the calibrated
  shear-flow mechanism.
- Row 5 (uncertainty accounting): Q5's location-vs-confidence decomposition,
  the no-repeats/can't-self-validate point, and the structured-drift
  violation of the iid `alpha` assumption are all card-grade material.

## 5. Assessment: EXCELLENT (19/20)

All required code complete, executed in order, and every checkpoint plus
every checkable memo number independently reproduced — including the two
hardest claims, the raw-target null result and the beam-16-removal
counterfactual, both of which survive adversarial recomputation. The memo
hits all five key targets, including the Q4 conditioning argument in full
and the best Q2 of the submissions reviewed. Held at 19 rather than 20 by
accumulated small-caliber looseness: "17 beams," "1.7 mm," a non-monotone
"falls," the overstated "pure uncertainty maximizer," and the un-run 4.4%
check the template names as the real one.
