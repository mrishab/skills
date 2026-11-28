# Java / Spring SonarQube Rules Reference

This document provides architectural rationale, conditional evaluation criteria, and remediation examples for SonarQube static analysis in Java and Spring Boot projects.

The canonical machine-readable rule mapping lives in [rules.json](./rules.json) (consumed by `scripts/fetch_sonar_issues.py`). Project-specific overrides can be placed in a repo-local `.sonar-triage.json` file at the project root rather than modifying the shared skill rules.

---

## 1. Architectural Patterns to PRESERVE (DO NOT MODIFY)

These SonarQube rules often report false positives against established Java / Spring design patterns. Attempting to "fix" these violations breaks compilation, annotation processing, mapper code generation, or API contracts.

| Rule ID | Rule Name | Architecture Context & Rationale |
|---|---|---|
| `java:S3252` | Static member accessed via subclass | **CRITICAL - DO NOT CHANGE**: MapStruct and annotation processors often require static constants (e.g. `ConcreteEntity.ID_FIELD`) to be referenced directly through the concrete class rather than a base interface. Changing this breaks mapper code generation. |
| `java:S119` | Type parameter naming convention | Generic type parameters (e.g. `T extends AbstractEntity<T>`, `E extends BaseModel<ID, E>`, `ID`, `R`) define domain model and repository hierarchies. Renaming breaks public API contracts and polymorphism. |
| `java:S1135` / `xml:S1135` | Track uses of "TODO" tags | TODO comments must remain until their associated feature or fix is actually implemented. Never delete or comment out TODO comments merely to satisfy static analysis. |
| `java:S1874` / `java:S1123` | Deprecated code usage | Deprecated methods and tags are intentionally preserved to ensure binary and source backward compatibility for existing consumers until major release milestones. |
| `java:S1602` | Remove lambda expression block braces | In multi-overloaded functional interfaces, explicit braces `{ return ...; }` are required to disambiguate overloaded methods (e.g. `Supplier` vs `Consumer`). Removing braces causes compiler failures (`reference is ambiguous`). |
| `java:S2160` | Subclasses adding fields should override equals | DTOs, models, or entities extending a base reflection/identity class rely on the base class's `equals`, `hashCode`, and `toString`. Adding boilerplate overrides across models creates unnecessary noise and breaks uniformity. |
| `java:S6548` | "Singleton" pattern should not be used | Framework constants, mapper instances, and fallback/default entities intentionally use singleton instances. |

---

## 2. Conditional Exceptions (Evaluate Context Before Fixing or Preserving)

Do **not** blanket-ignore these rules in Spring Boot production services. Preserve them only when the specific architectural condition below applies:

| Rule ID | Rule Name | When to Preserve vs. Fix |
|---|---|---|
| `java:S3011` | Reflection accessibility bypass (`setAccessible`) | **Preserve** only inside test fixtures or dedicated low-level reflection/serialization utilities. **Fix** in Spring Boot production services, where bypassing access checks is a security and encapsulation risk. |
| `java:S106` | Standard output usage (`System.out` / `System.err`) | **Preserve** only in CLI entrypoints, standalone tools, or migration runners. **Fix** in Spring Boot services by replacing with an SLF4J logger. |
| `java:S1172` | Unused method parameters | **Preserve** only when required by a polymorphic interface, framework interceptor, or controller signature. **Fix** on private or non-contract methods by removing the unused parameter. |

---

## 3. Actionable Code Smells to FIX (ALWAYS ADHERE TO)

These rules identify genuine code smells, memory leaks, concurrency bugs, and dead code. They should always be remediated when discovered.

### Concurrency & Lifecycle Rules

#### `java:S2142`: "InterruptedException" should not be ignored
- **Problem**: Catching `InterruptedException` without restoring the interrupted flag causes calling threads or thread pools to lose cancellation state.
- **Fix**: Call `Thread.currentThread().interrupt();` inside the catch block before wrapping and rethrowing.
- **Testing Guardrail**: In unit tests, assert `assertTrue(Thread.currentThread().isInterrupted())` and clean up with `Thread.interrupted()` in `finally`.
```java
// ❌ BAD
} catch (InterruptedException e) {
  throw new RuntimeException(e);
}

// ✅ GOOD
} catch (InterruptedException e) {
  Thread.currentThread().interrupt();
  throw new RuntimeException(String.format("Task interrupted: %s", e.getMessage()), e);
}
```

#### `java:S5164`: "ThreadLocal" variables should be cleaned up
- **Problem**: ThreadLocal instances in thread-pooled environments (like web servers or connection managers) cause severe memory leaks and cross-request context pollution.
- **Fix**: Always call `.remove()` on ThreadLocal objects in a `finally` block or when releasing context.
```java
// ✅ GOOD
try {
  localCache.set(data);
  process();
} finally {
  localCache.remove();
}
```

---

### Dead Code & Simplification Rules

#### `java:S1068` & `java:S1481`: Unused private fields & local variables
- **Fix**: Safely delete dead fields and variables that have no reads.

#### `java:S1144`: Unused private methods
- **Fix**: Delete unused private methods.

#### `java:S1488`: Immediately returned local variable
- **Fix**: Inline the expression directly into the `return` statement.
```java
// ❌ BAD
User user = repository.findById(id);
return user;

// ✅ GOOD
return repository.findById(id);
```

#### `java:S1155`: Collection.isEmpty() should be used instead of size()
- **Fix**: Replace `.size() == 0` or `.size() > 0` with `.isEmpty()` or `!collection.isEmpty()`. This also makes code immune to boundary mutations.

#### `java:S2129`: Primitive / Boxed Constructors
- **Fix**: Replace `new Long(x)` or `new String(s)` with `Long.valueOf(x)` or string literals.

#### `java:S1161`: Missing `@Override` annotation
- **Fix**: Add `@Override` to methods implementing interface contracts or superclass methods.

#### `java:S3776`: Cognitive Complexity
- **Fix**: Refactor complex nested if/else statements by introducing guard clauses, helper methods, or Java stream pipelines.

#### `java:S125`: Commented-out code
- **Fix**: Remove dead commented-out code blocks (git history preserves previous implementations).
