---
name: dual-dashboard-skill
description: >
  Merges Cloud Agent activity from /Updates/ folder into Dashboard.md.
  Use this skill when user asks about dashboard updates, cloud agent
  activity, or wants to sync cloud status to dashboard. Trigger on:
  "update dashboard", "merge updates", "dashboard sync", "cloud activity",
  "agent status", "what did cloud do", "sync dashboard", "dashboard update".
---

# Dual Dashboard Skill

## Purpose
Read Cloud Agent updates from /Updates/ folder and merge them into
Dashboard.md. Only Local Agent writes Dashboard.md (single-writer rule).

## Trigger Phrases
Use this skill when user says:
- "update dashboard"
- "merge updates"
- "dashboard sync karo"
- "cloud activity dikhao"
- "what did cloud do"
- "dashboard mein cloud updates add karo"
- "agent status"

## Input
- /Updates/cloud_*.md files (cloud agent ki activity)
- Dashboard.md (merge target)

## Scripts
- `scripts/dashboard_merger.py` — Local PC pe run hoga

## Steps
1. List all `cloud_*.md` files in /Updates/
2. For each file — strip YAML frontmatter, extract body
3. Format each entry as: `[HH:MM] ☁️ Cloud: <message>`
4. Find `## Cloud Agent Updates` section in Dashboard.md
5. Prepend new entries under that section
6. If section missing — create it at bottom of Dashboard.md
7. Move processed files to /Updates/processed/
8. Log merge count to /Logs/dashboard_merger.log

## Output Format
Dashboard.md updated with:
```
## Cloud Agent Updates
- [10:45] ☁️ Cloud: Email drafted for client@example.com
- [10:30] ☁️ Cloud: Health check — all systems running
```

## Rules
- ONLY Local Agent writes Dashboard.md — Cloud NEVER writes directly
- Processed updates move to /Updates/processed/ — never delete
- Run hourly via PM2 cron or Windows Task Scheduler
- If Dashboard.md missing — log error, do not create new file
- DRY_RUN=true supported — shows what would be merged without writing
