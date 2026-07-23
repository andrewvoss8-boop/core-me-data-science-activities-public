# Example student submissions (agent-generated, agent-graded)

Worked examples of complete ME 323 Module 1 submissions, graded against
`Module1_drafts/ME323_Module1_Rubric.md`, with each committed design scored on
the frozen synthetic ground-truth model (`gpr_str_matern_cal`, 85 tests).

**Provenance disclosure:** neither role here was a human. The "student" work
was produced by a Claude Fable 5 agent working through the student-facing
notebooks under module conditions (student handout data only, no access to
faculty/GT materials); the grading, rubric scoring, and GT evaluation were
performed by a separate Claude Fable 5 agent session. These are dry-run
artifacts for calibrating the rubric, the decision card, and the grading
workload before live deployment — not records of real student work.

## Layout

Each `studentN_fable-agent/` folder contains:

- `submission/` — exactly what a group would turn in at the Submission-1
  stage: the filled decision card (with preregistration table), the two
  completed pre-lab notebooks, the completed Submission 1 design notebook,
  and the knob-sweep CSV.
- `grading/` — the grader's outputs:
  - `GRADE_REPORT.md` — dimension scores against the rubric and the overall
    stage grade.
  - `grader_comments_prelab1.md` / `_prelab2.md` / `_submission1.md` —
    detailed per-artifact reviews, including independent recomputation of the
    submission's numerical claims.
  - `gt_design_evaluation.md` — the committed design scored on the frozen
    ground-truth model, plus the rivals the card named.
  - `gt_eval_script.py` — the script that produced those numbers (staff-only
    in spirit: it rebuilds the GT model from the full campaign pool).

## Example index

| Folder | Design (b, H_web) | Predicted | GT result | Stage grade |
|---|---|---|---|---|
| `student1_fable-agent/` | (1.39, 13.20) | 36.65 N/g (497 N), z=2 [461, 536] N | **38.74 N/g = 525.6 N** (in interval, +1.5σ) | 96% (77/80) |

Note: `grading/` contents reference frozen GT numbers and the full-campaign
model. Like `Module1_drafts/ground_truth.py`, they must not be distributed to
students before the module runs.
