# ME 323 Module 1 — Grading Rubric (DRAFT)

The module grades **the quality of the decision given the information
available**, not the realized strength of one noisy print. A weak decision can
produce a strong beam through luck; a strong decision can meet print
variability or an unmodeled failure. The leaderboard makes the testing day
exciting; this rubric is what carries the grade.

**Memo format:** each memo is written in markdown cells at the end of its
submission notebook, answering only that submission's numbered prompts, in
order. Submission 1's memo covers its prompts in about half a page; Submission
2's memo is the module's primary assessed artifact, 400–800 words. The pre-lab
memo questions are answered in markdown cells at the end of each pre-lab
notebook and are graded there — under the physics and data/ML dimensions below
— not re-answered in the submission memos. Both submissions also file the
decision card (`ME323_Module1_DecisionCard.md`); graders read the card first.

## Group and individual work

- **Group (one per group):** the four notebooks, the decision card and
  preregistration table, the printed beam, the test-day documentation, and
  both memos. The group must agree on one model and one beam — disagreement
  inside the group is memo material ("we rejected X because…"), not a reason
  for parallel submissions.
- **Individual (each student):** Submission 2's §0 recall answers, written
  from memory in the student's own words, and a 3–5 sentence individual
  postscript at the end of the Submission 2 memo: one place you agreed with
  the group's decision and one place you would have decided differently, with
  the evidence you'd cite. Dissent is not penalized; unsupported dissent and
  unsupported agreement are graded the same way.
- **Split:** 85% group, 15% individual (recall 7%, postscript 8%). A student
  who cannot explain the group's own model in the postscript should not
  expect the group score to carry them.

## The five graded dimensions

Weights are module-level. Each dimension names the artifacts where it is
assessed.

| Dimension | Weight | Assessed in | Strong looks like | Weak looks like |
|---|---|---|---|---|
| **Physics model and assumptions** | 20% | Pre-lab 1 + its memo Qs; card rows 2, 5 | Uses the three capacity branches, mode competition, and calibration honestly; treats the dominant-mode label as a proxy; takes a position on whether each fitted parameter (σ_y, k, τᵢ) corrects a handbook number or measures an unlisted property; names where the physics is fragile (knife edges, fixture assumptions, the thin-web frontier). Reduces the raw traces correctly and defends the beam-9 judgment call. | Reports the minimum capacity or the printed mode label as truth; treats calibrated values as material data; no validity limits. |
| **Data/ML model and validation** | 20% | Pre-lab 2 + its memo Qs; Submission 1 §2–3; card rows 3–4 | Distinguishes posterior median, epistemic sigma, aleatory noise, and total predictive uncertainty and uses each for its own job; reads the LOO table as 17-point evidence with a scope (including its stated conditional-on-calibration caveat); checks sensitivity to kernel and noise instead of treating them as facts. | Reports the optimizer output as fact; picks the lowest LOO number with no regional reasoning; defaults everywhere with no sensitivity check. |
| **Synthesis and the design decision** | 25% | Submission 1 §4 + memo; card rows 1, 6–8 | Puts physics and GP predictions side by side *at the candidate*, explains the disagreement or the grounds for trusting the agreement, states the risk posture, compares a credible rejected alternative, and commits. A defended default recipe outscores an arbitrary exotic one. | Selects the largest predicted number; averages the two models without explanation; no alternative considered; risk posture unstated or asserted after the fact. |
| **Preregistration and experimental plan** | 15% | The preregistration table; card row 9 | Sharp, falsifiable predictions filed before printing: load with an interval, a named expected morphology, the assumption most likely to break, and an explicit outcome that would change the next design. | Vague predictions that cannot be proven wrong ("around 500 N", "separation or bending"); falsifier missing or circular; table filed late. |
| **Test interpretation, update, and redesign** | 20% | Submission 2 §1–3 + memo; card row 10 | Compares the result to the *preregistered* interval and morphology; separates print variability, manufacturing deviation, model-form error, and mechanism hypotheses without claiming one test identifies the cause; uses the §3 refit to make a specific, evidence-connected next move — and says so plainly when the honest answer is "one test doesn't distinguish these." | Assigns one cause to every discrepancy; "agreed well" with no comparison; refits automatically and reports a new optimum with no connection to the observation. |

**Communication is graded inside every dimension**, not as its own line: a few
decision-relevant figures with consistent units and denominators, prose a
non-expert could follow. Twenty plots with no evidence chain lose points in the
dimension those plots were supposed to serve. Submission 1's memo names the
**three figures** that carry its argument; graders may ignore the rest.

**Beam performance bonus (up to +3% module grade, group):** strongest tested
str/w in class, or lightest beam clearing 700 N if tested. Bonus only — a
group whose well-reasoned beam breaks early loses nothing here that the
dimensions don't already measure.

**Notebook code** is checked pass/fail within the first two dimensions: the
required fill-ins run and do what the memo claims. Polished code earns nothing
extra; code that contradicts the memo costs the dimension it belongs to.

## Mapping to the two submissions

For gradebook entry, the dimensions land as: **Submission 1 ≈ 60%** (physics
20 + data/ML 20 + synthesis 25, less the card-row-10 share) with the
preregistration table filed alongside it (15%), and **Submission 2 ≈ 25%
group** (interpretation 20 + the synthesis share settled by the lightweight
challenge) **+ 15% individual**. The lightweight-challenge criteria below
grade inside the synthesis and interpretation dimensions.

## The three decisive questions

A grader reads the card and the memo and asks, in order:

1. **Why this beam instead of the next-best alternative?**
2. **What evidence would have changed the choice *before* printing?**
3. **What changed after testing, beyond the dataset gaining one row?**

A submission that cannot answer these is weak regardless of its mathematical
polish or its measured strength. A submission that answers all three crisply
is strong even if its beam underperformed.

## Grading the lightweight challenge hard, both directions

A beam expected to fail under `P_TARGET` and a beam padded far past the
lightest confident design both signal the same failure — not using the
uncertainty. Cap the challenge's contribution at half marks for either,
regardless of how polished the memo is. As a working band: "expected to fail"
means the design's own stated lower bound falls under `P_TARGET`; on the heavy
side, the class-default `z = 2` design and the range spanned by the 1/3/10%
noise-sensitivity table mark presumptively reasonable territory. A design
heavier than that range is fine when the memo prices the extra grams (a larger
`z`, a named model-form worry) and is padding when the only defense is a bare
safety factor. (`P_TARGET` = 700 N is an instructional spec, chosen so the
feasibility boundary crosses the tested design space — see the instructor
guide. Grade the reasoning against the spec, not the spec.)

## What earns a low grade

- A design defended only by "the optimizer said so," with no uncertainty and
  no physics check.
- Treating the equation optimum as truth and ignoring where the data
  contradicts it.
- A reflection that reports the number without engaging the preregistered
  prediction.
- A challenge beam expected to fail under `P_TARGET`, or one padded far beyond
  the lightest confident design.
- Code that does not run or does not match the memo.
- Post-hoc storytelling: a memo whose confident explanations appear nowhere in
  the preregistration or the card.

## What earns a high grade

- A design that names a risk and chooses anyway, with reasons.
- A group that caught a place the model misled them and said so.
- A preregistration that named the failure that actually happened — even if
  the beam underperformed. A group that predicted it would be surprised
  should score well on reflection precisely because the surprise was priced.
- A reflection that changes the second design in a way the data justifies —
  the Submission 2 §3 refit is where this shows up concretely.

## Notes for graders

- Reward judgment over precision. A well-argued "good enough" beam beats a
  precise beam with no reasoning.
- The two-query step is identical for everyone (same two beams, same returned
  values), so do not grade the numbers there; grade what students do with them.
- Distinguishing genuine reasoning from polished rationalization is exactly
  what the preregistration table is for: check the memo's explanations against
  what the group put on record before the test, and weight the on-record
  version.
