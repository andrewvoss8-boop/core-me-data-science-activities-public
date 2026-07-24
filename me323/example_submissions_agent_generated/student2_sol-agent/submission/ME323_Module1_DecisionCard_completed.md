# ME 323 Module 1 — Completed Design Decision Card

## Submission 1 decision card

| # | Row | Answer |
|---|---|---|
| 1 | **Decision.** What beam do you recommend? `(b, H_web)` and its estimated mass. | **Replicate `(b, H_web) = (1.10, 13.25) mm`**, estimated mass **12.694 g**. It is the strongest observed/query design at 475.7 N = 37.47 N/g, and the real print adds repeatability and failure-morphology evidence that the staff query did not provide. |
| 2 | **Physics.** What capacity and governing failure mode does the calibrated mechanics model predict there? Include the runner-up mode and its margin. | Calibrated mechanics predicts **617.0 N (48.60 N/g), LTB governing**. Bending is the runner-up at **620.7 N**, only **0.61%** higher; separation is 622.9 N. This is effectively a three-mode knife edge, so the LTB label is not a confident morphology prediction. |
| 3 | **Data.** What does your GP predict there? | Lane-A Matérn GP posterior median: **36.75 N/g**, equivalent to **466.6 N** using estimated mass. |
| 4 | **Model choice.** Which GP architecture did you choose, and why? Was the design sensitive? | **Lane A (plain log str/w), Matérn-5/2, 3% noise, MUI with ψ = 0.** Matérn slightly improves lane-A LOO (2.89 versus 2.94 N/g for RBF) and permits mode-handoff creases. Lane D wins global LOO, but it inherits the same physics structure that overpredicted this mode-boundary region by 23%, so I did not let it control extrapolation here. The exact optimum moves with noise/kernel, but lane-A pure exploitation stays in the same neighborhood: roughly `b = 1.00–1.48 mm`, `H_web = 13.20–13.39 mm`. |
| 5 | **Uncertainty.** Epistemic sigma and total predictive interval. | **σ_epi = 0.0217 log units**. With 3% observation noise, **σ_total = 0.0370**. Using `z = 2`, one future test is preregistered at **34.13–39.58 N/g**, or **433–502 N**. |
| 6 | **Support.** How close is this design to tested beams, and what did the nearest ones do? | It exactly replicates beam/query 16: **475.7 N, 37.47 N/g**, morphology unavailable. Beam 17 at `(1.00, 13.39)` returned **445.8 N, 36.64 N/g**, also without morphology. Beam 15 at `(1.00, 12.50)` reached **475.0 N, 34.41 N/g** and separated at the top flange-web interface, with an additional bottom-interface crack. |
| 7 | **Disagreement.** Where do physics and GP disagree, and why? | At the selected point, physics predicts **48.60 N/g** while the GP predicts **36.75 N/g**; the observed query is **37.47 N/g**, supporting the GP locally. The mechanics optimum sits where all three branches are within about 1%, so small fixture, interface-strength, imperfection, or print-session changes create a large error. The scalar physics model also cannot represent progressive interface fracture or twist-off morphology. |
| 8 | **Risk posture.** Exploit, explore, or replicate? | **Replicate / exploit.** MUI with **ψ = 0** gives no uncertainty bonus and points to the nearby thin-web ridge around `(1.00, 13.20)`. I used the engineering veto to replicate the exact best-observed geometry because only one real print is available and the missing information is repeatability plus mechanism, not another uncertain corner prediction. |
| 9 | **Alternative.** What credible design did you reject? | I rejected the default uncertainty-seeking interior candidate near **`(1.39, 14.88)`**. Its lane-A Matérn median is only about **35.77 N/g**, with **σ_epi ≈ 0.0507**, and its closest physical warning is beam 9, which twisted off the stand. It offered more information but lower expected performance and greater LTB/fixture risk. |
| 10 | **Falsifier.** What outcome would make you abandon the model or region? | **A peak below 430 N**, or a twist-off before clear material/interface damage, would fall below the preregistered interval or show that the fixture/stability model is not transferable. Either outcome would make the next design leave this thin-web ridge and force a revision of `k`, `tau_i`, or the observation model. |
| 11 | **Update after test.** | *To be completed after the physical test.* |

## Preregistration

| Quantity | Prediction |
|---|---|
| Geometry `(b, H_web)` | **(1.10 mm, 13.25 mm)** |
| Estimated mass | **12.694 g** |
| Calibrated-physics capacity and governing mode | **617.0 N; LTB proxy**. Bending is 620.7 N and separation is 622.9 N. |
| GP posterior median | **36.75 N/g on estimated mass**, equivalent to **466.6 N**. |
| Epistemic sigma at the design | **0.0217 log units** |
| Interval for one future test | **433–502 N** (**34.13–39.58 N/g**), using **z = 2** and total `sigma_log = 0.0370`. |
| Expected observed failure morphology | **Top flange separates from the web along the printed interface, without a complete central vertical fracture.** This is a morphology prediction based on nearby actual failures, even though the scalar physics proxy labels the point LTB by only 0.61%. |
| One assumption most likely to break the prediction | The single calibrated **interface strength `tau_i`** transfers to this print session despite layer-bond and support-condition drift. |
| Outcome that changes the next design | **Peak load < 430 N or twist-off before material damage.** Move away from the thin-web ridge and revise the fixture/interface model before optimizing again. |

## Final choice in one paragraph

I chose **`b = 1.10 mm, H_web = 13.25 mm`** because the decision card favors a claim that is both useful and falsifiable. It is already the best observed/query beam, the plain GP predicts it with low epistemic uncertainty, and a real replicate resolves the most important missing evidence: whether the 37.47 N/g result repeats and how the beam actually fails. I did not chase the nominal mechanics value of 48.6 N/g because the three capacity branches are tied within about 1% and the previous mechanics prediction missed by 23%. I also did not chase the high-uncertainty tall-web candidate because its expected value is lower and nearby evidence includes twist-off. The choice is therefore not “the equation optimum is true”; it is “the best-supported beam is worth verifying, with a sharp threshold that will make us abandon the region if it fails.”
