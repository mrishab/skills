# Java / Spring SonarQube Rules Reference

This document codifies the triage rules for static code analysis in Java and Spring Boot projects. It explicitly defines which SonarQube rules should typically be **preserved** (ignored as intentional architectural design patterns) and which rules must be **adhered to** (fixed).

---

## 1. Architectural Patterns to PRESERVE (DO NOT MODIFY)

These SonarQube rules often report false positives against established Java / Spring design patterns. Attempting to "fix" these violations breaks compilation, annotation processing, mapper code generation, API contracts, or testing harnesses.

| Rule ID | Rule Name | Architecture Context & Rationale |
|---|---|---|
| `java:S3252` | Static member accessed via subclass | **CRITICAL - DO NOT CHANGE**: MapStruct and annotation processors often require static entity constants (e.g. `ATTR_ID`, `ATTR_VERSION`) to be referenced directly through the concrete entity class (`User.ATTR_ID`), not the base interface (`Identified.ATTR_ID`). Changing this breaks MapStruct mapper generation or violates canonical mapper patterns. |
| `java:S119` | Type parameter naming convention | Core generic type parameters (e.g. `T extends BaseEntity<T>`, `E extends CrudEntity<ID, E>`, `ID`, `R`) define domain model and repository hierarchies. Renaming breaks public API contracts and framework polymorphism. |
| `java:S1135` / `xml:S1135` | Track uses of "TODO" tags | TODO comments must remain until their associated feature or fix is actually implemented. Never delete or comment out TODO comments merely to satisfy static analysis. |
| `java:S1874` / `java:S1123` | Deprecated code usage | Deprecated methods and tags are intentionally preserved to ensure binary and source backward compatibility for existing consumers until major release milestones. |
| `java:S1602` | Remove lambda expression block braces | In multi-overloaded functional interfaces, explicit braces `{ return ...; }` are required to disambiguate overloaded methods (e.g. `Supplier` vs `Consumer`). Removing braces causes compiler failures (`reference is ambiguous`). |
| `java:S3011` | Reflection accessibility bypass | Dynamic reflection utilities, serializers, and entity copiers dynamically inspect and mutate properties. Reflection access is required by design. |
| `java:S2160` | Subclasses adding fields should override equals | DTOs, models, or entities extending a base reflection/identity class rely on the base class's `equals`, `hashCode`, and `toString`. Adding boilerplate overrides across models creates unnecessary noise and breaks uniformity. |
| `java:S6548` | "Singleton" pattern should not be used | Framework constants, mapper instances, and fallback/default entities intentionally use singleton instances. |
| `java:S1172` | Unused method parameters (Framework signatures) | Method parameters in service interfaces (e.g. `Pageable pageable`, `SecurityContext context`) or controllers are part of polymorphic API contracts or framework interception hooks. |
| `java:S106` | Standard output usage (`System.out` / `System.err`) | CLI utilities, standalone tools, and migration runners intentionally print progress and diagnostic output to stdout/stderr. |

---

## 2. Actionable Code Smells to FIX (ALWAYS ADHERE TO)

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
