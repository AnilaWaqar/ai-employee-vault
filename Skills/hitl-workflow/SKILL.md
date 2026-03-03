---
name: hitl-workflow
description: Human-in-the-loop approval system for
sensitive actions. Creates approval request files
for email sends, LinkedIn posts, and WhatsApp replies.
Use whenever an action requires human confirmation
before execution. Move file to /Approved/ to proceed
or /Rejected/ to cancel.
---

# HITL Approval Workflow

## Overview
Yeh skill Claude ko approval request files banana sikhati hai.
Human file move karta hai → Orchestrator action leta hai.

## How It Works
```
Claude writes → Pending_Approval/
Human moves  → Approved/ or Rejected/
Orchestrator → Executes or cancels
Done/        → Archive
```

## Approval File Types

### 1. Send Email
```
---
type: approval_request
action: send_email
to: recipient@example.com
subject: Email Subject
created: ISO_TIMESTAMP
expires: ISO_TIMESTAMP_PLUS_24H
status: pending
---

**To:** recipient@example.com
**Subject:** Email Subject

---

Email body here...

---
```

### 2. WhatsApp Reply (log only — no auto-send)
```
---
type: approval_request
action: whatsapp_reply
to: Contact Name
created: ISO_TIMESTAMP
status: pending
---

Reply text here...
```

### 3. LinkedIn Post
Handled automatically by linkedin_poster.py — use LINKEDIN_*.md format.

## Orchestrator Behavior
- `Approved/` → Execute action (send_email) or acknowledge
- `Rejected/` → Log rejection, move to Done/REJECTED_*
- `Pending_Approval/` → Expire files older than 24h → Done/EXPIRED_*
- Skips: DRAFT_*.md, LINKEDIN_*.md (other scripts handle these)

## Rules
- Kabhi bhi bina Approved/ file ke action mat lo
- DRY_RUN=true pe email nahi bhejta, sirf log karta hai
- Har action ka audit log /Logs/YYYY-MM-DD.md mein hota hai
- 24h baad unexpired files auto-expire ho jaati hain
