# ME 323 Module 1 — Build & Test Lab (student-run) — SPEC DRAFT

Students print, test, and interpret their own beams. The Purdue team provides
the facility-specific guidance (printer fleet, slicer profiles, test frame,
scheduling); this document fixes what the module needs from that lab so the
modeling chain and the physical chain stay one activity. Items marked
**[PURDUE]** need the Purdue team's local detail before go-live.

**Window:** at least 4 weeks, interleaved with other lab activities. The
modeling notebooks (Pre-labs, Submission 1) run in parallel during the first
half; the group's beam must be printed and tested before Submission 2 opens.

## What each group does, in order

1. **CAD + slice.** Generate the I-beam solid at the group's committed
   `(b, H_web)` from the class template (flange width 10 mm, total height
   18 mm, printed length 172 mm), slice with the class profile, and record the
   slicer's mass estimate next to the notebook's `mass_est_g`. **[PURDUE]**
   template file, slicer, profile name, material lot policy.
2. **Print.** Same printer family, orientation, and settings as the campaign
   beams — the calibrated τᵢ is a printed-interface property and moves with
   print conditions; an uncontrolled print invalidates the comparison, and the
   memo should say so if it happens. **[PURDUE]** printer assignments, queue,
   reprint policy for failed prints.
3. **Weigh and measure.** Measured mass to 0.1 g; measured `b` and `H_web`
   with calipers at three stations along the span. Enter both next to the
   nominal values; the memo uses the gap between nominal and printed.
4. **Preregister.** The decision card's preregistration table
   (`ME323_Module1_DecisionCard.md`) is filed *before* the test slot. No
   preregistration, no test.
5. **Test.** Three-point bend at 150 mm span on the class fixture, proper
   supports, group present. One member runs the machine per local training
   rules, one photographs, one takes the failure note in their own words at
   the machine (the campaign notes were written the same way, misspellings
   and all). **[PURDUE]** frame, load cell, crosshead rate, safety training
   prerequisite, shielding.
6. **Reduce the raw trace.** Each group receives its own force–displacement
   CSV and reduces it to peak load themselves — the same reduction they
   practiced on four campaign traces in Pre-lab 1 — and decides whether the
   peak is a material strength or a fixture/stability artifact before entering
   it in Submission 2.
7. **Document.** Photo set per beam (see shot list), trace CSV, failure note,
   measured masses and dimensions — one folder per group, filed the day of the
   test. Submission 2's reflection cannot run without it.

## Contingency

- **Failed print:** reprint within the window under the reprint policy; if the
  queue cannot absorb it, staff print the group's committed geometry — the
  group still tests, reduces, and documents. The design decision was already
  graded at Submission 1 either way.
- **Failed or invalid test** (beam slips, early stop, fixture problem): the
  trace and photos still get filed and the group writes the failure note on
  what happened; staff schedule one retest if machine time allows. The memo treats a
  censored test the way the module teaches: the load reached is a lower
  bound, not a missing value.
- **Absent member on test day:** the test runs; individual grades follow the
  rubric's individual components, not test-day attendance.

## Photo shot list (staff once, then every group's beam)

Course-wide shots the module's slides and notebooks currently lack, in
priority order — these replace placeholder graphics, so frame them for
projection:

1. The fixture, annotated: span, loading nose, support geometry, print
   orientation, and the unbraced length the LTB branch assumes.
2. One clean example of each failure family on current geometry: vertical
   fracture (complete and partial), flange–web separation along the layer
   line, and LTB twist — same camera angle, same scale.
3. A force–displacement trace printed side by side with the photo of the same
   broken beam, one abrupt-fracture pair and one gradual pair.

Per-group, on test day: beam on the scale (mass legible), beam in the fixture
before load, the broken beam from the side and from the fracture face.

## Roles and budget assumptions **[PURDUE]**

Group size, number of groups, printer-hours per beam, expected print failure
rate, spare filament, TA/UG hours for machine supervision. The staffing model
assumes undergraduates supervise printing and testing sessions; students do
the work.
