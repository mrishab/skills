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

### 🚫 Rules to PRESERVE (DO NOT TOUCH)
| Rule ID | Pattern | Why It Must Not Be Changed |
|---|---|---|
| `java:S3252` | `Entity.ATTR_ID` | MapStruct and annotation processors often require static entity constants to be referenced through concrete classes, not interfaces. |
| `java:S119` | Generic types (`<T extends Base<T>>`, `<ID, E>`) | Standardized domain hierarchies and polymorphic entity contracts. |
| `java:S1135` | `// TODO` | Policy strictly forbids deleting TODO comments; only remove when implemented. |
| `java:S1874` | `@Deprecated` | Preserved for API consumer backward compatibility until major release milestones. |
| `java:S1602` | Lambda `{ return ...; }` | Disambiguates overloaded functional interfaces (e.g. `CheckedSupplier` vs `CheckedConsumer`). |
| `java:S3011` | Reflection access | Dynamic reflection utilities, serializers, and entity copiers require reflection access by design. |
| `java:S2160` | `equals` in DTOs / Models | Base model classes handle reflection-based or identity equality for all subclasses. |
| `java:S6548` | `INSTANCE` Singleton | Used for immutable constants, mappers, or fallback instances. |
| `java:S1172` | Unused parameters | Polymorphic interface, framework interceptor, or controller contracts required for framework signatures. |

### ✅ Rules to FIX (Always Adhere To)
- `java:S1068` / `java:S1481`: Unused private fields & local variables.
- `java:S1144`: Unused private methods.
- `java:S1488`: Immediately returned local variables (inline return).
- `java:S3776`: Cognitive complexity (extract guard clauses or helper methods).
- `java:S2142`: `InterruptedException` handling (call `Thread.currentThread().interrupt()`).
- `java:S5164`: `ThreadLocal` cleanup (call `remove()` in `finally`).
- `java:S1161`: Missing `@Override` annotation.
- `java:S1155`: Replace `.size() == 0` / `.size() > 0` with `.isEmpty()` / `!isEmpty()`.
- `java:S2129`: Replace `new Long(...)` / `new String(...)` with `valueOf` or literals.
- `java:S125`: Remove dead commented-out code.

For complete rationale on every rule, consult [rules_reference.md](./references/rules_reference.md).

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
2. Confirm that none of the candidates match the **Preserved Rules** table above.
3. If an issue is on an interface or polymorphic method (e.g. `java:S1172`), verify if removing the parameter would break callers or interface contracts.

### Step 3: Implement Targeted Fixes
1. Open the target file and apply the minimal, clean fix.
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
mvn test-compile -pl <module>
mvn test -pl <module>
```

### Step 5: Full Build Verification
After all actionable fixes are applied, verify the build passes cleanly:

```bash
mvn clean verify
```

---

## Verification Checklist

- [ ] All modified modules compile cleanly with zero errors.
- [ ] No MapStruct static constant references (`java:S3252`) were modified.
- [ ] No generic type parameters (`java:S119`) were renamed.
- [ ] No TODO comments (`java:S1135`) were removed without actual implementation.
- [ ] All `InterruptedException` catch blocks restore the interrupt status and unit tests assert `isInterrupted()`.
- [ ] Unit tests and static checks pass cleanly.
