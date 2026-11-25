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
(echo "<mutations>"; grep -E "status=['\"](SURVIVED|NO_COVERAGE)['\"]" modules/*/target/pit-reports/mutations.xml | head -n <COUNT> | tail -n 10; echo "</mutations>") | xmllint --format -
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

### 4. Advanced Fix Patterns

#### Restoring Thread Interrupted Flag
```java
// Source:
} catch (InterruptedException e) {
  Thread.currentThread().interrupt();
  throw new RuntimeException(String.format(ERR_MSG_TASK_EXECUTION, e.getMessage()), e);
}

// Test: assert thread interrupt status and clear in finally
@Test
void testInterrupted() {
  Thread.currentThread().interrupt();
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
// Fix: Inline parameter parsing or always initialize a collection without null checks to make the code mutation-immune.
```

### 5. Verify Batch
```bash
mvn test -pl modules/<module1>,modules/<module2>
```

### 6. Final Confirmation
Run full build and verify zero survivors:
```bash
grep -h -E "status=['\"](SURVIVED|NO_COVERAGE)['\"]" modules/*/target/pit-reports/mutations.xml | wc -l
```
*Expected: 0*
