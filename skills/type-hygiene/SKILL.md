---
name: type-hygiene
description: Audits and eliminates TypeScript Record anti-patterns, replacing nested Records with proper domain types. Activate when refactoring domain logic, handling complex DTOs, or addressing "any" / type unsafety issues.
version: 1.0.0
author: mrishab
tags: [typescript, refactoring, clean-code, architecture, typing]
---

# Type Hygiene: Record Eradication

Eliminates nested `Record<string, Record<string, T>>` structures and open-ended `Record<string, T>` anti-patterns from domain logic in favor of domain types, branded identifiers, and boundary validation.

## Hard Rules

1. **Zero Nested Records:** `Record<string, Record<string, T>>` is prohibited. Replace with domain value objects or composite keys.
2. **No Raw Records in Domain Logic:** Open dictionary structures belong only at system boundaries (I/O, external DTOs). Parse data at the edge into typed models.
3. **No Defensive Null Checks in Domain:** If domain logic requires constant null/undefined guard chains (`a[k1]?.[k2]`), parse the payload at the boundary.

## Decision Matrix

| Use Case | Target Solution |
| :--- | :--- |
| Known fixed keys with different types | Named `interface` or `type` |
| Known fixed keys with uniform values | Object literal with `satisfies Record<K, V>` |
| Finite string literal tokens | `Record<UnionKey, V>` |
| Arbitrary dynamic keys / high-churn cache | `Map<BrandedKey, V>` |
| Multi-level nested dictionary | Domain Value Object or composite key `Map<`${K1}:${K2}`, V>` |

## Anti-Patterns & Replacements

### 1. Nested Records
```typescript
// ❌ BAD: Transposition risk, no IntelliSense, double-index runtime crashes
type Permissions = Record<string, Record<string, boolean>>;

// ✅ GOOD: Domain Value Object with branded keys
type RoleId = string & { readonly __brand: unique symbol };
type ResourceId = string & { readonly __brand: unique symbol };

class PermissionMatrix {
  private matrix = new Map<string, boolean>();

  private key(role: RoleId, resource: ResourceId): string {
    return `${role}:${resource}`;
  }

  grant(role: RoleId, resource: ResourceId): void {
    this.matrix.set(this.key(role, resource), true);
  }

  has(role: RoleId, resource: ResourceId): boolean {
    return this.matrix.get(this.key(role, resource)) ?? false;
  }
}
```

### 2. Type Widening Configuration
```typescript
// ❌ BAD: Annotation erases exact key and value types
const config: Record<string, string | number> = { port: 8080, host: 'localhost' };

// ✅ GOOD: Preserves literal types and autocomplete
const config = { port: 8080, host: 'localhost' } satisfies Record<string, string | number>;
```

### 3. Shotgun Boundary Validation
```typescript
// ❌ BAD: Scattered defensive null-checks throughout business logic
function processUser(data: Record<string, any>) {
  if (data && data.profile && data.profile.age > 18) { ... }
}

// ✅ GOOD: Boundary schema parsing (e.g. Zod)
const UserSchema = z.object({
  profile: z.object({ age: z.number().min(0) })
});

function handleIncoming(raw: unknown) {
  const user = UserSchema.parse(raw);
  processUser(user); // Guaranteed valid; no defensive checks needed
}
```

### 4. High-Churn Cache
```typescript
// ❌ BAD: Plain object deletion causes runtime de-optimizations
const cache: Record<string, User> = {};
cache[id] = user;
delete cache[id];

// ✅ GOOD: Map with branded keys
type UserId = string & { readonly __brand: unique symbol };
const cache = new Map<UserId, User>();
cache.set(id, user);
cache.delete(id);
```

## Discovery Commands

```bash
# Find nested records (zero tolerance)
rg 'Record<string,\s*Record'

# Find open-ended record annotations
rg 'Record<string,'

# Find multi-level indexing chains
rg '\[\w+\]\[\w+\]'
```

## Verification Checklist

```bash
# 1. Zero nested records
rg 'Record<string,\s*Record' || echo "PASS"

# 2. Strict indexed access enabled
grep '"noUncheckedIndexedAccess": true' tsconfig.json

# 3. Clean compilation
tsc --noEmit
```
