# ME 323 Module 1 — Design Decision Card

One page per design gate, the same eleven questions every time. Your group
fills this card twice: with Submission 1 (before your beam is printed — rows
1–10 plus the preregistration table) and with Submission 2 (add row 11). The
card is the skeleton of your memo: every memo prompt maps onto a row, and
graders read the card before the memo. Keep each row to one to three
sentences, with numbers where numbers exist.

The card puts your group on record before the test: what you predicted, what
you feared, and what would have changed your mind. After the test, any group
can explain the result. The card shows which groups saw it coming.

## The card

| # | Row | Your answer |
|---|---|---|
| 1 | **Decision.** What beam do you recommend? `(b, H_web)` and its estimated mass. | |
| 2 | **Physics.** What capacity and governing failure mode does the calibrated mechanics model predict there? Include the runner-up mode and its margin. | |
| 3 | **Data.** What does your GP predict there (posterior median, in the units you model)? | |
| 4 | **Model choice.** State every knob behind your pick — lane, kernel, noise, acquisition rule, and dial — and why. Was your recommended design sensitive to these choices? If it was, why did you keep it? Every number on this card is read as coming from these knobs; any that doesn't must say where it came from and why you used it. | |
| 5 | **Uncertainty.** Epistemic sigma at your design, and the total predictive interval for one future test. | |
| 6 | **Support.** How close is this design to tested beams, and what did the nearest ones do (strength *and* failure note)? | |
| 7 | **Disagreement.** Where do the physics and the GP disagree near your design, and what is your best explanation of why? | |
| 8 | **Risk posture.** Is this pick exploiting, exploring, or replicating? Name your acquisition rule and dial value. | |
| 9 | **Alternative.** What credible design did you reject, and what tipped the choice? | |
| 10 | **Falsifier.** What test outcome would make you abandon this model or this region? Give one in each direction — a low load (at your interval floor, or say why it differs) and a high one (a result above your ceiling indicts the model too) — plus any failure morphology that fires regardless of load. | |
| 11 | **Update** *(after the test)*. What did the result change: your model, your confidence, or your next design? Name the assumption that moved. | |

## Preregistration (filed with Submission 1, before printing)

Committed before print day. Graded on discipline, not on being right: a sharp
prediction that misses beats a vague one that cannot miss. "About 500 N" with
no interval earns nothing here, and neither does "it might separate or bend."

| Quantity | Your prediction |
|---|---|
| Geometry `(b, H_web)` | |
| Estimated mass (g) | |
| Calibrated-physics capacity (N) and governing mode | |
| GP posterior median (state units and denominator) | |
| Epistemic sigma at the design | |
| Interval for one future test (lower, upper, and your z) | |
| Expected observed failure morphology (what the note-taker will write) | |
| The one assumption most likely to break this prediction | |
| The *low* outcome that would change your next design (explicit threshold or observation; if the threshold sits below your interval floor, say why) | |
| The *high* outcome that would change it (what a result above your ceiling would redirect) | |

## How this is graded

The card feeds the rubric's synthesis, preregistration, and interpretation
criteria (see `ME323_Module1_Rubric.md`). A grader asks three questions, in
order:

1. Why this beam instead of the alternative in row 9?
2. What evidence would have changed your choice *before* printing (row 10)?
3. After testing, what changed beyond the dataset gaining one row (row 11)?

A card that cannot answer those is weak no matter how polished the memo built
on it. Rows 2–7 require you to run both models *at your own candidate* and
put their numbers side by side. If they agree, say why you believe the
agreement (nearby data? shared assumptions?). If they disagree, explain the
disagreement in row 7 rather than averaging the two numbers.

Row 4 has a specific job: it is where your group defends its GP architecture.
Name the lane and knobs, give the reason, and report whether the recommended
design moved when you varied them (Submission 1's stress-test prompt, and the
optional full knob sweep, generate this evidence). A design that survived the
sweep is easy to defend. A design that moved and was kept anyway needs the
better argument: say what you know that the losing settings miss.
