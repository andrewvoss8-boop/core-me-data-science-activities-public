# Lessons

- Generated notebook edits are not durable unless the same change is made in `../ibeam150_analysis/run13_build_student_notebooks.py`.
- For generated instructional notebooks, compact question-specific figures and a single explicit legend are easier to read than repeated five- or six-map grids.
- In the Voss beam workbook, the `USE THIS TAB` header row overwrote beam 0's H, h, B; restore from `ALL IBEAMS WITH COLOR CHANGE` (19.447, 2.776, 8.454).
- Rectangle replicate groups A/B (Bambu, 2 walls) and EI #1/#2 (SunLu, 5 walls) differ in material and walls, not just infill; label them by walls or students read a false infill effect.
- Direct notebook reuse with `%run` prevents Submission 2 from drifting away from the model students actually completed in Submission 1; the two files must remain together or the path must be updated.
