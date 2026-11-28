---
name: ml-playground-audit
description: >-
  Conduct a deep product, UX, and functional audit of client-side machine learning playgrounds.
  Orchestrates multi-perspective subagents, prioritizes real browser interaction over DOM inspection,
  verifies mathematical and statistical correctness independently, and generates prioritized,
  evidence-backed audit reports. Use when auditing, reviewing, or testing ML playgrounds, educational
  data science tools, or interactive model explorers.
version: 1.0.0
author: Rishab Manocha
tags: [machine-learning, audit, ux, product, testing, subagents, evaluation]
---

# Machine Learning Playground Audit

Conduct an exhaustive product, usability, interaction, educational, and mathematical audit of client-side machine learning playgrounds. Evaluates applications through multi-perspective human exploration, rigorous independent mathematical validation, and systematic subagent orchestration.

---

## When to Activate

- **Activate when**:
  - Auditing, reviewing, or testing an interactive machine learning playground or educational data science tool.
  - Evaluating algorithm behavior, interactive visualizations, decision boundaries, training loops, metrics, or parameter controls.
  - Conducting a pre-release product review, UX teardown, or functional verification of an exploratory ML interface.
  - The user requests deep exploratory testing across product, UX, educational clarity, and mathematical correctness.

- **Do NOT activate when**:
  - Running simple unit or integration tests on backend code.
  - Performing automated headless smoke tests without user-facing visual interaction.
  - Reviewing general static code quality or linting (use static analysis or SonarQube tools instead).

---

## Core Philosophy & Quality Bar

1. **Substance Over Checklist**: A superficial QA pass that merely asserts buttons click or DOM elements render is a failure. Genuine usage requires experimenting with features, testing mental models, probing edge cases, and uncovering confusing outputs.
2. **Quality Over Quantity**: 12 reproducible, high-impact, deeply analyzed findings are vastly superior to 100 generic observations.
3. **Real Interaction Over DOM Inspection**: Always interact with the application through visible UI, screenshots, mouse/keyboard events, and user workflows. DOM and source-code inspection are strictly secondary confirmation tools used *after* an issue is experienced visually.
4. **Independent Mathematical Verification**: A successful execution is not proof of a correct result. Independently calculate expected outputs using known mathematical formulas and small verifiable test cases.
5. **Zero Hallucinations**: Every finding must be grounded in real observations or verified mathematical calculations. Categorize unverified concerns explicitly as *Unverified Suspicion*.

---

## The Primary Testing Loop

Every interaction with the playground must follow this empirical loop:

```text
[1. Observe Screen]
        │
        ▼
[2. Anticipate User Expectation]
        │
        ▼
[3. Formulate Action]
        │
        ▼
[4. Execute UI Interaction]
        │
        ▼
[5. Observe Actual Response]
        │
        ▼
[6. Interpret & Compare (Expected vs Actual)]
        │
        ▼
[7. Probe Deeper / Check Stale State / Verify Math]
        │
        ▼
[8. Capture Evidence & Document Actionable Finding]
```

---

## Step-by-Step Audit Workflow

### Phase 1: Product Discovery & Mental Mapping
*Do not immediately jump into error validation. First understand the product.*

1. **Orientation**: Open the playground and explore the layout, navigation, algorithm selection, dataset loaders, configuration panels, visualization viewports, and metric cards.
2. **Mental Map**: Identify:
   - What algorithms are supported (classification, regression, clustering, dimensionality reduction, neural networks)?
   - What datasets or synthetic data generators exist?
   - What hyperparameters can be configured?
   - What interactive tools exist (drawing points, tweaking weights, stepping epochs)?
3. **Target Audience**: Gauge whether the playground is targeted at beginners, undergraduate students, or advanced practitioners, and assess how well the default state serves that audience.

---

### Phase 2: Orchestrate Multi-Perspective Subagents

To ensure 360-degree coverage without repetitive overlap, spawn or divide responsibilities across specialized agent personas. Refer to [subagent_roles.md](./references/subagent_roles.md) for detailed persona prompts.

| Agent Persona | Primary Focus | Key Responsibilities |
| :--- | :--- | :--- |
| **1. First-Time User & Onboarding** | New User Experience | Onboarding flow, friction, unclear terminology, affordances, guided exploration. |
| **2. ML Student & Educator** | Pedagogical Value | Conceptual clarity, accuracy of explanations, intuition building, visualization utility. |
| **3. Experienced ML Practitioner** | Technical Rigor | Hyperparameter validity, statistical rigor, assumption checks, metric completeness. |
| **4. UX & Interaction Designer** | Interaction & Design | Information hierarchy, layout density, modal behavior, responsive states, cognitive load. |
| **5. Math & Functional Validator** | Correctness Verification | Independent calculation of metrics, confusion matrices, loss curves, numerical bounds. |
| **6. Exploratory Tester** | Non-Linear Pathways | Unusual configurations, rapid state transitions, re-runs, stale output detection. |
| **7. Visualization Specialist** | Visual Integrity | Chart scales, axis distortion, decision boundaries, color palette semantics, legend clarity. |
| **8. Product Gap Analyst** | Strategic Opportunities | Missing expected capabilities, workflow bottlenecks, high-value differentiators. |
| **9. Workflow Auditor** | End-to-End Tasks | Full lifecycle: select data → tune model → train → evaluate → compare → export. |
| **10. Adversarial Specialist** | Boundary & Stress Testing | Extreme inputs, rapid parameter scrubbing, invalid inputs, edge-case recovery. |

> **Runtime Fallback**: If parallel subagent spawning is unavailable in your environment, execute these 10 personas sequentially in a single session—grouping closely related perspectives (e.g., Onboarding + Educator, Math Validator + Adversarial) in deterministic order so all 10 lenses are still covered. If headless browser or DevTools automation is unavailable, run guided interactive checks where possible and record any unverified visual/interaction states in **Section H (Areas Not Fully Tested)** rather than reporting them as observed defects.

---

### Phase 3: Workflow Execution & Real Browser Interaction

Test complete, multi-step user workflows rather than isolated buttons:

1. **The End-to-End Experiment Lifecycle**:
   - Select or generate a dataset (e.g. non-linear separable, clusters, noisy sine wave).
   - Configure model hyperparameters (e.g. learning rate, polynomial degree, neighbors $k$, regularizer $\lambda$).
   - Execute training (step-by-step or continuous).
   - Inspect decision boundary, loss curves, confusion matrix, or regression fit.
   - Switch models (e.g. Logistic Regression $\to$ SVM $\to$ Decision Tree) and observe if dataset and configurations persist cleanly.
   - Modify hyperparameters post-run and verify if stale indicators or automatic updates occur.
2. **Explore Beyond the Happy Path**:
   - Zero, infinite, or boundary hyperparameter values (e.g. $k=1$, $k=N$, learning rate $= 0$, regularizer $= 0$).
   - Highly imbalanced, empty, single-point, or colinear datasets.
   - Rapidly switching algorithms mid-training or scrubbing sliders while animation runs.
   - Resetting experiments: Does state completely reset or does residual state leak into the next experiment?

---

### Phase 4: Independent Mathematical & Functional Verification

*Never trust the playground's displayed numbers without independent verification.*
Follow the 6-step verification process detailed in [verification_guide.md](./references/verification_guide.md):

1. **Identify the calculation**: What metric is shown (e.g., Accuracy, Precision, Recall, F1, Log-Loss, MSE, $R^2$, Silhouette Score)?
2. **Determine theoretical formulation**: Recall the canonical mathematical formula.
3. **Isolate a minimal test case**: Use a tiny synthetic dataset (e.g., 4–10 data points with known coordinates and labels).
4. **Independently calculate**: Derive the expected value using Python, pen-and-paper, or verified reference libraries.
5. **Compare**: Compare the playground's output against the ground truth using objective pass/fail criteria:
   - **Numeric Tolerance**: Allow a defined tolerance (e.g., `±1e-3` or the UI's displayed rounding precision, such as `±0.5` of the last displayed decimal place) so floating-point or rounding differences are not misclassified as a *Verified Mathematical Defect*.
   - **Determinism First**: Pin a deterministic random seed—or use a deterministic baseline (such as `k=1` KNN or fixed-centroid K-Means)—before flagging stochastic variance as a defect.
   - **Reproducible Evidence**: Every reported failure must attach the exact input dataset, full parameter/hyperparameter state, seed (if applicable), and expected vs. observed output.
6. **Detect Silent Failure Modes**:
   - Correct number, but wrong textual explanation.
   - Correct explanation, but miscalculated value.
   - Misleading visualization (e.g., non-square axes distorting distance in KNN/K-Means).
   - Sliders updated, but underlying model calculation remains cached/stale.
   - Decision boundary renders for training set without reflecting test set generalization.

---

### Phase 5: Synthesis & Actionable Prioritization

1. **Deduplicate**: Merge overlapping observations from multiple agents into single, high-impact findings.
2. **Classify by Finding Taxonomy**:
   - **Observed Defect**: Demonstrable functional failure or broken UI state.
   - **Verified Mathematical Defect**: Calculated value or visualization proven mathematically incorrect.
   - **Observed UX Friction**: Interaction, cognitive load, or workflow breakdown experienced firsthand.
   - **Product Opportunity**: Strategic capability or ergonomic improvement that solves observed user friction.
   - **Unverified Suspicion**: Potential problem that could not be fully verified (explicitly isolated).
3. **Prioritize by Severity**: Apply the P0–P4 severity framework.
4. **Compile Deliverables**: Format into the standard report specified in [report_template.md](./references/report_template.md).

---

## Severity & Prioritization Matrix

| Severity | Level | Definition | Playground Examples |
| :--- | :--- | :--- | :--- |
| **P0** | **Critical** | Product is unusable, fundamentally crashes, or outputs catastrophic mathematical errors that defeat its purpose. | App hangs indefinitely on training; loss is negative for cross-entropy; decision boundary completely inverted. |
| **P1** | **High** | Major feature, workflow, visualization, or metric is broken or severely misleading. | Metrics display training score labeled as test score; KNN distance distorted by unscaled axes; stale results displayed after parameter change. |
| **P2** | **Medium** | Meaningful UX friction, secondary functional flaw, or missing essential contextual cues. | No loading indicator during long computation; confusion matrix missing axis labels; resetting algorithm wipes custom dataset without warning. |
| **P3** | **Low** | Minor usability, layout polish, typography, or cosmetic inconsistency. | Tooltip alignment glitch; color contrast slightly low on inactive slider; minor decimal rounding inconsistency. |
| **P4** | **Opportunity** | High-value capability, pedagogical enhancement, or workflow simplification. | Add side-by-side model comparison; add interactive data point drag-and-drop; export experiment state as reproducible URL. |

---

## Evidence & Finding Schema

Every recorded finding must strictly follow this structure:

```markdown
### [FINDING-ID] <Concise, Descriptive Title>

- **Category**: Functional | UX & Interaction | Mathematical Correctness | Visualization | Educational | Product Gap
- **Severity**: P0 | P1 | P2 | P3 | P4
- **Location**: <Screen, Tab, Workflow, or Specific Control>
- **Confidence**: High | Medium | Low
- **User Perspective**: <What the user was attempting to achieve>
- **Observation**: <What actually happened during interaction>
- **Why It Matters**: <Impact on learning, usability, trust, or correctness>
- **Independent Verification**: <Ground-truth derivation, expected formula, or N/A>
- **Recommendation**: <Concrete, actionable remediation>
- **Reproducibility & Steps**:
  1. Go to ...
  2. Configure ...
  3. Click ...
  4. Observe ...
- **Evidence**: <Visual description, exact values, coordinates, or screenshots>
```

---

## Final Deliverables Structure

Consolidate findings into the comprehensive report structured as follows:

- **Section A: Executive Summary**: Candid assessment of product maturity, core strengths, critical liabilities, and strategic verdict.
- **Section B: Critical Findings (P0 / P1)**: Exhaustive breakdown of blockers with full proof and reproduction steps.
- **Section C: UX and Product Findings**: Concrete friction categorized by workflow and interaction pattern.
- **Section D: Functional and Mathematical Correctness**: Verified defects vs unverified suspicions with mathematical derivations.
- **Section E: Product Opportunities**: High-leverage features grounded in observed user pain points.
- **Section F: Prioritized Action Plan**: Grouped into *1. Fix Immediately*, *2. Fix Next*, *3. Improve When Practical*, and *4. Strategic Opportunities* with estimated complexity.
- **Section G: Detailed Findings Appendix**: Full catalog of all deduplicated findings matching the evidence schema.
- **Section H: Areas Not Fully Tested**: Explicit documentation of boundary configurations, algorithms, or browsers that were outside audit scope.

---

## Verification & Audit Checklist

Before delivering the audit report, verify:

- [ ] All reported defects were observed through real visual/interactive workflows, not inferred solely from static code.
- [ ] Every mathematical or statistical claim has an independent proof or derivation attached.
- [ ] Duplicate findings across subagents have been merged into cohesive, prioritized items.
- [ ] Every recommendation contains concrete UI/code guidance, avoiding vague generalities ("make it better").
- [ ] No P4 opportunity is suggested merely because "other tools have it"—every opportunity must resolve observed user friction.
- [ ] Unverified suspicions are clearly segregated from verified defects.
- [ ] The final report matches all sections of [report_template.md](./references/report_template.md).
