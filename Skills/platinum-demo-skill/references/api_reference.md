# Platinum Demo — API Reference

## What It Tests
- Git sync status
- Odoo health (http://13.200.252.166:8069/web/health)
- /Signals/ unread alerts
- /Updates/ unprocessed files
- /In_Progress/ cloud + local tasks
- /Pending_Approval/ items
- Dashboard.md existence

## Environment Variables
- `VAULT_PATH` — Path to vault root
- `CLOUD_VM_IP` — Cloud VM IP (default: 13.200.252.166)
- `DRY_RUN` — Set `true` for testing

## Run Command
```bash
python Skills/platinum-demo-skill/scripts/platinum_demo.py
```

## Report Output
Saved to: /Logs/demo_YYYY-MM-DD.md
