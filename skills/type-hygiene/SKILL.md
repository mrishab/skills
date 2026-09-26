---
name: type-hygiene
description: Audits and eliminates TypeScript Record anti-patterns, replacing nested Records with proper domain types. Activate when refactoring domain logic, handling complex DTOs, or addressing "any" / type unsafety issues.
version: 1.0.0
author: mrishab
tags: typescript, refactoring, clean-code, architecture, typing
---

# Type Hygiene: TypeScript Record Eradication

This skill enforces strict boundaries and rich domain models by eliminating TypeScript `Record` anti-patterns, specifically nested dictionaries and open-ended `Record<string, T>` usage in domain logic.

## Grounding Expertise

This workflow is grounded in principles from leading software engineering experts:
- **Matt Pocock**: Emphasizes `satisfies`, mandatory `noUncheckedIndexedAccess`, and branded primitive types.
- **Robert C. Martin (Clean Code)**: Warns against anemic data structures causing Feature Envy, and Law of Demeter violations (`data[a][b][c]`).
- **Alexis King ("Parse, Don't Validate")**: Push untrusted data to system edges, parse it into strong types, and eliminate downstream defensive checks.

## Trigger Criteria

Activate this skill when:
- Reviewing or refactoring domain entity structures.
- Dealing with high-churn caching or complex nested state configurations.
- Finding deep property access chains like `permissions[roleId][resourceId]`.
- Encountering type-widening issues on configuration objects.

## Step-by-Step Workflow

### Step 1: Discovery

Scan the codebase for `Record` usage and deep indexing patterns. Use the following commands:

```bash
# Find zero-tolerance nested Records
rg 'Record<string,\s*Record'

# Find open-ended Record usage (potential semantic amnesia)
rg 'Record<string,'

# Find deep indexing (Law of Demeter violations)
rg '\[\w+\]\[\w+\]'
```

### Step 2: Decision Matrix

Evaluate each `Record` usage against this decision matrix to find the correct alternative:

| Use Case | Solution |
| :--- | :--- |
| Known fixed keys with different types | **Named interface** or `type` |
| Known fixed keys with uniform values | `satisfies Record<K, V>` |
| Finite string literal tokens | `Record<UnionKey, V>` |
| Arbitrary dynamic keys / high churn | `Map<BrandedKey, V>` |
| Multi-level nested index | **Domain Value Object** or Composite Key Map |

### Step 3: Implement Replacements

Apply the structural changes, completely removing the `Record` usage in favor of the target types. See the Anti-Patterns section below.

## Hard Rules (Zero Tolerance)

1. **NO NESTED RECORDS**: `Record<string, Record<string, T>>` is unconditionally banned. It causes semantic amnesia, transposition vulnerabilities, and breaks IntelliSense.
2. **NO RAW RECORDS IN DOMAIN LOGIC**: Raw JSON/Records belong ONLY at I/O boundaries. They must be parsed (not just validated) at the edge.
3. **NO DEFENSIVE NULL CHECKS IN DOMAIN**: If domain logic requires constant null checking of nested structures, the boundary parsing has failed.

## Anti-Patterns and Solutions

### 1. Nested Records (The Semantic Amnesia)

❌ **Anti-pattern: Nested records for complex mapping**
```typescript
// Transposition vulnerability: swapping roleId and resourceId compiles silently
type Permissions = Record<string, Record<string, boolean>>;

const check = (perms: Permissions, roleId: string, resourceId: string) => {
  return perms[roleId]?.[resourceId] ?? false; // Law of Demeter violation
};
```

✅ **Replacement: Domain Value Object or Composite Key Map**
```typescript
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

❌ **Anti-pattern: Annotating config objects with Record**
```typescript
// Type is widened; IntelliSense forgets exact keys and values
const config: Record<string, string | number> = {
  port: 8080,
  host: 'localhost',
};
// config.port is inferred as string | number
```

✅ **Replacement: The `satisfies` operator**
```typescript
const config = {
  port: 8080,
  host: 'localhost',
} satisfies Record<string, string | number>;
// config.port is exactly 8080 (number)
// config.host is exactly 'localhost' (string)
```

### 3. Shotgun Null-Checking on DTOs

❌ **Anti-pattern: Trusting unparsed boundary data**
```typescript
function processUser(data: Record<string, any>) {
  if (data && data.profile && data.profile.age > 18) {
    // Process...
  }
}
```

✅ **Replacement: Parse, Don't Validate (e.g., using Zod)**
```typescript
import { z } from 'zod';

const UserSchema = z.object({
  profile: z.object({
    age: z.number().min(0)
  })
});

function processUser(data: unknown) {
  const user = UserSchema.parse(data);
  // Downstream domain logic never defensive-checks again
  if (user.profile.age > 18) {
    // Process...
  }
}
```

### 4. High-Churn Caching

❌ **Anti-pattern: Objects for frequent additions/removals**
```typescript
const userCache: Record<string, User> = {};
userCache[user.id] = user;
delete userCache[user.id];
```

✅ **Replacement: Map with Branded Keys**
```typescript
type UserId = string & { readonly __brand: unique symbol };
const userCache = new Map<UserId, User>();
userCache.set(user.id, user);
userCache.delete(user.id);
```

## Verification Checklist

Run these commands after applying the skill to guarantee compliance. ALL MUST PASS.

1. **Verify No Nested Records Remain**:
   ```bash
   rg 'Record<string,\s*Record' || echo "PASS"
   ```
   *Expected Output: PASS (No matches found)*

2. **Check for `noUncheckedIndexedAccess`**:
   ```bash
   cat tsconfig.json | grep '"noUncheckedIndexedAccess": true'
   ```
   *Expected Output: Match found in tsconfig.json*

3. **Verify Code Compiles**:
   ```bash
   tsc --noEmit
   ```
   *Expected Output: (No errors)*
