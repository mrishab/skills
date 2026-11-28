---
name: fix-sonarqube
description: Fetch, triage, and resolve SonarQube issues in Java and Spring Boot projects while preserving core architectural patterns. Use when reviewing SonarQube analysis, cleaning code smells, or resolving static analysis violations.
version: 1.0.0
---

# Fix SonarQube Issues

Automates the fetching, triaging, and remediation of SonarQube code smells and bugs in Java and Spring Boot projects without regressing established architectural patterns.

## When to Activate

- **Activate when**:
  - The user requests to review, clean, or fix issues reported by SonarQube.
  - The user provides a SonarQube server URL or points to static analysis reports / code smells / technical debt.
  - A post-feature audit is required to clean up unused variables, cognitive complexity, or exception handling.
- **Do NOT activate when**:
  - Fixing PIT mutation test survivors (use `fix-mutations` instead).
  - Writing new domain APIs or components from scratch.

---

## Triage Philosophy: Actionable vs Preserved

Spring and Java framework architectures often employ specific design idioms that trigger false-positive SonarQube rules. **Never sacrifice architecture to satisfy SonarQube.**

Rule categorizations (`preserved_rules`, `conditional_rules`, and `actionable_rules`) are defined in a single canonical file: [rules.json](./references/rules.json) (which can be extended per repository via an optional `.sonar-triage.json` file in the project root). Consult [rules_reference.md](./references/rules_reference.md) for full architectural rationale, conditional criteria, and remediation examples.

- **Preserved rules**: Intentional framework/API patterns (e.g., `java:S3252`, `java:S119`, `java:S1135`, `java:S1874`, `java:S1602`, `java:S2160`, `java:S6548`)—do not modify.
- **Conditional rules**: Context-dependent rules (e.g., `java:S3011`, `java:S106`, `java:S1172`)—preserve only in valid contexts such as test fixtures, CLI entrypoints, or polymorphic framework contracts; fix in production services.
- **Actionable rules**: Genuine code smells, resource leaks, and concurrency bugs (e.g., `java:S2142`, `java:S5164`, `java:S3776`, `java:S1068`/`S1481`)—always remediate.

> **Safety Guardrail — No Blind Suppressions**: Never add `@SuppressWarnings(...)`, `// NOSONAR`, or `sonar.exclusions` entries as a shortcut to make SonarQube green. If a rule genuinely cannot be fixed safely without breaking public contracts or framework behavior, document the technical justification and ask the user before suppressing or marking Won't Fix.

---

## Workflow & Step-by-Step Instructions

### Step 1: Fetch and Triage Issues
Run the helper script from the skill directory or repository:

```bash
python3 scripts/fetch_sonar_issues.py --format summary
```

To list only actionable issues formatted as a Markdown table:
```bash
python3 scripts/fetch_sonar_issues.py --actionable-only
```

*(Alternatively, fetch directly via curl using SonarQube credentials:)*
```bash
AUTH=$(echo -n "${SONARQUBE_TOKEN}:" | base64)
curl -s -H "Authorization: Basic ${AUTH}" \
  "${SONARQUBE_HOST_URL}/api/issues/search?componentKeys=${SONARQUBE_PROJECT_KEY}&issueStatuses=OPEN,CONFIRMED&ps=100"
```

### Step 2: Analyze & Filter
1. Review the generated list of issues.
2. Confirm that none of the candidates match `preserved_rules` in [rules.json](./references/rules.json) or valid `conditional_rules` contexts.
3. If an issue is conditional (e.g., `java:S1172`, `java:S3011`, `java:S106`), verify the call site and context before deciding to fix or preserve.

### Step 3: Implement Targeted Fixes
1. Open the target file and apply the minimal, clean fix (never using `@SuppressWarnings(...)`, `// NOSONAR`, or `sonar.exclusions` as a shortcut).
2. Never introduce fully qualified class names directly in Java code (use imports and static imports).
3. If modifying exception handling for `InterruptedException`, always restore the interrupt flag:
   ```java
   } catch (InterruptedException e) {
     Thread.currentThread().interrupt();
     throw new RuntimeException(e);
   }
   ```
4. If testing `InterruptedException` handling, assert `assertTrue(Thread.currentThread().isInterrupted())` and reset in `finally { Thread.interrupted(); }`.

### Step 4: Verify Module Compilation & Tests
Run compilation and tests for the affected modules:

```bash
# Maven
mvn test-compile -pl <module>
mvn test -pl <module>

# Gradle fallback
./gradlew :<module>:test
```

### Step 5: Full Build Verification
After all actionable fixes are applied, verify the build passes cleanly:

```bash
# Maven
mvn clean verify

# Gradle fallback
./gradlew check
```

---

## Verification Checklist

- [ ] All modified modules compile cleanly with zero errors.
- [ ] No MapStruct static constant references (`java:S3252`) were modified.
- [ ] No generic type parameters (`java:S119`) were renamed.
- [ ] No TODO comments (`java:S1135`) were removed without actual implementation.
- [ ] All `InterruptedException` catch blocks restore the interrupt status and unit tests assert `isInterrupted()`.
- [ ] Unit tests and static checks pass cleanly.
