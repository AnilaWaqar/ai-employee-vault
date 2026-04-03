# Dual Dashboard — API Reference

## Flow
```
Cloud VM → writes → /Updates/cloud_*.md
                         ↓ (git sync)
Local PC → reads → dashboard_merger.py → Dashboard.md
```

## Single Writer Rule
- ONLY Local Agent writes Dashboard.md
- Cloud NEVER writes Dashboard.md directly
- Cloud writes to /Updates/ only

## Environment Variables
- `VAULT_PATH` — Path to vault root

## Schedule
- Run hourly via PM2 cron or Windows Task Scheduler
- Command: `python Skills/dual-dashboard-skill/scripts/dashboard_merger.py`
