# ML Playground Audit Report Template

Use this markdown skeleton to structure the final consolidated audit deliverable. Every section from A through H must be populated.

---

```markdown
# Deep Product, UX, and Functional Audit: <Playground Name>

- **Date of Audit**: YYYY-MM-DD
- **Target Application**: <URL or Local Path>
- **Auditing Framework**: `ml-playground-audit`
- **Subagents Orchestrated**: <Count, e.g. 10 specialized agents>
- **Audit Verdict**: [Production Ready | Needs Critical Remediation | Exploratory Alpha]

---

## A. Executive Summary

### 1. Overall Product Quality Assessment
<Concise 2–3 paragraph summary assessing whether the application fulfills its core value proposition: enabling users to experiment with machine learning and intuitively understand what they observe.>

### 2. Core Strengths
- **Strength 1**: <Description>
- **Strength 2**: <Description>
- **Strength 3**: <Description>

### 3. Biggest Weaknesses & Liabilities
- **Liability 1**: <Description>
- **Liability 2**: <Description>

### 4. Most Concerning Functional & Mathematical Defects
- <Bullet points highlighting P0/P1 mathematical or state flaws>

### 5. Most Urgent UX Friction Points
- <Bullet points highlighting primary cognitive friction or workflow disconnections>

### 6. High-Leverage Strategic Opportunities
- <Top product capabilities that would dramatically elevate user retention and delight>

---

## B. Critical Findings (P0 & P1)

*Exhaustive breakdown of critical issues that break workflows, crash the application, or deliver fundamentally incorrect ML results.*

### [CRIT-01] <Title>
- **Category**: Functional | Mathematical Correctness | Visualization
- **Severity**: P0 / P1
- **Location**: <Screen / Control>
- **User Perspective**: <User intent>
- **Observation**: <What actually happened>
- **Why This Matters**: <Impact>
- **Independent Verification**: <Proof or mathematical derivation>
- **Recommendation**: <Concrete code or UI fix>
- **Reproducibility**:
  1. Step 1...
  2. Step 2...
- **Evidence**: <Logs, values, or visual description>

---

## C. UX and Product Findings

*Organized by feature, screen, or user journey.*

### 1. Onboarding & First-Time Experience
- **[UX-01] <Title>**: <Observation, impact, recommendation>

### 2. Configuration & Parameter Ergonomics
- **[UX-02] <Title>**: <Observation, impact, recommendation>

### 3. Interaction & Visual Feedback
- **[UX-03] <Title>**: <Observation, impact, recommendation>

### 4. Workflow Continuity & State Transitions
- **[UX-04] <Title>**: <Observation, impact, recommendation>

---

## D. Functional and Mathematical Correctness Findings

### 1. Independently Verified Mathematical Defects
*Calculated values or formulas proven mathematically incorrect through external derivations.*

| Finding ID | Metric / Feature | Displayed Value | Ground Truth Value | Discrepancy & Mathematical Proof |
|---|---|---|---|---|
| **[MATH-01]** | Precision Calculation | `0.85` | `0.67` | Inverted false positive and false negative counts. |

### 2. Visualization & Geometric Inconsistencies
*Distorted axes, aspect-ratio scaling flaws, or inaccurate boundary contours.*

- **[VIZ-01] <Title>**: <Description, distortion analysis, fix>

### 3. State Synchronization & Staleness Issues
*Mismatches between current parameters/data and rendered outputs.*

- **[STALE-01] <Title>**: <Description, trigger condition, fix>

### 4. Unverified Suspicions
*Behaviors that appear anomalous or inconsistent but could not be definitively mathematically proven.*

- **[SUSP-01] <Title>**: <Observation, suspected cause, recommended investigation method>

---

## E. Product Opportunities (P4)

*High-value product capabilities and workflow simplifications rooted in observed user friction.*

### 1. [OPP-01] <Title>
- **Observed User Friction**: <Why this feature is needed>
- **Proposed Capability**: <Detailed product proposal>
- **Expected Impact**: <Impact on learning, engagement, or differentiation>
- **Implementation Complexity**: Low | Medium | High

---

## F. Prioritized Action Plan

### 1. Fix Immediately (P0 & Critical P1)
| Priority | Issue / Defect | Recommended Action | Impact | Complexity |
|---|---|---|---|---|
| **P0** | | | Eliminates runtime crash | Low |
| **P1** | | | Restores metric accuracy | Medium |

### 2. Fix Next (P1 & Severe P2)
| Priority | Issue / Defect | Recommended Action | Impact | Complexity |
|---|---|---|---|---|
| **P1** | | | Fixes aspect ratio distortion | Low |
| **P2** | | | Adds stale results warning | Low |

### 3. Improve When Practical (P2 & P3)
| Priority | Issue / Defect | Recommended Action | Impact | Complexity |
|---|---|---|---|---|
| **P2** | | | Improves empty states | Medium |
| **P3** | | | Polishes slider grab handle | Low |

### 4. Strategic Product Opportunities (P4)
| Opportunity | Description | Value Proposition | Complexity |
|---|---|---|---|
| Side-by-side comparison | Compare 2 models on same data | Eliminates memory burden | High |

---

## G. Detailed Findings Appendix

*Consolidated catalog of all deduplicated findings with complete schema.*

### [ALL-01] ...
### [ALL-02] ...

---

## H. Areas Not Fully Tested

*Explicit boundaries of what was not covered during this audit session.*

- **Uncovered Algorithms**: <List any models not tested>
- **Unchecked Boundary Inputs**: <List parameters not pushed to infinity or zero>
- **Browser/Environment Matrix**: <List platforms or viewport sizes not audited>
```
