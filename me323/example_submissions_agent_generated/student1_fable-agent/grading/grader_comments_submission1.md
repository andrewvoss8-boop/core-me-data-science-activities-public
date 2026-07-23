# Grader comments — Submission 1 (Design) + decision card + knob sweep

Dimension: **Synthesis and the design decision** (25%) plus verification of
every numerical claim on the decision card. Reviewed by a Claude Fable 5
grader agent against `ME323_Module1_Submission1_Design_KEY.ipynb` and the
faculty knob sweep (`submission1_knob_sweep.csv`,
`ME323_Module1_Submission1_KnobSweep_FACULTY.ipynb`). Claims marked "rerun"
were independently recomputed by the grader from the student-facing data.

## 1. Card-claim verification table

| # | Card claim | Status |
|---|---|---|
| 1 | Pick (1.39, 13.20), mass 13.55 g, lane A RBF 3% MUI ψ=0.5 + veto b≥1.29, H≤14.5 | CONFIRMED (notebook cells 8, 12, 14) |
| 2 | Median 36.65 N/g (497 N), σ_epi 0.023, σ_total 0.038, z=2 [461, 536] N | CONFIRMED (cell 14 + rerun: 36.65, 0.0231, 0.0379, [461, 536]) |
| 3 | Unconstrained acquisition lands at (1.00, 13.20) | CONFIRMED (cell 12 output) |
| 4a | Lane D LOO 2.34 vs lane A 2.89 N/g | CONFIRMED (cell 6, matches template checkpoint) |
| 4b | Lane D recommends (1.39, 11.71) at ~42.5 N/g | CONFIRMED (sweep CSV: top pick in 29/40 D-runs; rerun μ = 42.47) |
| 4c | Lane A predicts 33.0 N/g there; "25%" disagreement | CONFIRMED by rerun (33.05; 22–28% depending on base) — not printed in any cell |
| 5a | Corrections 0.77–0.79 (beams 16, 17), 0.93 (beam 14) | CONFIRMED by rerun (0.771, 0.786, 0.928; memo's beam-15 0.88 = 0.875) |
| 5b | Lane D fitted H length scale ~0.5 mm | **CONTRADICTED**: rerun gives lane D (b = 1.70, H = 0.99 mm); 0.48 mm is **lane A's** H length scale — mis-attributed. Lane A b ≈ 3.4 mm claim ≈ confirmed (3.57) |
| 6 | Physics at pick: 635 N bend, LTB tie 0.1%, sep 797 N (+26%) | CONFIRMED (cell 14; rerun 635.2 / 797.2 / 634.8, tie 0.06%, +25.5%) |
| 7 | Veto sensitivity: both kernels, 1–10% noise stay in (1.29–1.39, 13.2–14.0); C and D converge at 10% | CONFIRMED by rerun (see §2 caveat) — not computed in the submitted notebook |
| 8 | Lanes C, D at pick: 37.58, 37.40 N/g | CONFIRMED exactly by rerun |
| 9 | Beam 16 37.48 @ 0.29 mm; beam 17 36.65 @ 0.43 mm; beam 15 34.41 @ 0.80 mm | CONFIRMED by rerun (all exact) |

## 2. Computed vs asserted

Computed in the notebook: unconstrained argmax, veto + constrained argmax at
the chosen knobs, committed-design block (median, sigmas, interval, physics
modes), LOO table, and the full 160-run unconstrained sweep with CSV export
and scatter plot (cells 12, 14, 17).

Asserted in the memo, not in any cell: the constrained sensitivity at other
kernel/noise settings (memo prompt 5 tells students to rerun by hand, so no
cell is expected), the lane cross-predictions, correction factors, and length
scales. Every asserted number except the lane-D length scale was reproduced
exactly by the grader — including the non-obvious (1.29, 13.95) pick at 4.4%
noise with RBF — so the reruns were genuinely performed.

Caveat on claim 7: (1.29, 13.95) is 4 grid notches (0.75 mm) from 13.20, so
the memo's "moves only one grid notch" overstates stability slightly; the
stated 13.2–14.0 band does hold. The lane-D length-scale mis-attribution (5b)
weakens — but does not break — the extrapolation argument in card row 9: at
the true D length scale of ~1.0 mm, beam 14's mild correction still cannot
comfortably anchor a point ~1.3–1.5 mm away in H.

## 3. Memo quality

- **Three figures named:** yes (memo section 6) — the LOO table, the
  four-panel decision map, and the sweep scatter, each with one sentence on
  the work it does. Quibbles: the LOO table is a table, not a figure, and
  "section 13" is a numbering quirk.
- **Risk posture before the pick:** yes — stated inline at the acquisition
  knob ("one print, incumbent 37.48 N/g already on the board; mostly exploit,
  half a sigma of benefit of the doubt") and the veto rationale precedes the
  constrained pick.
- **Rejected alternative:** very credible — the LOO winner's own pick,
  rejected with four quantified reasons; the 734/734 knife edge and the 0.936
  correction at that point both check out.
- **Synthesis at the candidate:** physics (46.8 N/g) and GP (36.65) side by
  side, disagreement explained by a measured local bias, explicit refusal to
  average: "We do not average the two numbers; we take the GP's, because it
  already carries the measured correction." Falsifier row is concrete and
  two-sided.

## 4. Copying check: clean

Student sweep uses noise grid {1, 3, 4.4, 10} vs faculty {1, 3, 5, 10} — the
4.4 comes from the student-facing template, and the 4.4% rows have no faculty
counterpart. The student CSV carries full float precision where the faculty's
is rounded, and lacks all faculty-only columns (phys_mode, gt_strength_N,
gt_sw, gt_gap). No GT-only numbers appear anywhere in the student files.
Matching picks on the 120 shared knob combos are expected from the
deterministic pipeline (random_state = 0) and confirm correct execution, not
copying. Trivial inconsistency: the notebook writes a column named `dial`
where the submitted CSV header says `psi`; contents identical.

## 5. Assessment: EXCELLENT (24/25)

Everything the strong-band rubric asks, done with numbers that survive
independent recomputation. The only substantive defect is the lane-D H
length-scale mis-attribution, plus the mild "one grid notch" overstatement;
both weaken supporting details without breaking the arguments they serve.
