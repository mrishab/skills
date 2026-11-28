---
name: fix-mutations
description: Find and fix survived PIT mutation tests. Run after `make install` to identify mutations that survived and fix the tests (or source code) so they are killed. Iterates through batches of 10 survived mutations until none remain.
version: 1.0.0
---

# Fix Survived Mutations

Workflow for resolving survived PIT mutation tests in Java / Spring multi-module projects.

## Prerequisite
Run `make install` (or your project's mutation testing target) first so `modules/*/target/pit-reports/mutations.xml` (or `target/pit-reports/mutations.xml`) exists.

## The Loop

### 1. Fetch Next Batch of 10 Mutations
```bash
(echo "<mutations>"; for f in modules/*/target/pit-reports/mutations.xml target/pit-reports/mutations.xml; do [ -f "$f" ] && xmllint --xpath "//mutation[@status='SURVIVED' or @status='NO_COVERAGE']" "$f" 2>/dev/null; done; echo "</mutations>") \
  | (echo "<mutations>"; xmllint --xpath "//mutation[position() > <OFFSET> and position() <= <COUNT>]" - 2>/dev/null; echo "</mutations>") \
  | xmllint --format -
```
*Start with `<OFFSET>=0`, `<COUNT>=10`, then increment both by 10 (`10`/`20`, `20`/`30`, ...) each iteration until no new mutations appear.*

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

### 4. Advanced Fix Patterns

#### Restoring Thread Interrupted Flag
```java
// Source:
} catch (InterruptedException e) {
  Thread.currentThread().interrupt();
  throw new RuntimeException(String.format(ERR_MSG_TASK_EXECUTION, e.getMessage()), e);
}

// Test: mock the blocking dependency to throw InterruptedException (do NOT pre-interrupt the thread,
// or VoidMethodCallMutator on Thread.currentThread().interrupt() will not be killed), assert the
// interrupt flag is restored, and clear it in finally so state does not leak to other tests.
@Test
void testInterrupted() throws Exception {
  when(dependency.call()).thenThrow(new InterruptedException("interrupted"));
  try {
    RuntimeException exception = assertThrows(RuntimeException.class, () -> service.run());
    assertTrue(exception.getCause() instanceof InterruptedException);
    assertTrue(Thread.currentThread().isInterrupted());
  } finally {
    Thread.interrupted();
  }
}
```

#### Empty Object on Collection/Map Helper Returning Null
```java
// Vulnerable: parseParameters returns null on missing/non-object parameters, and caller branches `if (parameters != null)`
// PIT replaces `return null;` with `Collections.emptyMap()`, and caller produces identical behavior.
// Fix: Always return an empty collection/map (Effective Java Item 54) from the helper and remove redundant caller null checks—avoid inlining helper logic, which duplicates parsing across callers.
```

### 5. Verify Batch
```bash
mvn test -pl modules/<module1>,modules/<module2>
```

### 6. Final Confirmation
Re-run the full mutation testing build so `mutations.xml` is regenerated, then verify zero survivors:
```bash
make install  # or: mvn test-compile org.pitest:pitest-maven:mutationCoverage
for f in modules/*/target/pit-reports/mutations.xml target/pit-reports/mutations.xml; do
  [ -f "$f" ] && xmllint --xpath "count(//mutation[@status='SURVIVED' or @status='NO_COVERAGE'])" "$f" 2>/dev/null
done | awk '{sum += $1} END {print sum+0}'
```
*Expected: 0*
