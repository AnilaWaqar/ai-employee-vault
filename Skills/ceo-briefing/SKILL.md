---
name: ceo-briefing
description: Generate comprehensive CEO briefing with system status, Odoo revenue,
social media stats, calendar events, and proactive suggestions.
Auto-runs every Sunday 10PM via Task Scheduler.
---

# CEO Briefing

## Role
Tu AI Employee ka Business Intelligence specialist hai. Har Sunday CEO ke liye
ek comprehensive briefing banata hai — data se insights nikalta hai.

---

## Script
`Skills/ceo-briefing/scripts/ceo_briefing.py`

## Output
`Briefings/CEO_BRIEFING_YYYYMMDD_HHMM.md`

---

## Briefing Sections

| Section | Data Source |
|---------|-------------|
| System Status | Vault folder counts |
| Revenue | Odoo API (this month invoices) |
| Social Media | Done/ folder (SENT_FACEBOOK/TWITTER etc.) |
| Email Activity | Logs/ files |
| Calendar Events | Google Calendar API |
| Proactive Suggestions | AI analysis of all data |

---

## Schedule

- **Auto:** Every Sunday 10PM (Windows Task Scheduler)
- **Manual:** `python Skills/ceo-briefing/scripts/ceo_briefing.py`

---

## Odoo Requirements

- Docker containers must be running
- `docker start odoo-ai-employee odoo-db`
