---
name: orchestrator
description: Manage all running processes for the
AI Employee system. Start, stop, restart watchers
via PM2. Setup Windows Task Scheduler for timed
tasks. Use when process management, scheduling,
or system health monitoring is needed.
---

# Orchestrator

## Overview
Yeh skill AI Employee ke sab processes manage karti hai.
PM2 se processes control karo. Task Scheduler se scheduled tasks.

## PM2 Processes (5 total)

| Process | Script | Purpose |
|---------|--------|---------|
| `master-pipeline` | Skills/gmail-watcher/scripts/master_pipeline.py | Gmail fetch + send |
| `whatsapp-watcher` | Skills/whatsapp-watcher/scripts/whatsapp_watcher.py | WhatsApp monitor |
| `linkedin-poster` | Skills/linkedin-poster/scripts/linkedin_poster.py | LinkedIn posts |
| `orchestrator` | orchestrator.py | Approved/Rejected handler |
| `plan-creator` | Skills/plan-creator/scripts/plan_creator.py | Plan generator |

## Common PM2 Commands
```bash
pm2 status                          # All processes ka status
pm2 logs <name> --lines 20          # Logs dekhna
pm2 restart <name>                  # Restart
pm2 stop <name>                     # Stop
pm2 start ecosystem.config.js       # Sab start
pm2 save                            # Process list save karo
```

## Scheduled Tasks (Windows Task Scheduler)

| Task | Script | Schedule |
|------|--------|----------|
| `AI-Employee-Daily-Briefing` | Skills/orchestrator/scripts/daily_briefing.py | Daily 8:00 AM |
| `AI-Employee-Weekly-Audit` | Skills/orchestrator/scripts/weekly_audit.py | Sunday 10:00 PM |

## Setup Scheduler
```bash
python setup_scheduler.py
```
(Admin rights required — UAC prompt aa sakta hai)

## Output Files
- Daily: `Plans/BRIEFING_YYYYMMDD.md`
- Weekly: `Plans/WEEKLY_AUDIT_YYYYMMDD.md`
- Logs: `Logs/daily_briefing.log`, `Logs/weekly_audit.log`
