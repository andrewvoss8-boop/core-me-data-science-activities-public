# Grader comments — Pre-lab 1 (Failure Modes)

Dimension: **Physics model and assumptions** (20%). Reviewed by a Claude
Fable 5 grader agent against `ME323_Module1_Prelab1_FailureModes_KEY.ipynb`
(Jul 21 key; the vossEditjul15 variant is an obsolete earlier flow and was not
used).

## 1. Fill-ins: PASS — all checkpoints hit exactly

- Cell 5 trace reduction (`peak_N` via groupby max): functionally identical to
  the key; checkpoint table matches the handout to 0.1 N (759.0 / 314.4 /
  582.6 / 654.6).
- Cell 12 `P_bend`: matches key; 835.0 N checkpoint hit.
- Cell 14 `P_sep`: matches key; 2893.9 N checkpoint hit.
- Cell 22 loss fill-in: MSLE identical to key (omits a cosmetic `float()`
  cast). Calibration lands exactly on checkpoint: σ_y = 66.8 MPa, k = 0.377,
  τᵢ = 16.76 MPa, MAPE 5.3%.
- Cell 25 objective fill-in: matches key; equation design checkpoint exact
  (b = 1.10, H_web = 13.25, 48.7 N/g; capacities 621/623/618 N).
- Cell 20 hand-tune playground left at defaults — same as the shipped key and
  an "edit" cell, not a fill-in; no deduction, but there is no artifact of
  hand-tuning exploration in the submitted state.
- No code-vs-prose contradictions. Every number cited in the memo was checked
  against actual cell outputs and, for memo 5, against the raw trace CSV.

## 2. Memo answers vs key targets

**Q2 — mode label as proxy.** Nails it, with mechanism: "all three within
about 1%. The proxy label 'LTB' is therefore a coin flip, and this is not an
accident. Maximizing the minimum of several surfaces drives the optimum to
where the surfaces intersect… The label should be read as 'all three
mechanisms are simultaneously active here,' not as a prediction of what the
broken beam will look like." Adds that error in any one calibrated parameter
moves the governing mode. Fully matches the key target.

**Q3 — calibration interpretation.** Explicit position on each parameter with
cited, verified evidence:

- σ_y: "mostly a correction to a number… consistent with printed PLA yielding
  below the bulk datasheet value. Some of the shift may also absorb
  progressive, mixed failure… so it is an effective strength, not a coupon
  measurement." (Cites +4% to +26% over-prediction on bend beams — verified.)
- k: "the measurement of a fixture property no handbook has. Only beam 9 is
  LTB-limited, and after calibration its residual is 0.0%: k is being set by
  essentially one data point… which is exactly why it will not transfer to a
  different fixture." The one-point identifiability observation goes beyond
  the key.
- τᵢ: "the measurement of a property no handbook lists," citing beams
  12/14/15 over-predicted +36/+40/+61% and mislabeled bend at the bulk guess,
  brought to −19/+8/+14% and relabeled separation after calibration (all
  residuals verified: +36.0/+39.5/+61.0 → −18.7/+7.7/+14.3). Closes with
  "one τᵢ cannot capture session-to-session bond variation; the value is a
  campaign average of a drifting property" — consistent with the faculty
  back-calculation (15–21 MPa, CoV ~15%).

**Q4 — validity limits at the thin-b edge.** Cites beam 15's full note (top
separation plus 80% bottom-interface fracture) with the +14% calibrated
over-prediction, beams 14 and 12's separations, beam 9's fixture dependence,
and concludes "the neighborhood of the optimum is precisely where the two
least-trustworthy calibrated parameters (τᵢ and k) govern… The 48.7 N/g
prediction there deserves the widest error bar on the map." Matches and
slightly sharpens the key.

**Q5 — beam-9 call.** Distinguishes trace shapes with quantitative reads all
independently verified against the raw CSV (beam 14 cliff to 24% within
~0.04 mm; beam 6 drop to 25% within 1 mm; beam 13 shedding gradually over
5+ mm; beam 9 rounded peak, 98% at +0.2 mm, 84% at +1.0 mm). The call:
"primarily a fixture/stability artifact, and it is also a genuine measurement
of the beam-plus-fixture system… only a lower bound on what the material could
carry if braced. A model of strength-to-weight on this fixture should keep the
point (the fixture is part of the objective we are optimizing), but it must
carry the caveat that the number is k-dependent: change the fixture and this
data point silently becomes wrong. A model of material capacity should
down-weight or flag it." A defended two-model-purposes answer — above the key.

**Q1 — mass denominator.** Correct on substance ("only denominator defined
for un-printed candidates… using measured mass would reward designs whose
particular print happened to under-extrude"), with one factual slip below.

## 3. Errors, misconceptions, standout insights

Errors:

- Memo answer 1 misattributes beam IDs on the mass-delta extremes: says
  "−2.8% on beam 4 and +1.5% on beam 12"; actual: −2.8% is beam 13, +1.5% is
  beam 1. Magnitudes, mean (−0.1%), and spread (~1.1%) are correct. Sole
  factual error found.
- Minor omission vs the rubric's fragility list: knife-edge/support-contact
  physics is never named (fixture assumptions and the thin-web frontier are
  covered thoroughly).

Standout insights: k identified from essentially one beam and therefore
non-transferable; residual spread across the three separation beams read as
evidence one τᵢ averages a drifting property; the framing that the optimum
sits exactly where the two least-trusted parameters govern; the beam-9
purpose-conditioned treatment. Memo 5's trace numbers were computed from the
data, not eyeballed from plots.

## 4. Assessment: EXCELLENT (19/20)

All fill-ins run and hit every checkpoint exactly; the memo treats the min()
capacity, the mode label, and all three calibrated parameters exactly as the
rubric's strong band demands. The only blemishes are the beam-ID mix-up in the
least important memo answer and the missing knife-edge/contact fragility —
neither touches a load-bearing conclusion.
