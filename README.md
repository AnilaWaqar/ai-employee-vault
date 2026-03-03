# AI Employee Vault 🤖

A fully autonomous AI Employee system built with Claude Code that handles Gmail, WhatsApp, LinkedIn, Facebook, Instagram, Twitter/X, Google Calendar, and Odoo Accounting — with human-in-the-loop approval for every action.

---

## Tier System

| Tier | Status | Capabilities |
|------|--------|-------------|
| Bronze | ✅ Complete | Gmail automation, email drafting, human approval |
| Silver | ✅ Complete | WhatsApp, LinkedIn, Email MCP, HITL Orchestrator |
| Gold | ✅ Complete | Odoo, Facebook, Instagram, Twitter, Calendar, CEO Briefing, Watchdog |

---

## Gold Tier Features

| Feature | Description |
|---------|-------------|
| Odoo Accounting | Invoice creation via MCP — Docker + PostgreSQL |
| Facebook + Instagram | Playwright browser automation with HITL approval |
| Twitter/X | Playwright browser automation (Google OAuth session) |
| Browser + Calendar MCP | Google Calendar API + `@playwright/mcp` |
| CEO Briefing | Weekly comprehensive briefing — revenue, social, calendar |
| Ralph Wiggum Loop | Autonomous self-prompting via Claude Code stop hooks |
| Error Recovery | Watchdog monitors 5 processes, auto-restart (max 3x) |
| Audit Logging | JSON logs analyzed into dashboard with success rates |

---

## Architecture

```
Gmail API
    │
    ▼
Needs_Action/EMAIL_*.md
    │
    ▼ Claude (/inbox-processor)
Drafts/DRAFT_*.md  +  Plans/PLAN_*.md
    │
    ▼ Human moves to Approved/
Approved/DRAFT_*.md
    │
    ▼ master_pipeline.py (every 120s)
Done/SENT_*.md  ──────────────────────────────────────────┐
                                                           │
WhatsApp Web ──► Needs_Action/WHATSAPP_*.md               │
LinkedIn     ──► Pending_Approval/LINKEDIN_*.md ──► Done/ │
Facebook     ──► Pending_Approval/FACEBOOK_*.md ──► Done/ │
Instagram    ──► Pending_Approval/INSTAGRAM_*.md ──► Done/│
Twitter/X    ──► Pending_Approval/TWITTER_*.md  ──► Done/ │
                                                           │
Odoo MCP ────────────────────── Invoices created directly  │
Calendar MCP ────────────────── Events created directly    │
                                                           │
CEO Briefing ── Briefings/CEO_BRIEFING_*.md               │
Watchdog     ── Logs/watchdog.log + Needs_Action/ALERT_*  │
Audit Logger ── Logs/audit-dashboard.md ──────────────────┘
```

---

## MCP Servers

| Server | Purpose |
|--------|---------|
| `odoo` | Create invoices, list customers |
| `email` | Send/draft/search Gmail |
| `browser` | Web navigation via Playwright |
| `calendar` | Google Calendar CRUD |

---

## Running Processes

| Process | Script |
|---------|--------|
| master-pipeline | `Skills/gmail-watcher/scripts/master_pipeline.py` |
| whatsapp-watcher | `Skills/whatsapp-watcher/scripts/whatsapp_watcher.py` |
| linkedin-poster | `Skills/linkedin-poster/scripts/linkedin_poster.py` |
| orchestrator | `orchestrator.py` |
| plan-creator | `Skills/plan-creator/scripts/plan_creator.py` |
| watchdog | `watchdog.py` |

---

## Scheduled Tasks (Windows Task Scheduler)

| Task | Schedule |
|------|----------|
| CEO Briefing | Every Sunday 10PM |
| Log Cleanup | 1st of each month, 3AM |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Brain | Claude Code (claude-sonnet-4-6) |
| Browser Automation | Playwright |
| Email | Gmail API (OAuth2) |
| CRM/Accounting | Odoo 17 (Docker) |
| Database | PostgreSQL 15 (Docker) |
| Calendar | Google Calendar API v3 |
| MCP Protocol | `@modelcontextprotocol/sdk` |
| Language | Python 3.14 + Node.js 24 |
| Platform | Windows 10 |

---

## Quick Start

```bash
# 1. Docker start karo (Odoo)
docker start odoo-db odoo-ai-employee

# 2. Processes start karo
python Skills/gmail-watcher/scripts/master_pipeline.py
python Skills/whatsapp-watcher/scripts/whatsapp_watcher.py
python watchdog.py

# 3. Claude Code mein kaam karo
claude

# 4. CEO Briefing generate karo
python Skills/ceo-briefing/scripts/ceo_briefing.py
```

---

## Credentials

All credentials stored in `.env` (not committed to git):
- Gmail OAuth token: `Skills/gmail-watcher/assets/token.json`
- Google API credentials: `Skills/gmail-watcher/assets/credentials.json`
- Odoo: `.env` (ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD)
- Social media: `.env` (FB_EMAIL, IG_USERNAME, TWITTER_EMAIL, etc.)

---

## Built With

- [Claude Code](https://claude.ai/claude-code) — AI orchestration
- [Playwright](https://playwright.dev) — Browser automation
- [Odoo](https://odoo.com) — ERP/Accounting
- [Model Context Protocol](https://modelcontextprotocol.io) — Tool integration
- [Google APIs](https://developers.google.com) — Gmail + Calendar
