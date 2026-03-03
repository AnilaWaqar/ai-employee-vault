# AI Employee System — SPEC.md

## Vision
An AI Employee that autonomously handles Gmail communications — reading, categorizing,
drafting, and sending emails — with human oversight for sensitive actions.
Built in tiers, each tier adding more capability and intelligence.

---

## Tier System

### 🥉 Bronze Tier — `AI_Employee_Vault/`
**Status:** ✅ Complete & Running

**Scope:** Gmail automation with human-in-the-loop approval

**Capabilities:**
- Gmail monitoring (unread + important emails, every 120s)
- Email categorization using Company_Handbook.md rules
- Draft response generation using templates
- Sensitive email flagging → Pending_Approval/
- Human approval workflow (Approved/ → auto-send)
- Auto-send via Gmail API
- Dashboard auto-update
- Logging (Claude activity + Python pipeline)

**Skills:** gmail-watcher, inbox-processor, dashboard-updater

**Pipeline:** `master_pipeline.py` (Gmail Watcher + Email Sender + Dashboard Updater)

---

### 🥈 Silver Tier — `AI_Employee_Vault/` (Personal AI Employee — Silver Tier)
**Status:** 🔲 Planned
**Spec:** See `SILVER_TIER.md`

**Scope:** Multi-channel automation (WhatsApp + LinkedIn + Email MCP + HITL Orchestrator)

**Capabilities:**
- WhatsApp Watcher (keyword-triggered action files)
- Email MCP Server (Claude sends via MCP tools)
- LinkedIn Auto-Poster (with approval)
- HITL Orchestrator (Approved/ → auto-execute)
- Plan Creator (Claude reasoning loop)
- PM2 + Task Scheduler (24/7 uptime)

**Skills:** whatsapp-watcher, email-mcp, linkedin-poster, hitl-workflow, plan-creator, orchestrator

---

### 🥇 Gold Tier
**Status:** 🔲 Planned
**Spec:** See `GOLD_TIER.md`

**Scope:** Full autonomy, memory, voice, calendar, research, analytics

**Capabilities:**
- Autonomous Agent Mode (configurable trust tiers, audit trail)
- Google Calendar integration (meeting detection, daily briefing)
- Web Research Agent (scheduled + on-demand, DuckDuckGo)
- Long-Term Memory & Contact Intelligence (contacts.json, follow-ups)
- Voice Command Interface (Whisper STT, pyttsx3 TTS, wake word)
- Analytics & Business Intelligence (weekly/monthly reports vs goals)

**Skills:** autonomous-agent, calendar-manager, web-researcher, memory-engine, voice-interface, analytics

---

## System Architecture

### Email File Flow (Bronze)
```
Gmail API
  ↓
Needs_Action/EMAIL_*.md
  ↓ Claude (/inbox-processor)
Plans/PLAN_*.md  +  Drafts/DRAFT_*.md
  ↓ Human review
Approved/DRAFT_*.md
  ↓ master_pipeline.py
Done/SENT_*.md
```

### Skill Structure (per skill, all tiers)
```
Skills/{skill-name}/
├── SKILL.md            # Role, steps, rules for Claude
├── scripts/            # Python implementation scripts
├── references/         # API docs & references
└── assets/             # Config files, tokens, data
```

Scaffold a new skill: `python init_skill.py {skill-name}`

### Claude Commands
- Stored in `.claude/commands/` — one `.md` file per skill
- Invoked via `/{skill-name}` inside Claude Code
- Each command file tells Claude how to act as that skill

---

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Email (Needs_Action) | `EMAIL_{id}.md` | `EMAIL_19c42bccd188ee6c.md` |
| Draft | `DRAFT_{date}_{id}.md` | `DRAFT_20260224_aniya_meeting.md` |
| Plan | `PLAN_{date}_{id}.md` | `PLAN_20260119_203753_19bd6e7c.md` |
| Approval required | `APPROVAL_REQUIRED_{filename}.md` | `APPROVAL_REQUIRED_EMAIL_19c144c32a3b8cc9.md` |
| Sent | `SENT_{draft_filename}.md` | `SENT_DRAFT_20260224_aniya_meeting.md` |
| Claude log | `YYYY-MM-DD.md` | `2026-02-24.md` |
| Pipeline log | `pipeline_YYYYMMDD.log` | `pipeline_20260224.log` |

---

## Global Rules (All Tiers)
- Human approval required before any email is sent
- Sensitive content (OTP, security alerts, financial, legal, HR) always → Pending_Approval
- All actions must be logged
- Processed email IDs must be tracked to avoid duplicates
- Company_Handbook.md is the source of truth for email rules and templates
