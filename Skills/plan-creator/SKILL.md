---
name: plan-creator
description: Read files in /Needs_Action/ and create
structured Plan.md files in /Plans/ with checkboxes.
Always reads Company_Handbook.md for rules. Creates
approval requests for sensitive actions. Use whenever
inbox processing, task planning, or reasoning about
a new action file is needed.
---

# Plan Creator

## Overview
Yeh skill Claude ko Needs_Action/ files padhne aur structured Plans/ files
banane ki ability deti hai. Python script automatically plan templates banata
hai. Claude intelligence se plans fill karta hai jab /plan-creator invoke ho.

## Auto Mode (Python Script)
`Skills/plan-creator/scripts/plan_creator.py` har 60s mein:
1. Needs_Action/ mein naye files dhundhta hai
2. Sensitivity check karta hai (Company_Handbook.md rules)
3. Plans/PLAN_*.md template banata hai
4. Sensitive → Pending_Approval/ mein flag karta hai
5. Processed files track karta hai (no duplicates)

## Claude Manual Mode (when /plan-creator invoked)

### Steps
1. Read all unprocessed files in /Needs_Action/
2. Read Company_Handbook.md for categorization rules
3. For each file, identify:
   - Task type: email / whatsapp / file_drop
   - Priority: high / normal
   - Sensitivity: any sensitive keywords?
4. Create /Plans/PLAN_TIMESTAMP_FILENAME.md

### Plan File Format
```
---
created: ISO_TIMESTAMP
status: in_progress
triggered_by: FILENAME
task_type: email / whatsapp / file_drop
priority: high / normal
approval_required: yes / no
skill_used: plan-creator
---

# Plan: SUBJECT/TITLE

## Source
- **File:** `filename.md`
- **Type:** email
- **From:** sender
- **Priority:** HIGH

## Objective
ONE SENTENCE GOAL

## Steps
- [x] File detected in Needs_Action/
- [x] Sensitivity check performed
- [x] Plan created
- [ ] Draft response created → Drafts/
- [ ] Human review complete
- [ ] Completed → Done/

## Approval Required
YES/NO — reason here
```

### Sensitivity Rules (from Company_Handbook.md)
Flag as sensitive if text contains:
- `legal`, `lawsuit`, `complaint`, `violation`, `termination`
- `confidential`, `password reset`, `security alert`, `otp`
- `hacked`, `breach`, `fraud`, `harassment`

Sensitive files → create `Pending_Approval/APPROVAL_REQUIRED_{filename}.md`

## Rules
- Always follow Company_Handbook.md
- Never send anything without /Approved/ file
- Always create Plan.md before taking any action
- Log every step to /Logs/
- Processed files tracked in Skills/plan-creator/assets/processed_plans.json
