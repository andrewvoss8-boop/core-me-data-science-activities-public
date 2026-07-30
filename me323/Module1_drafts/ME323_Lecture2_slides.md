---
marp: true
title: "ME 323 Module 1 — Lecture 2: From Data to Decisions"
paginate: true
---

# From Data to Decisions Under Uncertainty
### ME 323 Module 1, Lecture 2

Last time: the equations narrow the beam problem but cannot solve it. A fracture mode with no formula, fixture-dependent LTB, a few expensive tests.

Today: a model that learns from sparse data and tells you how much it does not know.

*(Flow and examples adapted from Prof. Bilionis's data-science lecturebook; notebooks in `Bilionis lecturebook/`.)*

---

## Where Pre-lab 1 left you

- You coded three capacity branches — flexural yield, junction shear-flow separation, LTB — calibrated $(\sigma_y, k, \tau_i)$, and took the minimum: one capacity number per design.
- The parity plot showed where that number holds and where it misses.
- Your optimizer picked **b = 1.10, H_web = 13.25 mm**: predicted 48.7 N/g. Staff queried the **ground truth model** — a frozen model fit to a prior campaign of real bend tests, standing in for the testing machine — and it returned 475.7 N = 37.48 N/g on the estimated-mass basis. At that geometry all three mode capacities tie within ~1%, so the "LTB" proxy label is a knife-edge call.

The physics gave you a *point estimate* sitting on a mode boundary, the region where you trust it least. Today's tool adds what is missing: a statement of confidence.

---

## You already have most of this

| Idea | Where you have it |
|---|---|
| Bayes' rule | ME 239 |
| Gaussian distribution | ME 239 |
| Multivariate Gaussian, covariance | ME 239 |
| Conditioning a Gaussian on data | ME 239 |
| **Gaussian Process** | new today, but only one step past 239 |
| **Acquisition functions (BO)** | new today |

We stack the 239 pieces into one tool and point back rather than re-derive.

---

## Bayes, in one line

$$\text{posterior} \propto \text{likelihood}\times\text{prior}$$

You start with a belief about beam strength. You test a beam. You update the belief.

Bayesian thinking: carry a **distribution** over the unknown strength surface, not a single guess. Every slide that follows is this line, applied to beams.

---

## A Gaussian is a belief about one beam

![height:420px](figures/fig_gauss_strength.png)

This is exactly ME 239's [fitting Normals to data](https://purduemechanicalengineering.github.io/me-239-intro-to-data-science/lecture12/example-fitting-normals.html) — mean, variance, `st.norm` — done on strength; Pre-lab 2's warm-up replays it on these four beams. Where does the 3% come from? Repeat prints of one design — four beams at (1.3, 12.8) spanned 548.6 to 566.1 N. Pooled over every repeated geometry the scatter runs ≈4.4%, with session-to-session and printer-to-printer structure inside it; the class fixes 3% as a stated working value.

---

## Two beams at once: covariance

![height:400px](figures/fig_mvn_correlation.png)

Nearby designs share material, geometry, and physics, so their strengths move together. The covariance matrix `Σ` writes that down. This is the piece the GP is built on.

---

## Conditioning: measure one, update the other

![height:400px](figures/gif_conditioning.gif)

Measure beam A and the joint Gaussian *conditions*: the belief about beam B shifts and tightens. You did this algebra in 239. Everything today is this move, repeated.

---

## The leap: a function is a long Gaussian vector

![height:400px](figures/gif_mvn_to_gp.gif)

Strength at 2 designs: a 2D Gaussian. At 120 designs: a 120-dimensional Gaussian. Connect the dots and the vector *is* a function. A **kernel** fills in the covariances: nearby beams correlate, distant ones do not.

---

## A Gaussian Process, before and after data

![height:400px](figures/fig_gp_prior_posterior.png)

Before data, the kernel proposes candidate strength curves. Each test kills the curves that disagree. In this module the GP models log(str/w), so $\exp(\mu_{\log})$ is the **posterior median** in N/g. The band quantifies uncertainty conditional on the model.

---

## Watch it learn, one beam at a time

![height:430px](figures/gif_gp_learning_beams.gif)

*(Earlier beam campaign, span-200 geometry; the concept is what matters. This animation gets rebuilt from the new 44-beam dataset when testing finishes.)*

The band collapses where beams land and stays wide where nothing has been tested. The equations never gave you that second part.

---

## The kernel is a modeling choice

![height:360px](figures/fig_kernel_lengthscale.png)

The length scale answers: how far does one test's influence reach? Too short and every point is an island. Too long and the model cannot bend. There is no single right answer; there are defensible and indefensible ones.

---

## So is the noise

![height:360px](figures/fig_noise_fits.png)

We assume 3% as the class working value. Pre-lab 2 refits at 1%, 3%, and 10% as a sensitivity check. The 1% fit moves to (1.58, 14.88), while the 3% and 10% fits pick (1.00, 13.39). The recommendation is assumption-sensitive.

---

## Epistemic and aleatory uncertainty do different jobs

- **Epistemic uncertainty** is uncertainty about the latent response surface because tests are sparse. Informative new beams can reduce it.
- **Aleatory uncertainty** is print-to-print and test-to-test scatter at a fixed nominal design. Another location does not remove it.
- For one future observation in log space:

$$\sigma_\text{total}=\sqrt{\sigma_\text{epi}^2+r^2},\qquad r=0.03$$

MUI and EI use $\sigma_\text{epi}$ because they value learnable uncertainty. A reliability bound for one future printed beam uses $\sigma_\text{total}$.

---

## Explore vs exploit

![height:420px](figures/fig_explore_exploit.png)

Exploit: test where the posterior median is highest. Explore: test where epistemic uncertainty is widest. **MUI** (maximum upper interval) makes the tradeoff a dial in latent log space:

$$a(x)=\mu(x)+\psi\,\sigma(x)$$

---

## The loop: Bayesian optimization

![height:430px](figures/gif_bo_mui.gif)

Fit → pick the acquisition argmax → test → refit. Watch it probe the thin-web corner once, learn the surface is worse than it looks there, and settle on the real peak. Seven tests, no gradient, no formula for the dip.

---

## Expected Improvement, the other dial

**EI** asks: by how much would a new test *beat the best beam so far*, on average?

- accounts for both latent mean $\mu$ and epistemic uncertainty $\sigma$, like MUI,
- but weighs *improvement*, so it stops caring about regions that cannot win,
- and it has its own dial, $\xi$: an improvement threshold. $\xi=0$ lets the probabilities trade explore against exploit on their own; larger $\xi$ counts only wins that clear the incumbent by that margin, pushing the pick toward uncertain regions.

MUI and EI can point at different next beams. The choice encodes your appetite for risk; Pre-lab 2 has you code both.

---

## Zoom out: spending a test budget

Each print-and-test costs a machine slot, a test engineer hour, and days of queue. The class gets **two ground-truth queries** — answered by the frozen staff model, cheap because the prior campaign already paid for that information — and each group gets **one real print**.

Optimal experimental design is the batch version of the acquisition question: given N tests, which set teaches the most or finds the best fastest? Choosing the next test *is* the engineering decision.

---

## Physics-informed GP: the two tracks meet

![height:400px](figures/gif_pigp_vs_gp.gif)

*(Earlier campaign data; rebuilt with the new dataset when testing finishes.)*

The plain GP sees only `(b, H_web)`. Submission 1 lane C also sees `log(P_phys)` and `P_LTB/P_bend`, where `P_phys` is the calibrated three-branch capacity (bend, separation, LTB). The features sharpen the fit where their physics is useful and can mislead where it is blind — the separation branch carries one calibrated $\tau_i$ for an interface strength that scatters between print sessions. Deciding which region you are in is your job, not the model's.

---

## Two decisions are yours; the rest are stress tests

You will meet six modeling "knobs" in Submission 1. Do not treat them as six equal choices.

- **You own two decisions:** the **lane** — how physics and data combine into one model — and the **risk posture** — how hard to chase predicted performance versus uncertainty.
- **The rest — kernel, noise, target scale — are stress tests.** After you pick coordinates, swap the kernel and refit at 1% / 3% / 10% noise, and see whether your pick survives.
- The strong conclusion is not "we chose RBF and 3%." It is: *"our exact optimum moves under reasonable assumptions, but every defensible model points at this neighborhood"* — or, just as strong: *"the recommendation is unstable, so we bought information instead of chasing the current maximum."*

---

## The decision map: put both models on the same axes

![height:420px](figures/fig_decision_map_4panel.png)

Calibrated physics (with mode boundaries), GP posterior median, their disagreement, and epistemic sigma — tested beams on every panel. Submission 1 builds this with *your* knobs; read your candidate against all four before you commit.

---

## The activity from here

1. **Pre-lab 2**: fit the GP, write MUI (and EI), work the noise assumption, find the GP-recommended beam.
2. **Two queries**: the class equation design and the class GP design go to the ground truth model — the same two beams for everyone. Only two.
3. **Submission 1**: combine physics, GP, and the two new points; pick the beam you will print; defend it in the memo.
4. Print, test, reflect, redesign: Submission 2 folds your own test result back into the model and asks what it changes.

---

## Before next time: Pre-lab 2

In `ME323_Module1_Prelab2_ML`:

- warm up by rebuilding the GP from ME 239's Normal-fit in four small steps (fit one Normal → covariance → conditioning → many beams at once),
- compare vanilla GP setup choices and read posterior median, epistemic uncertainty, and total predictive uncertainty,
- write both MUI and EI,
- refit under 1% / 3% / 10% noise and note what moves,
- record the locked class design: **b = 1.00 mm, H_web = 13.39 mm**, posterior median 36.7 N/g.

That beam is the class's second ground-truth query. Bring your rationale, not just the number.
