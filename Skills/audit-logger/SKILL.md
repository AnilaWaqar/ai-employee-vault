---
name: audit-logger
description: Comprehensive audit logging system. Analyzes all JSON logs,
generates audit dashboard with success rates, actor breakdown, and error reports.
Monthly cleanup of old log files.
---

# Audit Logger

## Role
Tu AI Employee ka Audit specialist hai. Saare actions track karta hai,
success rates calculate karta hai, aur monthly cleanup karta hai.

---

## Scripts

| Script | Kaam |
|--------|------|
| `scripts/audit_dashboard.py` | Logs analyze karo, dashboard banao |
| `scripts/log_cleanup.py` | Purane logs delete karo (30+ din) |

## Output
`Logs/audit-dashboard.md`

---

## Dashboard Sections

- Overview (total, success, failed, rate)
- By Actor breakdown
- By Action Type
- Daily Activity chart (last 7 days)
- Recent Errors (last 10)
- Recent Activity (last 5)

---

## Schedule

| Task | Schedule |
|------|----------|
| audit_dashboard.py | Weekly (Sunday ke saath CEO briefing) |
| log_cleanup.py | Monthly (1st of each month) |

---

## Log Format (JSON)

```json
{
  "timestamp": "ISO datetime",
  "action_type": "tweet_post / send_email / etc",
  "actor": "twitter-poster / claude / etc",
  "target": "platform or URL",
  "result": "success / error message",
  "content_preview": "first 100 chars",
  "dry_run": false
}
```
