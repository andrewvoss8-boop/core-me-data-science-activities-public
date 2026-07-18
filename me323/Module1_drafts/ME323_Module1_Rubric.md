# ME 323 Module 1 — Grading Rubric (DRAFT)

Two submissions. The memos carry the grade; the notebooks are checked for correctness and for the required code. Weights are a starting point for the team to adjust.

**Memo format:** each memo is written in markdown cells at the end of its submission notebook, answering the numbered prompts in order. Submission 1's memo ≈ half a page; Submission 2's memo is the module's primary assessed artifact, 400–800 words. No separate document.

Suggested split: **Submission 1 = 65%, Submission 2 = 35%** of the module grade.

---

## Submission 1 — Design, rationale, and notebooks (65%)

Turned in before printing. Includes the beam spec, a memo, and the three notebooks (Pre-lab 1, Pre-lab 2, and the design notebook).

| Criterion | Weight | What full marks looks like |
|---|---|---|
| **Data processing** | 10% | Strength and strength-to-weight are computed correctly. Measured mass and estimated nominal-geometry mass are both retained, named, and not mixed silently. Failure notes and units are handled correctly. |
| **Failure-mode work** | 15% | Flexural yield, the junction shear-flow separation check (calibrated τᵢ), and LTB are interpreted correctly. The student treats the dominant-mode output as a proxy, checks it against failure notes (including the near-tie at the equation optimum), identifies at least one disagreement, and takes a position on whether each calibrated parameter (σ_y, k, τᵢ) is a correction to a handbook number or the measurement of an unlisted property. |
| **GP and acquisition** | 15% | A GP is fit; posterior median, epistemic uncertainty, aleatory noise, and total predictive uncertainty are distinguished. MUI and EI are implemented. Kernel and noise choices are stated as assumptions, not defaults. The student explains why acquisition uses epistemic sigma. |
| **Use of the two ground-truth points** | 10% | The equation design and the GP design were queried, and both results are used in the final decision. Not ignored, not over-weighted. |
| **Design rationale (the memo)** | 30% | A clear case for the chosen beam that combines physics and the GP, names the uncertainty, and takes a defensible position on risk and explore/exploit. States assumptions and what could make the choice wrong. |
| **Code** | 10% | The required code runs and does what the memo claims. Readable. |
| **Communication** | 10% | Figures labeled and used. Memo is organized and concise. A non-expert could follow the decision. |

---

## Submission 2 — Reflection and the lightweight-bending challenge (35%)

Turned in after three weeks of printing and testing. The challenge beam is designed but not tested; the rationale carries the grade.

| Criterion | Weight | What full marks looks like |
|---|---|---|
| **Recall** | 10% | The section-0 answers are from memory, in the student's own words, and mostly right. Corrections after checking are noted honestly; corrections earn credit, bluffing does not. |
| **Reflection on the test** | 35% | Reports measured and estimated mass separately, compares the observed strength to the posterior-predictive interval on a consistent denominator, and compares the observed failure note with the modeled proxy. Explains the gap using print scatter, physics limits, and model-form error without claiming one test identifies the cause. Uses the §3 refit to report what their own result changed — the lightweight design, the best-str/w pick, or neither — and connects the movement (or its absence) to the noise and length-scale assumptions (memo Q7). |
| **The challenge design** | 40% | Gives `(b, H_web)`, estimated mass, posterior median strength, and a lower posterior-predictive bound for one future beam. The `z=2` probability statement is conditional on the Gaussian noise and model assumptions. The design is neither underdesigned nor padded far past the lightest feasible design. The mass-confidence tradeoff, closest-in-mass lighter infeasible point, 1/3/10% noise sensitivity, and physics check are used. |
| **Communication** | 15% | Clear, concise, figures support the argument. |

**Grading the challenge hard, both directions:** a beam expected to fail under `P_TARGET` and a beam padded far past the lightest confident design both signal the same failure — not using the uncertainty. Cap the challenge criterion at half marks for either, regardless of how polished the memo is.

---

## What earns a low grade

- A design defended only by "the optimizer said so," with no uncertainty and no physics check.
- Treating the equation optimum as truth and ignoring where the data contradicts it.
- A reflection that reports the number without explaining the gap.
- A challenge beam expected to fail under `P_TARGET`, or one padded far beyond the lightest confident design. A bare safety factor with no probability behind it counts as the latter.
- Code that does not run or does not match the memo.

## What earns a high grade

- A design that names a risk and chooses anyway, with reasons.
- A student who caught a place the model misled them and said so.
- A reflection that changes the second design in a way the data justifies — the Submission 2 §3 refit is where this shows up concretely.

---

## Notes for graders

- Reward judgment over precision. A well-argued "good enough" beam beats a precise beam with no reasoning.
- The two-query step is identical for everyone (same two beams, same returned values), so do not grade the numbers there, grade what students do with them.
- Expect layer-line fracture in thin-web designs to surprise some groups when they print. A student who predicted it would be surprising should score well on reflection even if the beam underperformed.
