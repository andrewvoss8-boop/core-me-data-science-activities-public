# Grader comments — Pre-lab 1 (Failure Modes)

Dimension: **Physics model and assumptions** (20%). Reviewed by a Claude
Fable 5 grader agent against `ME323_Module1_Prelab1_FailureModes_KEY.ipynb`
(Jul 21 key). Every numerical claim below was independently recomputed from
`student_beams_B10_L150.csv` and `student_traces_4beams.csv`, not taken from
the notebook's own printouts.

## 1. Fill-ins: PASS — all checkpoints hit exactly

- Cell 5 trace reduction (`peak_N = tr.groupby("beam_id").force_N.max()`):
  functionally identical to the key; checkpoint table matches the handout to
  0.1 N (759.0 / 314.4 / 582.6 / 654.6 — independently recomputed, exact).
- Cell 8 `str_to_weight`: matches key; checkpoint hit (beam 4 at 36.88 N/g,
  beam 15 at 34.41 N/g — recomputed 36.878 / 34.411).
- Cell 12 `P_bend`: matches key; 835.0 N checkpoint hit (recomputed 835.0).
- Cell 14 `P_sep`: matches key; 2893.9 N checkpoint hit (recomputed 2893.9).
- Cell 22 loss fill-in: MSLE identical to key (omits the cosmetic `float()`
  cast, as the precedent submission did). Calibration lands exactly on
  checkpoint: σ_y = 66.8 MPa, k = 0.377, τᵢ = 16.76 MPa, MAPE 5.3%
  (independent rerun: 66.83 MPa, 0.3766, 16.760 MPa, 5.3%).
- Cell 25 objective fill-in: matches key; equation design checkpoint exact
  (b = 1.10, H_web = 13.25, 48.7 N/g; capacities 621/623/618 N — recomputed
  620.7 / 622.9 / 617.9).
- Cell 20 hand-tune playground left at defaults (MAPE 20.9% = nominal) — same
  as the shipped key and an "edit" cell, not a fill-in; no deduction, but no
  artifact of hand-tuning exploration survives in the submitted state.
- The key's "KEY-only: how the LTB assumptions move the answer" comparison
  cell is faculty content, correctly absent from the submission.
- Integrity: grepped the full notebook for every faculty/GT-only value
  (65.242, 0.4245…, 21.056, 42.1, 38.74, 525.6, 1.39/12.08 optimum). Zero
  hits. Clean.

## 2. Claim verification

| # | Memo claim | Verdict |
|---|---|---|
| Q1 | Mass deltas span −2.8% to +1.5%; beam 13 = 17.8 g vs 18.31 g est (−2.77%); beam 1 = 27.4 g vs 26.99 g (+1.50%) | CONFIRMED (recomputed −2.769% / +1.504%; extremes correctly attributed, unlike the precedent submission) |
| Q2 | Capacities at optimum ≈ 617 / 621 / 623 N (LTB/bend/sep); bend ~0.6% and sep ~1.0% above LTB | CONFIRMED with rounding slack (recomputed 617.9 / 620.7 / 622.9; true margins 0.45% and 0.81%; notebook's own cell 25 prints 618, memo says 617) |
| Q3 | Nominal beam 7 +25.8%, beam 13 +16.9%; calibrated beam 7 +10.6% | CONFIRMED (all exact) |
| Q3 | Beam 9: nominal LTB 392.7 N (+24.9%); calibrated reproduces 314.4 N exactly | CONFIRMED (recomputed 392.7 / +24.9% / 0.0%) |
| Q3 | Beams 12/14/15 mislabeled bend at bulk guess, over-predicted +36.0/+39.5/+61.0%; calibrated → separation branch at −18.7/+7.7/+14.3% | CONFIRMED (all six residuals exact, mode switch confirmed) |
| Q4 | Beam 15 (b=1.0, H=12.5) top-flange separation + 80% bottom-interface fracture; beam 14 (b=1.4) separation; beam 9 (b=1.75, H=15.8) twist-off | CONFIRMED against the CSV notes and geometry |
| Q5 | "Beams 6 and 13 show abrupt post-peak cliffs… Beams 14 and 9 do not show the same clean fracture cliff" | **CONTRADICTED** for beams 13 and 14. Recomputed from the raw traces: beam 14 is the sharpest cliff in the set (654.6 N → 24% of peak within 0.03 mm); beam 13 sheds gradually (still 95% of peak 2 mm past the peak, declining over ~5.5 mm). Beam 6 is a cliff (→25% within 1 mm) and beam 9 is a rounded peak (98% at +0.2 mm, 84% at +1.0 mm) — those two are right |

## 3. Memo answers vs key targets

**Q1 — mass denominator.** Correct on substance (unprinted candidates have no
measured mass; a nominal denominator "prevents the optimizer from rewarding
accidental print-to-print mass variation") and, unlike the precedent
submission, attributes the extreme deltas to the right beams. Meets the key.

**Q2 — mode label as proxy.** Meets the key: quantifies the three-way tie,
names the mechanism ("maximizing the minimum of several capacity surfaces
naturally drives the optimum toward an intersection"), and lands on "a
three-mode knife edge, not a confident prediction that the observed beam must
fail by LTB." Margins slightly overstated (0.6%/1.0% vs true 0.45%/0.81%)
because they were computed from a misquoted 617 N — immaterial.

**Q3 — calibration interpretation.** Explicit position on each parameter, all
cited evidence verified: σ_y "mainly a correction… an effective printed-beam
bending strength" with the honest caveat that beam 7's surviving +10.6%
residual "warns that one effective strength cannot represent every fracture
history"; k "calibration of a fixture-dependent effective length, not
measurement of a material property," with the correct observation that k has
"absorbed the actual support, load-height, imperfection, and twist-off
behavior of this rig"; τᵢ "the closest of the three to measuring a property
that no handbook supplies," closing with "an effective campaign value, not a
universal interface constant" — consistent with the faculty back-calculation
(15–21 MPa, CoV ~15%). Meets the key on all three. Stops short of the
precedent's sharper one-point-identifiability observation for k.

**Q4 — validity limits at the thin-b edge.** Beam 15's full note, beam 14, and
beam 9 correctly deployed as the failures "surrounding" the optimum;
concludes the 48.7 N/g prediction is "much less trustworthy than its
numerical precision suggests." Meets the key. Does not repeat beam 15's +14.3%
calibrated over-prediction here (it appears in Q3) and does not reach the
precedent's framing that the optimum sits where the two least-trusted
parameters govern.

**Q5 — trace shapes and beam 9.** Split verdict. The beam-9 call itself is
strong and defended: "both" — a fixture/stability artifact *and* a valid
system-level capacity, "should not be interpreted as intrinsic PLA strength,"
keep it with a tip/twist label or separate likelihood, "highly informative"
for the LTB/fixture branch and not for σ_y. That matches the key's intent.
But the trace-shape reading that the question opens with is wrong for two of
the four beams (see table): the answer pattern-matches the failure notes
(fracture → cliff) instead of reading the plotted curves sitting directly
above it in cell 5's output. The inversion loses a physically load-bearing
observation: in this dataset the *interface separation* (beam 14) is the
catastrophic-abrupt event and the *partial fracture* (beam 13) sheds load
gradually — exactly the behavior that should sharpen distrust of the thin-b
separation neighborhood argued in Q4.

## 4. Errors, misconceptions, standout insights

Errors:

- Q5 trace-shape characterization contradicted by the raw data for beams 13
  and 14 (details in the table). The rubric's strong band explicitly requires
  reducing and reading the raw traces correctly; the reduction (peaks) is
  correct, the shape-reading is not. Mitigation noted for staff: the
  template's own cell-6 prose ("the cliff beams are the ones whose notes say
  *fracture*") does not match the trace data either and may have primed this
  answer — worth fixing in the template — but the memo question directly asks
  the student to read the shapes, and the plots were in the submitted output.
- Q2 quotes P_LTB as 617 N where the notebook's own cell 25 prints 618 N
  (true value 617.9). Trivial.

Minor omission vs the rubric's fragility list: knife-edge/support-contact
physics (web crippling, nose contact) is never named; fixture assumptions and
the thin-web frontier are covered.

Standout insights: the per-purpose treatment of beam 9 (keep for the
fixture-objective model, down-weight for material capacity); the τᵢ closing
that the fit is "a campaign average" rather than an interface constant; beam
7's surviving residual used to bound what one effective σ_y can represent.

## 5. Assessment: STRONG (17/20)

All fill-ins run and hit every checkpoint exactly, the notebook is clean of
faculty-only numbers, and Q1–Q4 sit solidly in the rubric's strong band with
every cited residual independently verified. The deduction is concentrated in
Q5: a contradicted reading of two of the four raw traces on a rubric-named
requirement (beam 14 is the sharpest cliff, not a gradual failure; beam 13 is
gradual, not a cliff), plus the memo staying at-key rather than above-key
elsewhere. **17/20** — checkpoint-perfect execution and a verified,
well-positioned calibration memo, held back by a data-reading error where the
rubric explicitly demands the traces be read correctly.
