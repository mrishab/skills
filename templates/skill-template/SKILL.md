---
name: skill-template
description: A template skill demonstrating the open Agent Skills standard. Use when scaffolding or learning how to write high-quality agent skills.
version: 1.0.0
---

# Skill Template

Provide a high-level summary of what this skill enables the agent to do.

## When to Activate

Specify clear, unambiguous trigger conditions for when the agent should select and activate this skill:
- Trigger 1: The user requests `<specific task or outcome>`.
- Trigger 2: The agent detects `<specific codebase condition or file type>`.
- Auto-Reject: Do NOT activate if `<out-of-scope condition>`.

## Workflow & Steps

1. **Step 1: Inspect & Prepare**
   - Check required dependencies and inputs.
   - If an automated helper script exists, execute it:
     ```bash
     ./scripts/example.sh
     ```

2. **Step 2: Core Execution**
   - Execute the primary task following standard conventions.
   - For detailed API parameters or background, consult [reference.md](./references/reference.md).

3. **Step 3: Verification & Quality Gate**
   - Verify that output matches expected format and passes checks.
   - Confirm with test or dry-run command.

## Verification Checklist

- [ ] Core task completed without errors
- [ ] No regression introduced
- [ ] Output validated against acceptance criteria
