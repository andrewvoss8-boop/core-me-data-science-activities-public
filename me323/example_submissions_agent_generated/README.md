# Example student submissions (agent-generated, agent-graded)

Worked examples of complete ME 323 Module 1 submissions, graded against
`Module1_drafts/ME323_Module1_Rubric.md`, with each committed design scored on
the frozen synthetic ground-truth model (`gpr_str_matern_cal`, 85 tests).

**Provenance disclosure:** no role here was a human, and the folder name
records which model played the student. `student1_fable-agent/`'s "student"
work was produced by a Claude Fable 5 agent; `student2_sol-agent/`'s by a Sol
agent — each working through the student-facing notebooks under module
conditions (student handout data only, no access to faculty/GT materials).
The grading, rubric scoring, and GT evaluation of every submission were
performed by a separate Claude Fable 5 grader-agent session. These are
dry-run artifacts for calibrating the rubric, the decision card, and the
grading workload before live deployment — not records of real student work.

## Layout

Each `studentN_<model>-agent/` folder contains:

- `submission/` — exactly what a group would turn in at the Submission-1
  stage: the filled decision card (with preregistration table), the two
  completed pre-lab notebooks, the completed Submission 1 design notebook,
  and the knob-sweep CSV. (student2's package also shipped a short README,
  kept here; its HTML notebook exports and local copies of the issued data
  CSVs are omitted as redundant.)
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
| `student2_sol-agent/` | (1.10, 13.25) — deliberate replicate of the class equation-query beam | 36.75 N/g (467 N), z=2 [433, 502] N | **37.48 N/g = 475.7 N** (in interval, +0.5σ; equals the incumbent by construction) | 89% (71/80) |

The two examples make a useful contrast for grader calibration: student1
exploits one step beyond the data (and its rejected rival turned out better
on GT); student2 replicates the incumbent exactly, arguing for morphology and
repeatability evidence (and its rejected explore rival turned out much worse,
GT 33.07 N/g).

Note: `grading/` contents reference frozen GT numbers and the full-campaign
model. Like `Module1_drafts/ground_truth.py`, they must not be distributed to
students before the module runs.
