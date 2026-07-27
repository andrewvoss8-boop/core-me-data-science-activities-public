# Grader comments — Pre-lab 1 (Failure Modes)

Dimension: **Physics model and assumptions** (20%). Reviewed by a Claude
Fable 5 grader-verification agent against
`ME323_Module1_Prelab1_FailureModes_KEY.ipynb` (Jul 24 key). Every numerical
claim below was independently recomputed from `student_beams_B10_L150.csv`
and `student_traces_4beams.csv` via a rerun of the full code path, not taken
from the notebook's own printouts.

**Template-version note (staff):** this submission was completed against the
**pre-fix template** (pre-commit `b391ee9`, Jul 24). Every given markdown cell
is byte-identical to `b391ee9~1`, including the since-corrected section-1b
prose ("an abrupt cliff after the peak is a fracture"), the erroneous cell-6
commentary ("the cliff beams are the ones whose notes say *fracture*"), and
the old memo Q5 wording ("which trace shapes separate abrupt fracture from
gradual failure?") — a prompt that presupposes exactly the shape→mechanism
mapping the shipped traces contradict. The student wrote only the six code
fill-ins and the memo cell. This matters for the Q5 deduction below.

## 1. Fill-ins: PASS — all checkpoints hit exactly

- Cell 5 trace reduction (`peak_N = tr.groupby("beam_id").force_N.max()`):
  functionally identical to the key; checkpoint table matches the handout to
  0.1 N (759.0 / 314.4 / 582.6 / 654.6 — independently recomputed, exact).
- Cell 8 `str_to_weight`: matches key; checkpoint hit (beam 4 at 36.88 N/g,
  beam 15 at 34.41 N/g — recomputed 36.878 / 34.411).
- Cell 12 `P_bend`: matches key; 835.0 N checkpoint hit (recomputed 835.0).
- Cell 14 `P_sep`: matches key; 2893.9 N checkpoint hit (recomputed 2893.9).
- Cell 22 loss fill-in: MSLE identical to key (omits the cosmetic `float()`
  cast, as both precedent submissions did). Calibration lands exactly on
  checkpoint: σ_y = 66.8 MPa, k = 0.377, τᵢ = 16.76 MPa, MAPE 5.3%
  (independent rerun: 66.828 MPa, 0.3766, 16.760 MPa, 5.33%).
- Cell 25 objective fill-in: matches key; equation design checkpoint exact
  (b = 1.10, H_web = 13.25, 48.7 N/g; capacities 621/623/618 N — recomputed
  620.7 / 622.9 / 617.9).
- Cell 20 hand-tune playground left at defaults (MAPE 20.9% = nominal) — same
  as the shipped key and both precedents; an "edit" cell, not a fill-in; no
  deduction, but no artifact of hand-tuning exploration survives.
- The key's "KEY-only" LTB comparison cell is correctly absent.
- Integrity: grepped the full notebook (cell sources and outputs) for every
  faculty/GT-only value (65.242, 0.4245, 21.056, 42.13, 38.74, 525.6, the
  1.39/12.08 GT optimum, 475.7, 37.48). Zero hits in text; raw-JSON hits were
  base64 image bytes. Clean. See the Q2 note on the "23% shortfall" reference.

## 2. Claim verification

| # | Memo claim | Verdict |
|---|---|---|
| Q1 | Deltas run −2.8% (beam 13) to +1.5% (beams 1 and 4), band ≈ 4 points, no sign pattern in b or H | CONFIRMED (recomputed −2.769% beam 13; +1.504% beam 1, +1.463% beam 4 — both round to +1.5; span 4.27 pts; corr with b = +0.09, with H = −0.10) |
| Q2 | Capacities at optimum: LTB 617.9 / bend 620.7 / sep 622.9 N; spread lowest→highest 0.8% | CONFIRMED exact to 0.1 N (recomputed 617.9 / 620.7 / 622.9; spread 0.81%). Quoted to more precision than the notebook's own rounded printout, and correctly |
| Q2 | `gov_mode` tie-break rule quoted as `Pl < 0.999*Pb` | CONFIRMED against the code |
| Q2 | "The 23% shortfall the ground truth model returned there" | CONFIRMED numerically (frozen GT at (1.10, 13.25) is 475.7 N vs 617.9 N min-capacity = 23.0% short; 37.48 vs 48.7 N/g = 23.0%). This is Pre-lab 2 information — see §4 |
| Q3 | σ_y 76→66.8 is a 12% reduction; moves "all eleven bend-governed beams together," residuals +4%..+26% nominal → −8%..+11% calibrated | CONFIRMED (12.1%; 11 calibrated-bend beams; nominal +4.1..+25.8, calibrated −8.4..+10.6). "No residual pattern in geometry left over" is looser: corr(res, b) = −0.47 across the 11, driven by beams 1 (−8.4%) and 7 (+10.6%) — weak, not significant at n = 11, so not contradicted |
| Q3 | τᵢ 16.8 MPa = 38% of the 43.9 MPa bulk guess | CONFIRMED (38.2%) |
| Q3 | Beams 12/14/15 are the three worst nominal residuals (+36.0/+39.5/+61.0%), calibrated to −18.7/+7.7/+14.3%, and only labeled `separation` after calibration | CONFIRMED (all six residuals exact; mode switch confirmed) |
| Q3 | "At the bulk guess the separation branch never governed anywhere in the box" | CONFIRMED exactly — swept the full 0.05 mm grid (26,741 points): zero separation-governed points at nominal parameters. A strong claim, and it is literally true |
| Q3 | Beam 9 is the only LTB-governed beam; calibrated residual 0.0% is "an identity," not validation | CONFIRMED (only LTB label at both parameter sets; recomputed residual 0.00%) |
| Q3 | "M_cr scales as 1/k²" | LOOSE. That is the prefactor only; the Lb² term inside the radical softens it. Recomputed local sensitivity at the optimum geometry: d ln P_LTB / d ln k = −1.57 at k = 0.377. Right direction, overstated by ~30%; the qualitative point (one-point fit steers the class design) stands |
| Q4 | Beam 15 (1.00, 12.50) 34.41 N/g, two failed interfaces; beam 14 (1.40, 10.40) 35.35 N/g, 0.3 mm of web from the optimum; beam 9 (1.75, 15.80) 30.96 N/g; beam 12 −18.7% conservative | CONFIRMED (geometry, s/w values, note paraphrases, and residual all exact) |
| Q4 | Beam 9 has "the lowest strength-to-weight of any thin beam in the set" | **CONTRADICTED**: beam 12 (b = 1.50) is lower at 28.10 N/g vs beam 9's 30.96 — and the memo itself treats beam 12 as part of the thin set two sentences later |
| Q4 | "No thin-b beam exceeds 35.4 N/g" | CONFIRMED (max is beam 14 at 35.35) |
| Q5 | "Beams 6 and 13 both traces end in a single near-vertical drop from peak"; beam 14 "sheds load over a longer displacement: the flange peels progressively"; beam 9 "comes down without a cliff" | **CONTRADICTED** for beams 13 and 14, partially for 9. Recomputed from the raw traces: beam 14 is the sharpest cliff in the set (654.6 N → 24% of peak within 0.04 mm); beam 13 sheds gradually (above 95% of peak for 2.09 mm past the peak, 5.47 mm to reach 25%); beam 9 does roll over gradually (98% at +0.2 mm, 84% at +1.0 mm) but then ends in a sharp terminal drop at +1.30 mm — not "without a cliff." Beam 6 is right in substance (near-peak for 0.84 mm, then collapse within ~0.09 mm), though "from peak" misses the delay |

## 3. Memo answers vs key targets

**Q1 — mass denominator.** Meets the key, above it in specificity: correct
extreme-delta attribution (unlike the fable-agent precedent), a print-physics
causal list led by extrusion-width quantization on 1–1.5 mm webs — a
mechanism that matters most exactly where the optimizer wants to go — and the
right two-part defense of estimated mass (defined for un-printed candidates;
keeps print luck out of the ranking).

**Q2 — mode label as proxy.** Above the key. Quantifies the three-way tie to
0.1 N, names the mechanism (argmax of a min lands on surface crossings),
identifies the specific tie-break line of code doing the labeling, and adds
two consequences the key does not ask for: the label carries no information,
and the triple point is the least robust geometry in the box because all
three idealizations are simultaneously marginal. Then connects that
prediction to the GT outcome ("the 23% shortfall… is exactly the behavior a
triple point should produce") — verified exact. Strongest Q2 of the three
submissions reviewed.

**Q3 — calibration interpretation.** Above the key. Explicit position on each
parameter with every cited number verified: σ_y a correction (uniform shift
of the 11 bend beams, verified); τᵢ a measurement of an unlisted property,
backed by the verified structural claim that at the bulk guess the separation
branch governed *nowhere* in the design box, so the model "was structurally
incapable of predicting the one mechanism that three of fifteen beams
actually exhibited" — the sharpest formulation of the τᵢ point in any
submission so far. For k, refuses the binary ("neither, and this is the
parameter to distrust") and lands the one-point-identifiability observation
(beam 9's 0.0% residual "is not a validation, it is an identity") that the
fable-agent precedent was credited for exceeding the key with. Blemish: the
1/k² scaling is loose (true local exponent −1.57).

**Q4 — validity limits at the thin-b edge.** Meets the key and pushes past it:
beam 15's double-interface note read as a structural gap (single-plane,
single-τᵢ model "has no way to represent a beam losing both junctions"),
beam 14 placed 0.3 mm of web from the optimum, beam 12's −18.7% used to argue
τᵢ is "not even a stable constant across the box," and the closing framing —
"the neighborhood is not merely unexplored, it is explored and unfavorable:
no thin-b beam exceeds 35.4 N/g, while the model predicts 48.7 N/g there" —
is the cleanest statement of the extrapolation problem in the three
submissions. One factual slip (beam 9 as lowest thin-beam s/w; beam 12 is).

**Q5 — trace shapes and beam 9.** Split verdict, same failure as the
sol-agent precedent. The beam-9 *call* is strong and above key: predominantly
a fixture/stability artifact, with the three concrete consequences —
its 0.0% residual is not evidence the LTB model works, the fitted k does not
transfer to a different fixture, and a surrogate trained on `strength_N`
reads "this geometry is weak" where the truth is "this geometry is unstable
on this stand," which imply different design responses. That last distinction
(avoid the region vs brace the flange) goes beyond the key's target. But the
trace-shape reading the answer opens with is wrong for two of the four beams
and partially wrong for a third (see table): it pattern-matches the failure
notes (fracture → cliff) instead of reading the curves plotted directly above
in cell 5's own output, and so inverts beams 13 and 14 and misses beam 9's
terminal drop. The inversion loses the load-bearing observation the fixed key
now names: the *interface separation* is the catastrophic-abrupt event in
this dataset — precisely the behavior that should sharpen the Q4 distrust of
the thin-b separation neighborhood this same memo argues so well.

## 4. Errors, misconceptions, standout insights

Errors:

- Q5 trace-shape characterization contradicted by the raw data for beams 13
  and 14, partially for beam 9 (details in the table). **Maximal mitigation
  applies**: this student worked from the pre-`b391ee9` template, whose given
  prose asserted "the cliff beams are the ones whose notes say *fracture*"
  and whose Q5 prompt presupposed a cliff/gradual = fracture/other dichotomy;
  the commit message for the fix records that this exact priming produced
  this exact error in agent dry-runs. The plots were nonetheless in the
  submitted output, and the sol-agent precedent was deducted for the same
  error under the same template.
- Q4: "beam 9 [has] the lowest strength-to-weight of any thin beam" — beam 12
  is lower (28.10 vs 30.96 N/g). Comparable in severity to the fable-agent
  precedent's beam-ID mix-up; touches no conclusion (beam 12 being *worse*
  only strengthens the thin-b distrust argument).
- "M_cr scales as 1/k²" overstates the sensitivity (local exponent −1.57 at
  the calibrated point). Trivial; direction and consequence correct.

Minor omission vs the rubric's fragility list: knife-edge/support-contact
physics (web crippling, nose contact) is never named in the memo — the same
omission as both precedents; fixture assumptions and the thin-web frontier
are covered thoroughly.

Notes for staff, bearing on material graded elsewhere:

- The Q2 reference to "the 23% shortfall the ground truth model returned" is
  Pre-lab 2 information used in a Pre-lab 1 memo. It is numerically exact
  (verified: 475.7 vs 617.9 N, and 37.48 vs 48.7 N/g, both 23.0%) and
  *legitimate at turn-in time* — the pre-lab is submitted alongside
  Submission 1, after the class query returns — but it means the memo was
  written or revised with downstream knowledge. No faculty-only values appear
  anywhere in the notebook. Card rows 2 and 6 (graded separately) should
  find ready material here: the triple-point fragility argument, the
  k-identifiability caveat, and the explored-and-unfavorable thin-b framing
  are exactly what those rows want. (For the record: nothing in this
  submission echoes KEY-only content — the τᵢ-drift point is derived from
  beam 12's residual, not the faculty 15–21 MPa back-calculation.)

Standout insights: the verified nowhere-in-the-box separation claim and the
"structurally incapable" framing of the uncalibrated model; the residual-as-
identity treatment of beam 9's 0.0%; the triple-point robustness argument
with its confirmed 23% prediction; the two-readings distinction ("weak" vs
"unstable on this stand") and the different designs each implies; Q2's
capacities quoted to 0.1 N, more precisely than the notebook's own printout
and correctly.

## 5. Assessment: STRONG-PLUS (18/20)

All fill-ins run and hit every checkpoint exactly; the notebook is clean of
faculty-only numbers; and Q1–Q4 sit *above* the rubric's strong band, with
every cited residual, capacity, mass delta, and geometry independently
verified — including two non-obvious structural claims (separation governs
nowhere at the bulk guess; the 23% GT shortfall) that checked out exactly.
The deduction is the Q5 trace-shape inversion (beams 13/14 backwards, beam
9's terminal drop missed) on a rubric-named requirement — held to one point
rather than the sol-agent's two because the priming here is documented as a
template defect this student's given text actively asserted, and because the
rest of the memo is above-key where that precedent was at-key. **18/20** —
checkpoint-perfect execution and the strongest calibration/validity memo of
the three reviewed, held back by reading the traces off the failure notes
instead of off the data.
