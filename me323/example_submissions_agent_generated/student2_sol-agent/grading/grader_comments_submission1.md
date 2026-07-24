# Grader comments — Submission 1 (Design) + decision card + knob sweep

Dimensions: **Synthesis and the design decision** (25%) and **Preregistration
and experimental plan** (15%), plus verification of every numerical claim on
the decision card. Reviewed by a Claude Fable 5 grader agent against
`ME323_Module1_Submission1_Design_KEY.ipynb` and the faculty knob sweep
(`submission1_knob_sweep.csv`, `ME323_Module1_Submission1_KnobSweep_FACULTY.ipynb`).
Claims marked "rerun" were independently recomputed by the grader from the
student-facing data (`student_beams_B10_L150.csv` + the two class-query rows)
through the notebook's own pipeline.

## 1. Card-claim verification table

| # | Card claim | Status |
|---|---|---|
| 1 | Pick = deliberate replicate (1.10, 13.25), mass 12.694 g, "strongest observed/query design at 475.7 N = 37.47 N/g" | CONFIRMED (cells 12–13; rerun mass 12.6943 g, 37.473 N/g, beam 16 is the max) |
| 2 | Physics 617.0 N (48.60 N/g) LTB; bending 620.7 N, +0.61%; separation 622.9 N | CONFIRMED (cell 13 + rerun: 617.0 / 620.7 / 622.9, margin 0.606%) |
| 3 | GP median 36.75 N/g = 466.6 N | CONFIRMED (cell 13 + rerun: 36.753 N/g, 466.6 N) |
| 4a | LOO: lane A Matérn 2.89 vs RBF 2.94; lane D wins globally (2.34/2.38) | CONFIRMED (cell 6, matches template checkpoint; rerun 2.889/2.935 and 2.338/2.379) |
| 4b | Exploit sensitivity band b = 1.00–1.48, H = 13.20–13.39 | CONFIRMED (cell 14 focused stress test: all six A-lane MUI ψ=0 rows land in {1.000–1.484} × {13.203–13.390}) |
| 5 | σ_epi 0.0217, σ_total 0.0370, z=2 interval 34.13–39.58 N/g = 433–502 N | CONFIRMED (cell 13 + rerun: 0.0217, 0.0370, [433.3, 502.4] N) |
| 6 | Beam 16 475.7 N / 37.47; beam 17 (1.00, 13.39) 445.8 N / 36.64; beam 15 (1.00, 12.50) 475.0 N / 34.41 + quoted morphology | CONFIRMED (cell 13 nearest-support table + rerun, all exact; morphology quote matches the data file verbatim) |
| 7 | Disagreement 48.60 vs 36.75 vs observed 37.47; three branches within ~1% | CONFIRMED (cells 12–13 + rerun; full spread LTB→sep is 0.96%) |
| 8 | MUI ψ=0 unconstrained pick at (1.00, 13.20) | CONFIRMED (cell 12 output; rerun argmax (1.000, 13.203)) |
| 9 | Rejected alternative (1.39, 14.88): lane-A Matérn median ~35.77 N/g, σ_epi ~0.0507; closest physical warning is beam 9 (twist-off) | CONFIRMED by rerun (35.766 / 0.0507 at the exact point; beam 9 is the nearest tested beam in standardized coordinates) — not printed in any cell |
| — | Scoreboard inputs: equation beam "predicted 48.7, returned 37.48, 23.0% shortfall"; locked GP "predicted 36.7, returned 36.65" | NOT CHECKED (staff-supplied scoreboard values, not derivable from student data) — but consistent with rerun: own-calibration physics gives 48.60 at the geometry, and (48.60−37.47)/48.60 = 22.9% |

No claim was contradicted. The card's 37.47/36.64 versus the memo's
37.48/36.65 is a denominator-source difference (own mass model vs the
class-official figures), not an error; both are stated on estimated mass.

## 2. Computed vs asserted

Computed in the notebook: the LOO table (cell 6), the posterior/uncertainty
maps and four-panel decision map (cells 8, 10), the unconstrained argmax, the
veto and the replicate's summary numbers (cell 12), the full decision-card
block at the exact submitted geometry — mass, three mode capacities with
margin, median, both sigmas, the z=2 interval, and the nearest-support table
(cell 13) — and a from-scratch 72-row knob sweep with CSV export, scatter
plot, and a focused A-lane exploit stress test (cell 14).

Asserted in the memo/card, not in any cell: the rejected alternative's
lane-A Matérn median and sigma (the sweep's (1.387, 14.881) row is the RBF
ψ=1 fit at 35.898/0.0502, not the Matérn evaluation the card quotes), and the
beam-9-is-nearest claim. Both were reproduced exactly by the grader (35.766,
0.0507; beam 9 nearest), so the evaluations were genuinely performed even
though the notebook does not show them. The 48.7 and 36.7 scoreboard
predictions are staff-supplied and were taken on faith, correctly labeled.

One precision slip: card row 4 says lane D's physics structure "overpredicted
this mode-boundary region by 23%." The 23% is the shortfall on the
*predicted* denominator (memo section 1 states this correctly); as an
overprediction on the observed value it is 29.7%. Given that memo prompt 1
explicitly asks for stated denominators, the card's verb choice is a real,
if small, imprecision.

## 3. Memo quality

- **Three figures named:** yes (memo section 6) — the section-3
  posterior/uncertainty maps, the four-panel decision map, and the sweep
  scatter, each with one sentence on its work. All three are actual figures;
  no quibbles this time.
- **Risk posture before the pick:** yes — ψ=0 is declared and glossed ("pure
  exploit; uncertainty receives no upside bonus") in the acquisition cell
  itself, and the veto rationale is written into cell 12 *above* the final
  design printout. Card row 8 restates it cleanly.
- **Synthesis at the candidate:** physics (48.60 N/g) and GP (36.75) side by
  side with the observed query (37.47) as tiebreaker; the disagreement is
  explained by the 0.61% three-mode knife edge plus mechanisms the scalar
  model cannot represent. No averaging — the GP number is taken, with the
  local observation as the stated grounds.
- **Rejected alternative:** credible — it is the class-default recipe's own
  pick, rejected with three quantified reasons (lower median, double the
  sigma, beam-9 twist-off adjacency), all verified. One blur: the card calls
  it "the default uncertainty-seeking interior candidate" without noting it
  is generated by MUI ψ=1 under *RBF*; under the student's own Matérn kernel,
  ψ=1 stays on the ridge (their own sweep shows this). That fact would have
  *strengthened* their case, and its absence slightly muddies whose rule
  produced the alternative.
- **The replication decision itself:** defensible and genuinely argued, not
  asserted. The template blesses a near-replicate exactly when the memo says
  what the print buys; this memo prices it twice over — repeatability of a
  best-in-class result under 3–4% scatter, and a failure morphology the
  staff query deliberately withheld — and the preregistered morphology row
  shows the mechanism question is real, not decorative. The expected-value
  cost of the veto is essentially zero (raw exploit argmax 36.74 N/g at
  (1.00, 13.20) vs 36.75 at the replicate), though the memo leaves that
  near-tie implicit rather than stating it as the clincher it is. The honest
  caveat the memo does not make: one replicate cannot strongly establish
  repeatability at n=1 — it can falsify a gross outlier and it does buy the
  morphology, which is what the falsifier row actually leans on.

**Decisive question 1 (why this beam vs next-best):** answered, on record and
quantified — the replicate beats the alternative on median (36.75 vs 35.77),
on epistemic sigma (0.0217 vs 0.0507), and on adjacent physical evidence
(beams 15/17 vs beam 9's twist-off), and it uniquely supplies the missing
morphology observation.

**Decisive question 2 (what evidence would have changed the choice before
printing):** answerable from the record, mostly explicitly — memo section 5
states the choice was conditioned on the A-lane exploit neighborhood
surviving the kernel/noise sweep ("If your recommendation holds only under
your exact settings…" is engaged directly), and the replicate's rationale
rests on beam 16's morphology being unavailable, so a supplied failure note
would have removed half the print's value. What is not said: what would have
made them trust lane D's higher extrapolation. This is the memo's one
genuinely thin spot, though the 23%-miss argument implies the answer.

## 4. Copying check: clean

The student sweep is structurally independent of the faculty CSV: 72 rows on
noise {1, 3, 10} with dial values {0, 1} and an EI row, versus the faculty's
{1, 3, 5, 10} with ψ ∈ {0, 0.5, 1, 2}; no 5% rows exist to have been copied
(the student skipped the template's optional 4.4% as well — their grid
follows memo prompt 5's "1% and 10%" instruction, and the sweep section
explicitly provides no template). Column schema differs throughout
(`acquisition`/`dial`/`b`/`H_web` at full float precision vs the faculty's
`rule`/`b_mm`/`H_web_mm` rounded), the notebook's column names match the
submitted CSV exactly, and all four faculty-only columns (`phys_mode`,
`gt_strength_N`, `gt_sw`, `gt_gap`) are absent. Picks agree with the faculty
file on shared knob combos, as the deterministic pipeline (random_state = 0)
requires — evidence of correct execution, not copying. No GT-only numbers
(GT calibration values, the GT optimum, 38.74 / 525.6 N) appear anywhere in
the package; the only greps that fire are load samples inside the raw traces
file, which is byte-identical to the issued student data.

## 5. Assessment and recommended scores

Everything asserted survives independent recomputation — zero contradicted
claims, a genuinely executed from-scratch sweep, and a replicate defended the
way the template demands rather than sleepwalked into. The defects are small:
the "overpredicted by 23%" denominator slip on card row 4, the blurred
attribution of the rejected alternative's generating rule, the unstated
near-tie that makes the veto free, and a falsifier threshold (430 N) sitting
3 N below the preregistered lower bound (433 N) with no stated reason for
the buffer.

**Synthesis and the design decision: 24/25** — full side-by-side synthesis,
a verified quantified alternative, and a priced replication argument; one
point off for the row-4 denominator slip and the blurred RBF-ψ=1 provenance
of the alternative.

**Preregistration and experimental plan: 14/15** — all four required
elements are sharp and on record, including a morphology prediction that
knowingly contradicts the physics label with reasons; one point off for the
unexplained 430-vs-433 falsifier gap and a falsifier that engages only the
downside of an interval whose upside breach would equally indict the model.
