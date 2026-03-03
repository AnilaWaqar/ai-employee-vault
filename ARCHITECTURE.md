# Architecture — AI Employee Vault

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     AI EMPLOYEE VAULT                        │
│                   (Windows 10 + Docker)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │  Gmail   │    │ WhatsApp │    │ LinkedIn │             │
│  │   API    │    │   Web    │    │   Web    │             │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘             │
│       │               │               │                     │
│       ▼               ▼               ▼                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Needs_Action/ & Pending_Approval/       │   │
│  │                    (Markdown Files)                  │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  CLAUDE CODE (AI Brain)              │   │
│  │              claude-sonnet-4-6 model                 │   │
│  │                                                      │   │
│  │  Skills: inbox-processor, linkedin-poster,           │   │
│  │          facebook-poster, twitter-poster,            │   │
│  │          odoo-accounting, calendar-mcp,              │   │
│  │          ceo-briefing, ralph-wiggum                  │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                          │                                   │
│            ┌─────────────┼─────────────┐                    │
│            ▼             ▼             ▼                     │
│       ┌─────────┐  ┌─────────┐  ┌─────────┐               │
│       │  MCP    │  │ Drafts/ │  │ Plans/  │               │
│       │Servers  │  │         │  │         │               │
│       └────┬────┘  └────┬────┘  └─────────┘               │
│            │             │                                   │
│    ┌───────┴──┐    ┌─────▼──────┐                          │
│    │ odoo     │    │  Human     │                           │
│    │ email    │    │  Review    │                           │
│    │ browser  │    └─────┬──────┘                          │
│    │ calendar │          │ Approved/                        │
│    └──────────┘          ▼                                  │
│                    ┌─────────────┐                          │
│                    │master_      │                          │
│                    │pipeline.py  │                          │
│                    │(every 120s) │                          │
│                    └─────┬───────┘                          │
│                          │                                   │
│                          ▼                                   │
│                      Done/ ✅                               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE                            │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Docker     │  │  Watchdog    │  │ Task Scheduler│     │
│  │  odoo:17     │  │  (30s check) │  │ CEO: Sun 10PM │     │
│  │  postgres:15 │  │  5 processes │  │ Cleanup: Mon  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Email Flow (Bronze + Silver)

```
Gmail Inbox
    │
    ▼ gmail_watcher.py (every 120s)
Needs_Action/EMAIL_*.md
    │
    ├── Sensitive? ──► Pending_Approval/ (manual review)
    │
    ▼ Claude /inbox-processor
Drafts/DRAFT_*.md
Plans/PLAN_*.md
    │
    ▼ Human approves (moves to Approved/)
Approved/DRAFT_*.md
    │
    ▼ email_sender.py
Gmail → Recipient
    │
    ▼
Done/SENT_*.md
```

---

## Social Media Flow (Gold)

```
Claude drafts post
    │
    ▼
Pending_Approval/PLATFORM_*.md
    │
    ▼ Human moves to Approved/
Approved/PLATFORM_*.md
    │
    ▼ platform_poster.py (Playwright)
Facebook / Instagram / Twitter / LinkedIn
    │
    ▼
Done/SENT_PLATFORM_*.md ──► Audit Log JSON
```

---

## MCP Architecture

```
Claude Code
    │
    ├── odoo MCP ──────► Odoo XML-RPC ──► Docker:8069
    │                    (invoices, customers)
    │
    ├── email MCP ─────► Gmail API
    │                    (send, draft, search)
    │
    ├── browser MCP ───► Playwright headless
    │                    (web navigation)
    │
    └── calendar MCP ──► Google Calendar API v3
                         (events CRUD)
```

---

## Ralph Wiggum Loop

```
Claude starts task
    │
    ▼
Claude completes response
    │
    ▼ Stop Hook triggers (ralph_hook.py)
    │
    ├── .current_task exists? NO ──► Claude stops normally
    │
    └── YES
        │
        ├── Done/ has done_marker? YES ──► Delete .current_task
        │                                  Claude stops ✅
        │
        └── NO (or max loops reached)
            │
            ▼ Exit code 2 + inject prompt
        Claude continues working 🔄
```

---

## Watchdog Flow

```
watchdog.py (every 30s)
    │
    ▼ wmic process scan
    │
    ├── Process UP? ──► Log OK, reset restart count
    │
    └── Process DOWN?
        │
        ├── restarts < 3 ──► subprocess.Popen restart
        │
        └── restarts >= 3
            │
            ▼
        Needs_Action/ALERT_*.md + Dashboard warning
```

---

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Email | `EMAIL_{gmail_id}.md` | `EMAIL_19c42bcc.md` |
| Draft | `DRAFT_{date}_{slug}.md` | `DRAFT_20260303_meeting.md` |
| Plan | `PLAN_{date}_{id}.md` | `PLAN_20260303_abc123.md` |
| Sent | `SENT_{original}.md` | `SENT_DRAFT_20260303.md` |
| Social | `FACEBOOK_{ts}.md` | `FACEBOOK_20260303_1000.md` |
| Alert | `ALERT_{process}_{ts}.md` | `ALERT_MASTER-PIPELINE_20260303.md` |
| Briefing | `CEO_BRIEFING_{ts}.md` | `CEO_BRIEFING_20260303_2200.md` |
| Audit | `WEEKLY_AUDIT_{date}.md` | `WEEKLY_AUDIT_20260303.md` |
