# Grader comments — Submission 1 (Design) + decision card + knob sweep

Dimensions: **Synthesis and the design decision** (25%) and **Preregistration
and experimental plan** (15%), plus verification of every numerical claim on
the decision card. Reviewed by a Claude Fable 5 grader agent against
`ME323_Module1_Submission1_Design_KEY.ipynb` and the faculty knob sweep.
Claims marked "rerun" were independently recomputed by the grader from the
student-facing data (`student_beams_B10_L150.csv` + the two class-query rows)
through the notebook's own pipeline. The notebook executes cleanly top to
bottom, and **every printed output is byte-identical between the recorded
notebook and the grader's fresh run** — the defects found below all live in
card/memo prose the notebook never computes.

## 1. Card-claim verification table

| # | Card claim | Status |
|---|---|---|
| 1 | Pick (1.85, 12.15), t_f 2.93 mm, mass 16.56 g | Mass EXACT (16.5599 g, rerun). Flange thickness is exactly 2.925 mm; the notebook prints 2.92, the card says 2.93 — the card disagrees with its own notebook at the rounding digit |
| 2 | Physics 721 N bending = 43.6 N/g; separation 1024 N (+42%); Mcr/My = 1.16 | Capacities EXACT (rerun 721.14 / 1024.34 N, margin +42.04%). 43.6 is a mis-rounding of 43.547 (notebook correctly prints 43.5). Mcr/My = 1.1554 → "1.16" is generous rounding, and it clears the student's own 1.15 feasibility floor by only 0.5% — a +0.3% change in k drops it below; the card does not say so |
| 3 | Lane D median 38.07 N/g; 12-model ensemble spans 33.5–39.5, mean 36.3 | EXACT (rerun 38.0733; ensemble 33.48–39.48, mean 36.26). The ensemble appears in no notebook cell — asserted-but-reproducible |
| 4 | LOO: D wins both kernels (2.34/2.38 vs 2.89/2.94); sweep: 146 of 150 non-lane-B picks in b∈[1.0,2.5]×H∈[11.5,15.0]; lane corners A→wall, C→(2.1,13.6), D→(1.4,11.7); exactly 1 of 150 clears both constraints | EXACT throughout (rerun of the full 200-row sweep reproduces every count and corner; grader's regenerated CSV in `knob_sweep_grader_rerun.csv`). See §3 on what the card does *not* say about the one feasible pick |
| 5 | σ_epi 0.048, σ_total 0.065, 95% interval 33.5–43.2 N/g = 555–716 N | EXACT (0.0479 / 0.0650 / 33.52–43.25 N/g = 555.0–716.2 N) |
| 6 | Nearest support: #15 (1.00,12.50) 0.92 mm, 34.41; #16 1.33 mm, 37.47; #17 1.50 mm, 36.64; #14 (1.40,10.40) 1.81 mm, 35.35; quoted morphology notes | EXACT throughout (Euclidean distances 0.9192/1.3314/1.5034/1.8069; all values and note quotes match the CSV verbatim) |
| 7 | Measured/physics ratios 1.23/0.93/0.88/0.79/0.77 (#12/14/15/17/16); thick-web bend beams 0.90–1.09; #16/#17 at Mcr/My ≈ 0.99 with zero/negative separation margin; #14 negative margin, Mcr/My 1.43 | EXACT (rerun 1.231/0.928/0.875/0.786/0.771; thick-web 0.904–1.092; #16: 0.994, +0.4%; #17: 0.979, −6.4%; #14: −12.2%, 1.431). Computed in no cell — asserted-but-reproducible, and the card's central argument |
| 8 | σ_epi 0.048 vs "0.022 at beam 16's coordinates"; "no lane's posterior median reaches 37.47 anywhere in the box"; "EI collapses to ranking by σ alone"; "ψ = 2 and EI both go to the wall"; ξ 0→0.05 changes nothing | **The weakest row — three claims fail.** (a) σ_epi at beam 16 reruns to **0.0267** under the student's own knobs (no tried setting yields 0.022): asserted-and-wrong, and "more than double" is actually 1.8×. (b) "No lane reaches 37.47" is **contradicted by the card's own lane-D numbers** (38.07 in row 3, 40.4 in row 9; lane D's median exceeds 37.47 over 7.6% of the grid). It is true only of lanes A and C. (c) Consequently "EI collapses to σ-ranking" is wrong for the student's own primary lane: lane-D EI reruns to (1.39, 11.71) — the *median-driven* pick, identical to MUI's, far from the σ-argmax at (1.00, 7.80). (d) ψ=2 under lane D goes to (1.87, 8.54), an interior low-H region, not a wall. The ξ claim holds for lane D but vacuously. The replicate-band check (no beam within \|Δb\|<0.15, \|ΔH\|<0.30) is EXACT |
| 9 | Rejected rival (1.39, 11.71): lane D 40.4; sep margin ~1%; "0.02 mm in web thickness from beam 14"; lane A 33.0 / lane C 36.1 there; 9.4 N/g ensemble spread | Median EXACT (40.43); margin +0.54% ("~1%" fair); Δb to beam 14 is 0.0129 mm — "0.02" is wrong at its own precision (trivial). Lane A/C values quoted (33.0/36.1) match the RBF/3% ensemble members, not the student's own Matérn/4.4% knobs (33.40/35.77) — a knob-mismatch blur, not an error, since both support the point. Spread EXACT: full 12-model span at the rival is 9.42 N/g |
| 10 | Separation needs τᵢ < 11.8 MPa (a 30% drop); k fitted to beam 9 alone; Mcr/My = 1.16 ↔ k 11% worse | EXACT (τᵢ threshold 11.80 MPa = −29.6%; k for Mcr=My at the design = 0.4190 = +11.2% over 0.377; beam 9 is the sole LTB-governed calibration point per Pre-lab 1) |

## 2. Computed vs asserted — and the one concealment

Computed in the notebook: the 17-beam assembly, LOO table, posterior maps,
four-panel decision map, unfiltered lane-D argmax (1.39, 11.71) with its
40.4/0.048 printout, the veto table of §4b, the feasibility filter, the full
submitted-design block (mass, three capacities, margins, median, sigmas,
interval, nearest-support line), and a from-scratch 200-row knob sweep with
CSV export and scatter.

Asserted in prose but reproduced exactly by the grader: the 12-model
ensemble (rows 3, 9), the measured/physics ratio table with per-beam margins
(row 7 — the argument the whole card stands on), the region-split LOO table
(memo §2: A 3.25/2.72, C 3.67/2.88, D 3.34/1.76 thin/thick — exact), the
noise ladder 39.77/38.96/38.07/38.04, the kernel-swap value 38.59, lane A's
33.7 at the design, and the τᵢ/k thresholds of row 10. This is a large body
of genuinely-performed, uncell'd analysis; every number of consequence
checks out.

**The one concealment, and it matters:** cell 14 computes a fine-grid
(0.01 mm) filtered argmax and immediately overwrites it with
`B_FINAL, H_FINAL = 1.85, 12.15` under the comment "printable rounding of
the argmax." The grader's rerun of that exact fine grid puts the filtered
argmax at **(1.84, 11.81)**, median 38.45 N/g. The submitted point is a
manual move of +0.34 mm in H_web — to a *lower* median (38.07) and a
*lower* LTB reserve (1.155) — and the pre-override argmax is never printed,
so nothing in the notebook or memo discloses that a hand adjustment
happened, let alone defends it. 0.34 mm is not rounding. The stated
selection procedure ("searching inside that envelope lands at 1.85/12.15")
is therefore not the procedure that was run. There may well be a defensible
reason (distance from the feasibility boundary's corner, printability of
0.05-mm-multiples); the defect is that the reason is nowhere on record and
the comment affirmatively mislabels the step. In a module whose rubric
grades "the quality of the decision given the information available," an
undisclosed manual override of the declared procedure at the single
decisive step is the most serious finding in this submission.

Two smaller prose-vs-record slips, both in the memo's stress test (§5):
the claimed RBF unfiltered argmax move "to (1.35, 11.90)" reruns to
(1.40, 11.60) — the H direction of the move is wrong; and "lane A's fitted
ARD length scale in H_web is 0.48 mm" (§2) reproduces only under the class
RBF/3% defaults, not the student's stated Matérn/4.4% knobs (0.73 mm).
Memo §4's "the disagreement panel is at its widest near our design" is
loose — the panel's true maximum (~9.6 N/g) sits 1.3 mm away near
(1.1, 13.3); the card's version ("among the widest") is the accurate one.

## 3. Memo quality

- **Three figures named:** yes (§6) — but the first, the region-split LOO
  table, is computed in no cell (numbers verified exact); the four-panel map
  and sweep scatter exist and match their descriptions.
- **Synthesis at the candidate:** the strongest of the three examples. The
  card puts 43.6 (physics) and 38.07 (GP) side by side *at the point*,
  explains the 5.5 N/g gap with a mechanism (mode-margin-dependent physics
  bias) instead of a preference, refuses to average, and stakes the print on
  the physics being closer — with the refusal itself argued ("we would
  rather defend a margin argument than an unstable argmax"). The ratio table
  behind it is exact, and the GT evaluation vindicates the mechanism story
  (see `gt_design_evaluation.md`: measured/physics 0.944 at the pick's
  42% margin vs 0.90 at the rival's 1% margin vs 0.77 at the triple point).
- **Rejected alternatives:** two, both quantified, both verified — the
  incumbent replicate (rejected for buying a confirmation instead of a
  discrimination; a direct, argued inversion of the student2 strategy) and
  the lane's own unfiltered argmax (rejected on a 0.5% separation margin and
  the 9.4 N/g ensemble spread). The "2.3 N/g cut... to buy a 42% margin" is
  arithmetic the card actually shows.
- **The sweep reading:** "the neighborhood is stable, the point is not" is
  the honest version of a sensitivity result most submissions would
  overclaim, and the lane-corner decomposition (A/C/D pull to three corners;
  the lane is the knob doing the work) is exactly the reading the template
  asks for. One blur: the card never says *which* pick was the "exactly one"
  clearing both constraints — it is A-plain/RBF/10%/EI at (7.00, 13.58), a
  b = 7.0 outlier nowhere near the submitted design, so it supports the
  card's "every sweep pick is infeasible-or-elsewhere" argument less
  directly than the sentence implies. Memo §6's "146 of 150 picks in one
  neighborhood and none inside the feasible region" is true only under the
  charitable parse (none *of the 146*); read plainly against card row 4's
  "exactly one," the two statements collide.
- **Risk posture:** "Exploring, and we should not dress it up" — declared
  before the pick, with ψ = 0.5 argued from the one-print stake. But the
  EI-rejection rationale ("diagnosis rather than taste") rests on row 8's
  contradicted claims: under the student's own lane the diagnosis is false
  (lane-D EI lands on the same point as their MUI). The *decision* (MUI,
  low ψ) is unaffected; the stated *grounds* are partly wrong, and this is
  the card's one argument that does not survive verification.

**Decisive question 1 (why this beam vs next-best):** answered twice over,
quantified, verified — margin-bought-back physics vs the replicate's
zero-information print and the rival's knife-edge margin.

**Decisive question 2 (what evidence would have changed the choice before
printing):** explicitly on record — the row-10 falsifiers state the τᵢ and k
values that would flip the argument, the "assumption most likely to break"
row names the alternative bias mechanism (thinness-scaling rather than
margin-scaling) that would make 38.07 optimistic, and §5 concedes the point
is knob-sensitive. The thin spot: nothing states what evidence would have
justified *keeping* the unfiltered argmax (e.g. a beam-14 morphology note
showing partial-fracture rather than clean separation).

## 4. Copying check: clean

The knob-sweep CSV was written by the notebook (`knob_sweep.csv`) but not
shipped with the package; the grader regenerated it from cell 17
(deterministic, `random_state=0`) — `knob_sweep_grader_rerun.csv` — and it
is structurally independent of the faculty sweep: 200 rows on noise
{1, 3, 4.4, 8, 10} × {MUI ψ∈{0, 0.5, 1, 2}, EI} vs the faculty 160 on
{1, 3, 5, 10} × {ψ∈{0, 0.5, 1, 2}, EI}; schema `lane/kernel/noise/acq/dial/
b/H_web/median/sigma/sep_margin/mcr_my` at full float precision vs the
faculty's rounded `rule/b_mm/H_web_mm`; all four faculty-only columns
(`phys_mode`, `gt_*`) absent, and the two feasibility columns are the
student's own addition. Greps across all four artifacts for every
faculty/GT-only value (GT calibration 65.242/0.4246/21.056, GT optimum,
41.08/680.2, 38.74/525.6) return zero hits outside base64 image bytes.

## 5. Assessment and recommended scores

The most ambitious synthesis of the three examples, and the best-vindicated:
the mechanism-specific-bias argument is original, quantified, computed from
evidence available to the student, and the frozen GT confirms both its
direction and its magnitude ordering. Everything the notebook computes
reproduces exactly, and the large asserted-but-uncell'd analysis body
reproduces too. Against that stand defects the precedent submissions did
not have: an undisclosed manual override of the declared selection procedure
mislabeled as rounding, and a risk-posture row where three of five claims
fail verification — including one number (σ = 0.022) that reproduces under
no setting and one claim contradicted by the card's own row 3.

**Synthesis and the design decision: 22/25** — top-band synthesis,
alternatives, and sweep reading; minus one for the cell-14 override
concealment (the procedure defended is not the procedure run), minus one
for row 8's failed claims (wrong σ, self-contradicted incumbent claim, and
an EI diagnosis that is false for the student's own lane), minus one for
the accumulated precision slips (43.6/2.93 against the notebook's own
printout, the §5 RBF-argmax direction error, the knob-mismatched citations,
the "none inside the feasible region" collision).

**Preregistration and experimental plan: 15/15** — the sharpest
preregistration of the three: interval with stated z whose bounds match the
notebook to 0.1 N/g, a named morphology written in the note-taker's own
vocabulary with the two mechanisms it excludes, an assumption-most-likely-
to-break row that names the *rival explanation* for the observed bias rather
than a generic worry, falsifiers in both directions with different stated
consequences (including the upside trigger both precedents lacked), a
weaker-signal tier (twist-before-fracture → k), and row-11 readings
pre-committed to three outcome bands. The falsifier threshold equals the
interval bound exactly (555 N), fixing the 430-vs-433 defect the student2
example was deducted for.
