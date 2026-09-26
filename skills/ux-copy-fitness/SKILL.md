---
name: ux-copy-fitness
description: Audits and reduces unnecessary text across an entire web application, enforcing concise, scannable, action-oriented UI copy.
version: 1.0.0
author: mrishab
tags: [ui, ux, copy, optimization, auditing]
---

# ux-copy-fitness

Audits and reduces unnecessary text across an entire web application, enforcing concise, scannable, action-oriented UI copy based on established UX research (Krug's Law, Nielsen's Research).

## Trigger Criteria

Activate this skill when:
- Conducting a UI/UX audit or polish pass.
- Users are skimming over important information or missing actions.
- The UI feels cluttered, verbose, or overwhelming.
- Converting wireframes/designs to production implementation.
- Reviewing new features before launch.

## Workflow

Follow these steps to systematically reduce cognitive load and improve scannability across the application.

### 1. Discover Verbose Text and Anti-Patterns

Use `rg` (ripgrep) to find potential areas for reduction across the codebase.

**Search for long strings (potential over-explanation):**
```bash
rg "'.{80,}'|\".{80,}\"" -g "*.{tsx,jsx,ts,js,html}"
```

**Search for "Furniture Text" (unnecessary introductory words):**
```bash
rg -i "welcome to|here you can|please note|fill out all|select an option|from the list below" -g "*.{tsx,jsx,html}"
```

**Search for Tech Stack References (Anti-User):**
```bash
rg -i "powered by|built with|runs on|react|next\.js|tailwind|postgres" -g "*.{tsx,jsx,html}"
```

**Search for Generic Button/Action Labels:**
```bash
rg -i ">(click here|submit|ok|yes|no)<" -g "*.{tsx,jsx,html}"
```

### 2. Apply Krug's Law (75% Reduction Target)

For every block of text discovered:
1. "Get rid of half the words on each page."
2. "Then get rid of half of what's left."

Ask yourself: *What is the absolute minimum number of words required for the user to understand the state or complete the task?*

### 3. Implement Progressive Disclosure

Move non-essential context out of the primary reading path. Remember that 80% of users need only the primary label and action.
- Hide supplemental context behind tooltips.
- Use accordions for secondary information.
- Provide "Learn more" links instead of inline paragraphs.

### 4. Optimize for F-Pattern Scanning

Users fixate on the first 1-2 words of any line. Front-load actionable keywords and nouns. Omit articles (a, an, the) in menu items and buttons.

## Hard Rules (Zero Tolerance)

Enforce these strict quantitative limits on UI copy dimensions. (Based on cognitive load limits: Working memory holds only 4±1 chunks).

| Element | Length Limit | Character Limit | Formatting Rules |
| :--- | :--- | :--- | :--- |
| **Button Labels** | 1-3 words | ≤25 chars | Sentence case, `[Verb] + [Noun]`, Omit articles |
| **Page Headings** | 2-5 words | ≤45 chars | Sentence case, Front-load keyword |
| **Modal Titles** | 3-5 words | ≤35 chars | Sentence case |
| **Body/Helper Text** | 1-2 sentences | ≤120 chars | - |
| **Tooltips** | 1 sentence | ≤80 chars | - |
| **Empty State Headline** | 2-4 words | ≤30 chars | - |
| **Toast Notifications** | 3-6 words | ≤40 chars | Past-tense confirmation |
| **Error Messages** | 1-2 sentences | ≤100 chars | `[What happened] + [Fix]` |

## Anti-Patterns and Replacements

### ❌ Furniture Text
Text that exists out of habit, not necessity.

❌ **Bad:** `"Welcome to your Dashboard. Here you can view your recent activity."`
✅ **Good:** `"Dashboard"`

❌ **Bad:** `"Please fill out all required fields below to continue."`
✅ **Good:** *(Delete entirely, use standard `*` indicators)*

❌ **Bad:** `"Select an option from the list below:"`
✅ **Good:** `"Role"` (Label directly attached to dropdown)

❌ **Bad:** `"There are currently no items available to display at this time."`
✅ **Good:** `"No projects yet"`

### ❌ Tech Stack References
Exposing implementation details to users provides zero value for their task (Alan Cooper's Implementation Model vs Mental Model).

❌ **Bad:** `"This feature is powered by our new AI engine."`
✅ **Good:** `"Smart recommendations"`

❌ **Bad:** `"Loading React components..."`
✅ **Good:** `"Loading..."`

### ❌ Generic Actions
Never use generic confirmations that don't describe the result. (Apple HIG)

❌ **Bad:** `<button>Yes</button>`
✅ **Good:** `<button>Delete Project</button>`

❌ **Bad:** `<button>OK</button>`
✅ **Good:** `<button>Save Changes</button>`

### ❌ Poor Error Messages
Errors must explain what happened and how to fix it concisely.

❌ **Bad:** `"An unexpected system error occurred while processing your request. Please try again later or contact support."`
✅ **Good:** `"Payment failed. Check your card details and try again."`

## Verification

Run these checks to ensure the application meets the UX copy fitness standards. All commands must return clean (no matches) for the audit to pass.

1. **Verify no extremely long strings exist in UI components:**
   ```bash
   rg "'.{120,}'|\".{120,}\"" -g "*.{tsx,jsx,html}"
   ```
2. **Verify no generic actions remain:**
   ```bash
   rg -i ">(submit|ok|yes|no|click here)<" -g "*.{tsx,jsx,html}"
   ```
3. **Verify no tech stack leaks:**
   ```bash
   rg -i "powered by|built with" -g "*.{tsx,jsx,html}"
   ```
4. **Verify no furniture text remains:**
   ```bash
   rg -i "please note|here you can|welcome to" -g "*.{tsx,jsx,html}"
   ```
