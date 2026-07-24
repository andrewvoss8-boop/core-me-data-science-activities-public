# Grader comments — Pre-lab 2 (ML / GP modeling)

Dimension: **Data/ML model and validation** (20%). Reviewed by a Claude
Fable 5 grader agent against `ME323_Module1_Prelab2_ML_KEY.ipynb`, with
independent recomputation from `student_beams_B10_L150.csv` (md5-identical to
the course copy) using the notebook's own pipeline code.

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
| Handout best-of-15 / eq beam (cell 1) | 36.88 / 37.48 N/g | 36.88 / 37.47 | CONFIRMED |
| Official kernel (cells 3, 7) | `0.0778**2 * RBF([1.7, 0.144])`, phys (3.41, 0.48) mm | identical | CONFIRMED |
| Five-option kernels (cell 3) | raw `2.51**2*RBF([1.59,0.135])`; Matérn `[2.07,0.178]`; shared `0.303` | identical | CONFIRMED |
| Slice crossing (cell 10) | median 36.79, σ_epi 0.0268, σ_total 0.0402 | identical | CONFIRMED |
| Noise table (cell 12) | 1% → (1.58, 14.88); 3%/10% → (1.00, 13.39) | identical incl. medians/sigmas | CONFIRMED |
| Acquisition table (cell 15) | all 10 rows | identical | CONFIRMED |
| Locked design (cell 20) | (1.00, 13.39), 36.7 N/g, σ 0.032 | identical | CONFIRMED |
| Memo Q1: σ_epi small on the ridge, large up the wall | 0.028 @ (1.0,13.2) vs 0.055 @ (1.0,14.88) | CONFIRMED |
| Memo Q2: raw-target surface "can rise toward the light corner" | — | raw-option surface argmax (1.00, 13.20); light corner (1.0, 16.0) = 31.15 N/g vs 36.69 at (1.0, 13.39) — it *falls* toward the corner | CONTRADICTED |
| Memo Q2: unscaled inputs "change the learned geometry" | — | unscaled fit converges to identical physical scales [3.411, 0.476] mm (printed in the student's own cell 3) | CONTRADICTED |
| Memo Q4: equation design "lands on a three-mode boundary" | — | Pre-lab 1 territory | NOT CHECKED |

- The key's staff-only cells 21–23 (assert + regularized isotropic Matérn
  comparison) are absent, as expected — no deduction.
- Grader note (as in the student1 precedent): the rubric's "LOO table as
  17-point evidence" element does not appear in Pre-lab 2 in either version;
  it is graded from Submission 1.

## 2. Memo answers vs key targets (cell 22)

**Uncertainty vocabulary.** Posterior median, epistemic sigma, aleatory noise,
and total uncertainty are each used for their own job throughout; "posterior
median" is never conflated with a mean. As with the precedent submission, the
distinction lives in template cells and is never restated in the student's own
words.

**Q1 (region where uncertainty changes the action).** Meets the key target
cleanly: contrasts ψ=0 at (1.0, 13.2) with ψ=1 at (1.00, 13.39) and EI at
(1.00, 14.88), and correctly attributes the high-web pick to the larger σ_epi
rather than the median (35.61 < 36.78, confirmed). Solid.

**Q2 (setup choices).** The weakest answer, and the one deduction that
matters. Two of its three claims are false for this notebook's pipeline: (a)
"the raw-strength target… after predicting newtons and dividing by mass, light
high-web beams can receive an amplified N/g prediction" — the raw option
regresses str/w in N/g directly (`response = sw_obs`, cell 3); no
newtons-then-divide step exists, and the recomputed raw surface falls, not
rises, toward the light corner (31.15 N/g at (1.0, 16.0)). (b) The
unscaled-input claim is contradicted by the student's own cell 3 printout,
which shows the unscaled fit landing on the identical physical length scales
[3.411, 0.476] mm. Meanwhile the starkest printed-kernel contrast — shared
scale [0.608, 0.998] mm vs ARD [3.411, 0.476] mm — is never mentioned. The
key target explicitly asks for the printed kernels/length scales as evidence;
this answer asserts mechanisms instead of reading them. The closing
"conditional posterior, 16 points" caveat is right, but it caps a paragraph
whose evidence is wrong.

**Q3 (MUI vs EI).** Good: correct reading of ψ as an explicit sigma bonus and
ξ as an improvement threshold, correct table citations, and the right
mechanism for EI's edge-seeking ("it sees little confident improvement over
the incumbent elsewhere" — confirmed: grid median max 36.78 < y_best 37.47).
Minor miss: the generic claim that larger ξ "pushes the choice" is not borne
out by their own table, where all five ξ values pick the same point — worth a
sentence, not given.

**Q4 (why the designs differ; failure notes).** The failure-notes half is
strong: beams 12/14/15 flange-web separations, beam 9 fixture tipping, "two
models can agree on coordinates while sharing blindness to the morphology."
But the key's central answer to "why is the agreement weaker than it looks" —
the GP is conditioned on data containing the equation beam's own result, so
agreement is conditioning, not independent convergence — is only gestured at
("after seeing the equation beam return 37.48… it learns a lower empirical
ridge") and the weakness is instead attributed to shared omission of
morphology. That is a real but secondary point; the self-referential-evidence
argument is the one the question is fishing for. Partial.

**Q5 (noise robustness).** Meets the key target: correct 1% vs 3%/10% reading,
correct statement that 3%/10% agreement does not validate either value, and
integrates the 4.4%-with-structure disclosure. Neither the template's invited
4.4% rerun nor the precedent submission's bracketing argument (4.4% lies
between two agreeing settings) appears — the disclosure is cited but not used
to close the loop.

## 3. Errors, misconceptions, standout insights

Errors: the two CONTRADICTED Q2 claims above. Both are checkable against
cell 3's own printed output, which the rubric flags directly ("code that
contradicts the memo costs the dimension it belongs to").

Standout: the Q4 failure-notes synthesis and the correct EI mechanism in Q3
are genuinely good; Q1 is textbook-clean.

No integrity issues: no faculty/GT-only values (σ_y = 65.242, k = 0.424578,
τᵢ = 21.056, GT optimum ~42.1 @ (1.4, 12.1), 38.74 / 525.6) appear anywhere in
the notebook; the 4.4% figure is disclosed in the template itself (cell 13).

## 4. Assessment: GOOD (16/20)

All required code complete, in order, and every numerical checkpoint
independently reproduced; Q1, Q3, and Q5 meet the key targets. The deduction
is concentrated where the rubric looks hardest: Q2's sensitivity discussion
rests on two claims the student's own cell 3 output contradicts while missing
the shared-vs-ARD contrast that output actually demonstrates, and Q4 supplies
a secondary argument where the key's conditioning argument belongs.
**16/20** — flawless, fully reproduced code and three strong memo answers,
held below excellent by a kernel-sensitivity answer that asserts mechanisms
its own printed evidence refutes and a Q4 that misses the conditioning point.
