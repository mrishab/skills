---
name: ux-copy-fitness
description: Audits and reduces unnecessary text across an entire web application, enforcing concise, scannable, action-oriented UI copy.
version: 1.0.0
author: mrishab
tags: [ui, ux, copy, optimization, auditing]
---

# UX Copy Fitness

Audits and reduces text across web applications to maintain concise, scannable, action-oriented UI copy.

## Length Limits

| Element | Max Words | Max Characters | Format & Syntax |
| :--- | :--- | :--- | :--- |
| **Button Labels** | 1–3 words | ≤25 chars | Sentence case, `[Verb] + [Noun]`, no articles (a/an/the) |
| **Page Headings** | 2–5 words | ≤45 chars | Sentence case, front-load keywords |
| **Modal Titles** | 3–5 words | ≤35 chars | Sentence case, direct statement or question |
| **Body / Helper Text** | 1–2 sentences | ≤120 chars | Focus only on constraints or consequences |
| **Tooltips** | 1 sentence | ≤80 chars | Clarification or shortcut only |
| **Empty State Title** | 2–4 words | ≤30 chars | `No [items] yet` |
| **Toasts / Alerts** | 3–6 words | ≤40 chars | Past-tense confirmation (e.g. `Changes saved`) |
| **Error Messages** | 1–2 sentences | ≤100 chars | `[What happened] + [Actionable fix]` |

## Discovery Commands

```bash
# Long strings in UI components (>80 chars)
rg "'.{80,}'|\".{80,}\"" -g "*.{tsx,jsx,ts,js,html}"

# Furniture text (empty preambles)
rg -i "welcome to|here you can|please note|fill out all|select an option|from the list below" -g "*.{tsx,jsx,html}"

# Tech stack leaks (anti-user)
rg -i "powered by|built with|runs on|react|next\.js|tailwind|postgres" -g "*.{tsx,jsx,html}"

# Generic button labels
rg -i ">(click here|submit|ok|yes|no)<" -g "*.{tsx,jsx,html}"
```

## Anti-Patterns & Replacements

### 1. Furniture Text
Delete conversational filler that conveys no functional information.

| ❌ Bad | ✅ Good |
| :--- | :--- |
| `"Welcome to your Dashboard. Here you can view recent activity."` | `"Dashboard"` |
| `"Please fill out all required fields below to continue."` | *(Delete entirely; use `*` on required fields)* |
| `"Select an option from the list below:"` | `"Role"` |
| `"There are currently no items available to display at this time."` | `"No projects yet"` |

### 2. Tech Stack Leaks
Do not expose implementation libraries or infrastructure in UI copy.

| ❌ Bad | ✅ Good |
| :--- | :--- |
| `"This feature is powered by our AI engine."` | `"Smart recommendations"` |
| `"Loading React components..."` | `"Loading..."` |

### 3. Generic Action Labels
Always name the exact result of the action.

| ❌ Bad | ✅ Good |
| :--- | :--- |
| `<button>Yes</button>` | `<button>Delete Project</button>` |
| `<button>OK</button>` | `<button>Save Changes</button>` |
| `<button>Click Here</button>` | `<button>Download Invoice</button>` |

### 4. Poor Error Messages
State the issue and the solution directly.

| ❌ Bad | ✅ Good |
| :--- | :--- |
| `"An unexpected error occurred while processing your request. Please try again later."` | `"Payment failed. Check your card details and retry."` |

## Progressive Disclosure
For secondary details or deep documentation:
- Hide secondary explanations behind tooltips or `<details>` accordions.
- Use "Learn more" links instead of multi-paragraph in-page explanations.

## Verification Checklist

All commands must return clean (zero matches):
```bash
# 1. No UI strings over 120 chars
rg "'.{120,}'|\".{120,}\"" -g "*.{tsx,jsx,html}"

# 2. No generic action labels
rg -i ">(submit|ok|yes|no|click here)<" -g "*.{tsx,jsx,html}"

# 3. No tech stack leaks
rg -i "powered by|built with" -g "*.{tsx,jsx,html}"

# 4. No furniture text
rg -i "please note|here you can|welcome to" -g "*.{tsx,jsx,html}"
```
