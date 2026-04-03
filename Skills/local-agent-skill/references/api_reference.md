# Local Agent — API Reference

## Responsibilities
- Approved files execute karna
- Cloud signals padhna
- Dashboard.md update karna
- WhatsApp actions handle karna (LOCAL ONLY)
- Odoo invoices post karna (after approval)

## Environment Variables
- `VAULT_PATH` — Path to vault root
- `DRY_RUN` — Set `true` for testing

## Folders Watched
- `/Approved/` — Files ready to execute
- `/Signals/` — Cloud agent messages
- `/In_Progress/local/` — Claimed tasks

## Rules
- NEVER execute without approved file
- WhatsApp ONLY on local — never cloud
- Always log every action
