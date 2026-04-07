Status Apr 7

Core path: 2-variable (b, H) GP/BO lab for Purdue. 5D stability and ablation notebooks are reference/advanced material, not required for v1.

McCallie pilot (4D): printer/rig drift was real and systematic. One student team beat "Voss + AI" without ML. Engagement came from competition and skin in the game, not from the notebook itself.

Activity structure: "Who Wins?"

Three approaches compete. The point is not that ML+physics wins (students will figure that out). The point is that executing ML+physics well is hard, and that is where the learning happens.

Phase 1: The Physicist (before the notebook opens) -- "Can you beat the machine?"
Each team member A builds a hand calculator in Google Sheets or Desmos: Str/w as a function of b and H, with R and failure criteria visible. They discover: for a given b, there is an optimal H. They plot this curve. They submit a physics-only beam recommendation with written justification. This is a gate. No GP notebook access until Phase 1 is checked off. If time allows for multiple rounds of testing, the first round is framed as hand calcs vs. the GP: each team's Phase 1 pick and their Phase 2 pick both get printed and tested. Students see directly whether physics or data won, and why. This sets up Phase 3 (merge) with real motivation.

Phase 2: The Data Scientist (the notebook)
Team member B works the GP notebook independently. Loads the shared training data. Fits a GP with (b, H) inputs. Tunes noise and acquisition. Gets a pure-ML recommendation. This person does not see the hand calc results yet.

Phase 3: The Engineer (merge)
A and B come together. They code the physics into the ML: specifically, they write the equation for R (stability ratio = Mcr/My) in a code cell the notebook provides a scaffold for. This requires translating the beam section property equations (Iy, J, Ix) into code. It is real work, maybe 20-30 lines, but the notebook gives them the structure and they fill in the physics. This is not the main thing they are evaluated on, but if they get it wrong, the GP with physics features will perform worse than the plain (b,H) GP, and that will show.

For dH: students already found the optimal H(b) curve in their Phase 1 spreadsheet. They can code the optimization in Python, or (simpler) interpolate from their spreadsheet values. Either way, Phase 1 directly feeds Phase 3. This is the payoff for doing Phase 1 well.

They compare all three GP surfaces (physics-only prediction, GP with (b,H), GP with (b,dH,R)). They cross-check the GP recommendation against the spreadsheet. They pick one beam (the "human pick"), set a confidence wager, and present at a CDR checkpoint.

This structure gives each person distinct, meaningful work. Neither role is filler. The merge in Phase 3 is where the real insight happens, and it only works if both people did their job well in Phases 1 and 2.

Printing budget

Single round: Teams of 2 (40 teams), each submitting 1 beam (the Phase 3 human pick). Instructor pre-prints 3 baseline beams: best physics-only, best GP-only (b,H), best GP+physics (b,dH,R). Total: ~43 beams. Teams of 4 if that is too many (23 beams).

Multi-round (if printing/testing time allows): Round 1 prints each team's Phase 1 pick (hand calc) and Phase 2 pick (GP). Teams see the results, learn where physics or data won and why. Round 2 is Phase 3: they merge, code R into the GP, and submit their final human pick. This doubles the printing but makes the "can you beat the machine?" framing concrete and gives students real feedback before the final decision. Budget: ~120 beams for 40 teams (2 per team in round 1 + 1 in round 2 + 3 baselines). Probably only feasible with teams of 4 (~60 beams).

Differentiation: why smart teams win

"It is too easy to know ML+physics is the best approach." True. But executing it well requires:

1. Noise judgment. Students pick alpha from a continuous range. The ablation study showed: too low overfits, too high smooths away real signal. The right answer depends on the data. Smart teams reason about the calibration data.
2. Physics encoding quality. Computing R and dH correctly requires understanding the beam equations. If you get it wrong, the GP gets garbage features and performs worse than plain (b,H).
3. Hand calc cross-check. Teams that built a good spreadsheet in Phase 1 can sanity-check the GP. Teams that rushed Phase 1 are flying blind in Phase 3.
4. Acquisition tuning. The explore/exploit tradeoff matters. Students who understand what kappa or xi does make better choices.
5. Heteroscedastic noise. Students who recognize that beams near R=1 have higher noise and account for it get better uncertainty estimates.
6. The wager. Forces explicit confidence calibration. Smart teams wager appropriately. Overconfident teams lose points.

Student ID seeds the random candidate generation, so no two teams get identical outputs even with identical settings.

Transferability risk

The ablation study on McCallie data showed that (b, dH, R) + high noise + EI dominates. There is no guarantee the same configuration wins on Purdue printers and test rigs. Two options:

Option A: Purdue runs a pilot dataset (12-16 beams, LHS-spaced) ASAP and sends the numbers back. We validate before deploying. This is the safe path.

Option B: Accept the risk. The activity grades on reasoning quality, not on whether (b,dH,R) beats (b,H) on their specific data. If the physics features do not help on Purdue's data, that is itself a lesson (maybe their printer is more consistent, or their rig introduces different failure modes). The activity still works because students learn the process of encoding physics into a model and evaluating whether it helped.

Option B is probably fine for v1. The worst case is that the baselines perform similarly, and the differentiation comes entirely from noise/acquisition tuning and the wager. That still teaches the right things.

Risk project variant

Adapted from the Beam Redesign for Risk and Reliability Project. Each team draws a random minimum strength requirement (in Newtons, not Str/w) from a distribution. Goal: design the lightest beam that hits your required strength. The objectives are separated: strength is the constraint, weight is what you minimize. This matters because Str/w already bakes in weight, which hides the tradeoff. With a raw strength floor, students must reason about how much extra mass they can shave while still clearing the threshold with confidence.

Pop quiz for the whole class if any team's beam fails their strength requirement. Bonus for lightest beam that clears.

This version directly teaches wise risk-taking. You must set a safety margin using the GP's uncertainty bands. Overdesign wastes mass (costs you on the leaderboard). Underdesign risks failure (costs everyone). The GP helps you thread the needle, but only if you trust it the right amount.

This could be a standalone activity or a follow-on to the "Who Wins?" version. The instructor chooses.

Bayesian fundamentals section (in the notebook, before they touch the GP)

The notebook needs a section early on that builds intuition before students start tuning knobs. Structured as a progression:

1. What is Bayesian reasoning? You have a prior belief. You see data. You update. The posterior is your new belief. One concrete example: "you think this beam will hold 400N based on the equations. You test it and it holds 350N. What do you believe now? What if you test a second one and it holds 380N?" This is Bayes in two sentences.

2. A GP is Bayesian reasoning on steroids. Instead of updating one number, you update an entire surface. The prior is the kernel (how smooth do you think the function is?). The data updates it everywhere, but more where you have data and less where you do not. The uncertainty bands are the model telling you "I am guessing here."

3. What are the different GP setups and when would you choose each? This is where they see the knobs before turning them:
   - Noise level (alpha): how much do you trust each data point? Low alpha = trust the data, risk overfitting. High alpha = smooth through noise, risk missing real signal.
   - Parameterization: (b,H) vs (b,dH,R). When does adding physics features help? When does it hurt (if computed wrong)?
   - Acquisition function: UCB vs EI. UCB has an explicit explore/exploit dial (kappa). EI balances automatically but has xi. When would you want more exploration?
   - Kernel: Matern vs RBF. How smooth do you think the real function is?

4. How different are the answers? Show them. Run the GP with 3-4 preset configurations on the training data and display the resulting surfaces and recommendations side by side. Students see that the "answer" depends heavily on choices they make. This is the whole point: the model is not an oracle, it is a tool that reflects your assumptions.

This section should take 15-20 minutes. Short text, concrete examples, one or two interactive cells where they toggle a setting and see the surface change. No graded deliverable from this section, just understanding. The graded work comes in Phases 2 and 3.

Noise calibration

Instructor provides a small separate dataset before the main activity: a few beams tested on different printers, different filament colors, with 2-3 repeats each. Students compute variance across repeats. They look for patterns: does noise depend on R? On printer? On color? The data is deliberately incomplete. Students must make judgment calls about what noise level to use. This is one of the main learning objectives.

Wagering and consequences

Light version: wager affects project score only (1-5 bonus/penalty points).
Heavy version: add pop quiz if any team's beam is weaker than all three baselines. Creates collective stakes.

Wagering on day 1 (before seeing results) gets a multiplier. Teaches: committing early with less information is riskier but has higher expected payoff if you are well-calibrated.

The main pedagogical point of wagering is wise risk-taking. Students learn to characterize uncertainty, leverage modeling and physics, and take calculated risks with limited data. This is the engineering skill the whole activity is built around.

What is built

- beam_lab_student.ipynb: Tiger-team version with PBL scaffolding (man vs machine, CDR, wager, reflection). GP/BO code works for 2-variable case.
- beam_lab_instructor_setup.ipynb: LHS generation, data entry template, noise calibration from duplicate tests.
- ablation_study_2var.ipynb: Retrospective BO sensitivity analysis. Key finding: (b,dH,R) + alpha=3e-3 + EI is the strongest configuration on McCallie data.
- I_beam_2var_GP.ipynb: 2-variable GP exploration notebook with 1D slices, EI/UCB recommendations at multiple exploration levels, and (b,dH,R) reparameterization block.
- LHS_beam_design_12plus.ipynb: LHS generation with maximin infill for additional samples.
- Beam Redesign for Risk and Reliability Project.md: Reference for the risk-project framing.

Open questions

1. LLM policy: allow for spreadsheet/plots but not for the human pick justification? Or allow everywhere and grade on quality of reasoning?
2. Rubric weighting: Phase 1 (spreadsheet + physics recommendation) vs Phase 2-3 (GP + human pick) vs reflection.
3. Digital-only variant: GP oracle for schools without printers. Same structure, simulated expensive tests. Deferred.
4. Drift: mention McCallie anecdote in the CDR prompt ("what would make identical beams test weaker over time?") but do not simulate drift for v1.
5. Purdue data: Option A or B above. Need to decide before semester start.

Next steps

1. Get Purdue's decision on pilot data (Option A) vs. proceed without (Option B).
2. Finalize the hand-calc prerequisite: write the Phase 1 assignment sheet (what to compute, what to submit, what "checked off" means).
3. Re-read beam_lab_student end-to-end as a student. Check flow, cognitive load, broken refs.
4. Lock rubric: one short block covering reasoning, model skepticism, physics cross-check, wager calibration, team roles.
5. Instructor one-pager: timing (how many lab periods), what to print, common failure modes, CDR script.

Notebook prompts and content to build

Physics discovery sequence (guide students to catch what the bending calc misses)
- Start from just 3 data points. Have students calculate predicted failure stress from Ix alone. What goes wrong? The thin-web beam is way weaker than predicted.
- Why is the thin-web beam so much weaker? Because bending theory assumes the beam stays upright. Thin webs tip sideways first. This is lateral-torsional buckling (LTB).
- What are J and R? J is the torsional stiffness of the cross-section (resistance to twisting). R = Mcr/My: how close the beam is to tipping before it yields. R > 1 means it yields first (ductile, predictable). R < 1 means it tips first (sudden, catastrophic).
- Do the failure descriptions in the data cluster with R? (Yes. Low-R beams show twisting/lateral failure modes.)
- Students must catch: you need more than the bending calc. Bending is necessary but not sufficient.
- What assumptions does R make? Thin-walled J approximation. Idealized BCs. No imperfections. No fillet contribution unless added.

Noise and uncertainty prompts
- Characterize noise sources: color-to-color, printer-to-printer, test-to-test, bond quality, porosity. Include screenshot from 3D printer variability paper.
- Is it safer to assume more noise or less? More noise prevents overfitting (acts as regularizer). Less noise trusts data more, risks fitting to noise. There is a sweet spot.
- Is it always better to overestimate noise? Mostly yes for safety, but too much smooths away real signal.
- Are the provided +/- bounds on material flexural strength adequate noise bounds? What alpha do they equate to? (Convert material uncertainty to GP noise in log-space.)
- How would your noise choice change if consequences of failure were higher?
- If your boss required 1% chance of failure, how would you design it? (Connect GP uncertainty bands to reliability.)

Real-world messiness prompts
- The print stops halfway through. Can you keep that print? How do you decide?
- How would the flat-strength project work? (See risk project variant above.)

Core takeaway for students: understand the noise, understand the physics, have intelligent priors.

Industry and research connections
- SpaceX-style interview framing: "walk me through your design decisions." Check snubber, mechie.io for example questions.
- PIGP paper (physics-informed GP): https://arxiv.org/pdf/2507.09968

Lateral-torsional buckling: the physics of R, J, and tipping failure

Geometry: I-beam with web height H (mm), web thickness b (mm), flange width B = 16 mm, flange thickness h = (25 - H)/2 mm. Total height = 25 mm. Span L = 202.3 mm.
Material: PLA. E = 2.5 GPa. G = E/2.6 ~ 0.962 GPa. Yield strength sigma_y = 76 MPa.

Bending strength (what the simple calc gives you):
  Ix = b*H^3/12 + 2*(B*h^3/12 + B*h*((H+h)/2)^2)       [strong-axis moment of inertia]
  y_max = H/2 + h                                          [NA to extreme fiber, in meters]
  My = sigma_y * Ix / y_max                                [yield moment]
  Predicted failure load (3-pt): P_yield = 4*My / L

  This calc predicts that tall, thin-webbed beams are strong (big Ix from flanges far apart). It is wrong for thin webs.

Tipping strength (what the simple calc misses):
  Iy = H*b^3/12 + 2*h*B^3/12                              [weak-axis moment of inertia]
  J = (H*b^3 + 2*B*h^3) / 3                               [torsional constant, thin-wall approx]
  Mcr = (C1 * pi / L) * sqrt(E*Iy * G*J)                  [critical moment for LTB]

  C1 = 1.35 for 3-point bending (moment gradient factor).

  This is the moment at which the compression flange kicks sideways and the beam twists and collapses. No warning.

Stability ratio:
  R = Mcr / My

  R > 1: yielding governs. Ductile. Predictable from Ix alone.
  R < 1: LTB governs. Sudden. Bending calc overpredicts by a factor of 1/R.
  R near 1: sensitive to imperfections, BCs, print quality. This is where noise is highest.

Why thin webs break the bending prediction:
  Iy ~ b^3 (dominated by web contribution for small b).
  J ~ b^3 (web term dominates for small b).
  So Mcr ~ b^3.
  But My ~ Ix, which is dominated by flanges via the parallel axis theorem. My is weakly dependent on b.
  Result: as b decreases, Mcr drops as b^3 while My barely changes. R drops fast.

  Example: b=1.5mm, H=20mm gives R ~ 0.5. The bending calc says this beam is strong. It will actually fail at about half the predicted load because it tips.

  Example: b=5mm, H=18mm gives R ~ 3. This beam yields cleanly. The bending calc is accurate.

Intuition for J:
  J measures how hard it is to twist the cross-section. For a thin-walled open section like an I-beam, J is proportional to the sum of (length * thickness^3) for each plate element. A thin web (small b) makes J small, makes the beam easy to twist, makes it vulnerable to LTB. Thickening the web or adding fillets at the web-flange junction increases J and raises R.

What students code in Phase 3:
  The notebook provides function signatures and constants. Students fill in:
  1. calc_Iy(H, b, B, h) -> Iy in m^4
  2. calc_J(H, b, B, h) -> J in m^4
  3. calc_R(H, b, B, h) -> R (dimensionless), using Mcr/My
  These use the equations above. All inputs in mm, convert to m internally.
  If coded correctly, R becomes a powerful GP feature. If coded wrong, the (b,dH,R) GP underperforms (b,H), and students see that immediately in the output.
