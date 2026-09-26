---
name: fix-mutations
description: Find and fix survived PIT mutation tests. Run after `make install` to identify mutations that survived and fix the tests (or source code) so they are killed. Iterates through batches of 10 survived mutations until none remain.
version: 1.0.0
---

# Fix Survived Mutations

Automates the process of finding and resolving survived PIT mutation tests across all modules in the Trishul monorepo. Survived mutations indicate that the test suite does not adequately cover the mutated edge case.

## Prerequisites

- A successful `make install` build must have run recently so that `modules/*/target/pit-reports/mutations.xml` files exist.
- If no `mutations.xml` files exist, run `make install` first.

## Workflow

### Phase 1: Discover Survived Mutations

Run the following command to fetch the next batch of 10 survived mutations:

```bash
(echo "<mutations>"; xmllint modules/*/target/pit-reports/mutations.xml | grep -v 'status="KILLED"' | head -n <COUNT> | tail -n 10; echo "</mutations>") | xmllint --format -
```

- Start with `<COUNT>=10` for the first batch.
- Increment `<COUNT>` by 10 for each subsequent batch (20, 30, 40, ...).
- When incrementing no longer produces new mutations (output is identical to the previous batch), all mutations have been processed.

### Phase 2: Parse Each Mutation

Each `<mutation>` XML element contains:

| Field | Description |
|---|---|
| `sourceFile` | The Java source file containing the mutated code |
| `mutatedClass` | Fully qualified class name that was mutated |
| `mutatedMethod` | The method that was mutated |
| `lineNumber` | Line number of the mutation |
| `mutator` | The PIT mutator type (e.g., `NullReturnValsMutator`, `VoidMethodCallMutator`, `NegateConditionalsMutator`, `ConditionalsBoundaryMutator`, `BooleanTrueReturnValsMutator`) |
| `description` | Human-readable description of what the mutation did |

### Phase 3: Fix Each Mutation

For each survived mutation:

1. **Locate the source file** using the `mutatedClass` field. The source file lives under `modules/<module>/src/main/java/...`.

2. **Locate the existing test file** named `<ClassName>Test.java` in the corresponding `src/test/java/...` directory. If no test file exists, create one following existing test patterns.

3. **Understand the mutation**:
   - `NullReturnValsMutator` / `EmptyObjectReturnValsMutator`: A method's return value was replaced with `null` or empty. The test must assert the return value is not null and equals the expected value (e.g., `assertSame(instance, instance.someMethod(...))` for builder-pattern methods).
   - `VoidMethodCallMutator`: A void method call was removed. The test must verify the method was called (e.g., `verify(mock).methodCall(...)` or use `InOrder` verification).
   - `NegateConditionalsMutator`: A conditional was negated (`==` → `!=`, `<` → `>=`). The test must cover both branches of the conditional.
   - `ConditionalsBoundaryMutator`: A boundary condition was changed (`<` → `<=`, `>` → `>=`). The test must include boundary values.
   - `BooleanTrueReturnValsMutator` / `BooleanFalseReturnValsMutator`: A boolean return was replaced. The test must verify both `true` and `false` return cases.
   - `MathMutator`: An arithmetic operator was changed. The test must verify the exact result.

4. **Fix the root cause, not the symptom**:
   - If the source code has a pattern like `size() > 0`, refactor it to `!isEmpty()` to make it immune to boundary mutations.
   - If a builder method returns `this`, assert `assertSame(builder, builder.someMethod(...))`.
   - If a debug/logging method is being called, verify it via mock interactions.
   - If a test has a copy-paste bug (e.g., asserting the wrong variable), fix the assertion target.

5. **Follow coding conventions**:
   - Use static imports for JUnit and Mockito methods (`import static org.junit.jupiter.api.Assertions.*`, `import static org.mockito.Mockito.*`).
   - Never use full classpath references like `org.junit.jupiter.api.Assertions.assertNotEquals(...)` inline — always import.
   - Follow existing test patterns in the module.
   - Don't use reflection unless absolutely necessary.
   - Don't create bulk refactor scripts.

### Phase 4: Verify Batch

After fixing all mutations in a batch, run the affected modules' tests:

```bash
docker-compose --env-file mvn.env -f docker-compose-bin.yml run --rm --remove-orphans mvn mvn test -pl modules/<module1>,modules/<module2>,...
```

If tests fail, fix the compilation or logic errors and re-run.

### Phase 5: Iterate

Increment `<COUNT>` by 10 and repeat Phases 1–4 until no new mutations appear.

### Phase 6: Final Verification

Run a full build to confirm everything passes:

```bash
make install
```

This builds all modules with `clean install`, running all tests and PIT mutation coverage.

### Phase 7: Confirm Zero Survivors

After `make install` completes, verify zero survived mutations remain:

```bash
xmllint modules/*/target/pit-reports/mutations.xml | grep -v -c 'status="KILLED"'
```

If the count is `0`, the goal is complete.

## Common Mutation Fix Patterns

### Builder/fluent method returns `this`
```java
// Source: returns this
public Builder setFoo(String foo) { this.foo = foo; return this; }

// Test: assert same instance returned
assertSame(builder, builder.setFoo("value"));
```

### Void method call removed
```java
// Source: calls connection.commit()
connection.commit();

// Test: verify in order
InOrder order = inOrder(mock1, mock2, connection);
order.verify(connection).commit();
```

### Conditional boundary `> 0` → `>= 0`
```java
// Source (bad pattern — vulnerable to boundary mutation):
if (list.size() > 0) { ... }

// Fix source to be mutation-immune:
if (!list.isEmpty()) { ... }
```

### Boolean return replaced with `true`
```java
// Test must cover the false case:
doReturn(false).when(mockRepo).exists(id);
assertFalse(service.exists(id));
```

### Null return value
```java
// Test must assert non-null and correct value:
DeleteResult result = service.delete(id);
assertNotNull(result);
assertEquals(expectedResult, result);
```

## Tips

- Fix one mutation at a time. Don't batch unrelated changes.
- After fixing, always compile and run tests before moving on.
- If a mutation is in a debug/logging method that has no observable side effect, consider whether the method itself should be removed or if a `verify()` assertion is appropriate.
- Use `assertSame` for builder-pattern return values, `assertEquals` for value comparisons.
