---
name: fix-mutations
description: Find and fix survived PIT mutation tests. Run after `make install` to identify mutations that survived and fix the tests (or source code) so they are killed. Iterates through batches of 10 survived mutations until none remain.
version: 1.0.0
---

# Fix Survived Mutations

Workflow for resolving survived PIT mutation tests in the Trishul monorepo.

## Prerequisite
Run `make install` first so `modules/*/target/pit-reports/mutations.xml` exists.

## The Loop

### 1. Fetch Next Batch of 10 Mutations
```bash
(echo "<mutations>"; xmllint modules/*/target/pit-reports/mutations.xml | grep -v 'status="KILLED"' | head -n <COUNT> | tail -n 10; echo "</mutations>") | xmllint --format -
```
*Start with `<COUNT>=10`, then increment by 10 (20, 30, ...) each iteration until no new mutations appear.*

### 2. Common Mutators & Fixes

| Mutator | Behavior | Fix |
| :--- | :--- | :--- |
| `NullReturnVals` / `EmptyObject` | Return replaced with null/empty | Assert return is non-null and matches expected |
| `VoidMethodCall` | Method call removed | Add `verify(mock).method(...)` or `InOrder` check |
| `NegateConditionals` | Condition flipped (`==` → `!=`) | Add tests covering both true/false branches |
| `ConditionalsBoundary` | Boundary shifted (`<` → `<=`) | Add boundary edge-case tests, or refactor `size() > 0` to `!isEmpty()` |
| `BooleanTrue/FalseReturn` | Boolean return forced | Add tests asserting both boolean outcomes |
| `MathMutator` | Operator swapped (`+` → `-`) | Assert exact calculated result |

### 3. Conventions
- Locate source at `modules/<module>/src/main/java/...` and test at `src/test/java/...`.
- Use static imports: `import static org.junit.jupiter.api.Assertions.*`, `import static org.mockito.Mockito.*`.
- For builder methods returning `this`, assert `assertSame(builder, builder.someMethod(...))`.

### 4. Verify Batch
```bash
docker-compose --env-file mvn.env -f docker-compose-bin.yml run --rm --remove-orphans mvn mvn test -pl modules/<module1>,modules/<module2>
```

### 5. Final Confirmation
Run full build and verify zero survivors:
```bash
make install
xmllint modules/*/target/pit-reports/mutations.xml | grep -v 'status="KILLED"' | grep '<mutation' | wc -l
```
*Expected: 0*
