# ME 323 Module 1 — Design Decision Card (Submission 1, rows 1–10 + preregistration)

## The card

| # | Row | Your answer |
|---|---|---|
| 1 | **Decision** | (b, H_web) = (1.39, 13.20) mm; estimated mass 13.55 g. |
| 2 | **Physics** | Calibrated capacity 635 N = 46.8 N/g. Governing mode: bend, but P_LTB = 635 N is a dead tie (0.1% margin) — the design sits on the bend/LTB boundary, so the label means "both active." Separation is the true runner-up mechanism at 797 N, a 26% margin. |
| 3 | **Data** | Lane A GP (log str/w, estimated-mass denominator): posterior median 36.65 N/g, i.e. 497 N. Lanes C and D agree there: 37.58 and 37.40 N/g. |
| 4 | **Model choice** | Lane A plain, RBF, 3% noise, MUI psi = 0.5, plus a stated veto (b >= 1.29, H_web <= 14.5). LOO favored lane D by 0.55 N/g; we overruled it because D's advantage collapses where we design: D and A disagree by 25% at D's preferred point, an artifact of extrapolating the physics correction across a 0.5 mm H length scale. Sensitivity: under the veto the pick held at (1.29, 13.20) for both kernels at 1 to 3% noise and moved one notch in H at 4.4 and 10%; lanes C and D join the same point at 10%. We kept the neighborhood and stepped one notch interior (1.29 to 1.39) for separation and print margin at a predicted cost of 0.05 N/g. |
| 5 | **Uncertainty** | sigma_epi = 0.023 (log). sigma_total = sqrt(0.023^2 + 0.03^2) = 0.038. z = 2 interval for one future test: [34.0, 39.5] N/g = [461, 536] N. |
| 6 | **Support** | 0.29 mm from beam 16 (1.10, 13.25): best beam tested, 37.48 N/g, morphology not supplied (query). 0.43 mm from beam 17 (1.00, 13.39): 36.65 N/g, morphology not supplied. 0.80 mm from beam 15 (1.00, 12.5): 34.41 N/g, flange separated at the top interface and the bottom interface fractured 80% through. |
| 7 | **Disagreement** | Physics exceeds the GP by about 10 N/g at our design (46.8 vs 36.7). Explanation: knife-edge optimism in the calibrated physics — the max-of-min optimizer runs to where all mode surfaces tie and every parameter error compounds. The bias is measured, not conjectured: beams 16 and 17, 0.3 to 0.4 mm away, came in 23% and 21% below calibrated physics. We do not average the two numbers; we take the GP's, because it already carries the measured correction. |
| 8 | **Risk posture** | Exploiting, with a stated veto. MUI, psi = 0.5, 3% noise. Half a sigma of benefit of the doubt to untested designs; regions struck: b < 1.29 (separation family + wall + near-replicate of the class queries) and H_web > 14.5 (beam 9 tip/twist territory, mass-denominator inflation). |
| 9 | **Alternative** | (1.39, 11.71), lane D's pick, promising 41 to 44 N/g across kernels and noise up to 4.4%. Rejected because: lane A predicts 33.0 N/g there (25% cross-model disagreement, larger than the promised gain); it is another bend/LTB knife-edge point (734 vs 734 N); its correction factor (0.94) is anchored only by beam 14 across a 1.3 mm H gap while every closer-analog correction is 0.77 to 0.88; and we have exactly one print. |
| 10 | **Falsifier** | Either outcome kills the model for us: (a) strength below 455 N (below the z = 2 lower bound with margin), or (b) an observed clean flange-web separation with no vertical fracture. (a) says the GP median and its flat-in-b ridge are wrong at thin b; (b) says the 26% separation margin (and tau_i) does not hold at this session's layer bond. Either sends the next design to b >= 2 and demotes lane A near the boundary. |
| 11 | **Update** | (after the test) |

## Preregistration (filed before printing)

| Quantity | Prediction |
|---|---|
| Geometry (b, H_web) | (1.39, 13.20) mm |
| Estimated mass | 13.55 g |
| Calibrated-physics capacity and mode | 635 N; bend, tied with LTB (0.1%); separation +26% |
| GP posterior median | 36.65 N/g, log str/w model, denominator = estimated mass (497 N) |
| Epistemic sigma at the design | 0.023 (log units) |
| Interval for one future test | [461, 536] N ([34.0, 39.5] N/g), z = 2 on sigma_total = 0.038 |
| Expected observed failure morphology | Vertical fracture at the bottom center of the beam, likely partial through-depth; a small secondary flange-web separation would not surprise us. Not expected: tip/twist, or a clean separation with no fracture. |
| Assumption most likely to break this | The 3% independent-noise assumption together with lane A's long b length scale (3.4 mm): if session-to-session bond drift dominates, both the interval and the flat-in-b ridge are too confident. |
| Outcome that changes the next design | >= 510 N: next design steps thinner along the ridge (b toward 1.2), the ridge is real and flat. <= 455 N or separation morphology: next design moves to b >= 2 and we distrust every thin-b prediction from this dataset. In between: refit and re-run the sweep; the decision stands on the update. |
