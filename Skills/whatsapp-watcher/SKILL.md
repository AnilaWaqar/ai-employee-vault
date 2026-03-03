---
name: whatsapp-watcher
description: Monitor WhatsApp Web for business-critical
  messages containing keywords like urgent, invoice,
  payment, help, deadline. Creates action files in
  /Needs_Action automatically. Always use this skill
  when WhatsApp monitoring, client message detection,
  or business alert automation is needed.
---

# WhatsApp Watcher

## Overview
Yeh skill Playwright use karke WhatsApp Web monitor karti hai.
Jab koi business keyword wala message aaye, yeh `/Needs_Action/`
mein ek structured Markdown file banati hai taake Claude process kar sake.

## Steps
1. Playwright se WhatsApp Web kholo (persistent session)
2. Har 60 seconds mein naye unread messages check karo
3. Business keywords match karo:
   `urgent, asap, emergency, invoice, payment, quote,
   meeting, deadline, schedule, help, issue, problem,
   project, task, delivery`
4. Match hone pe `/Needs_Action/WHATSAPP_YYYYMMDD_HHMMSS.md` banao
5. Priority set karo: HIGH (urgent/asap/emergency), NORMAL (baaki)
6. Processed messages track karo (duplicates skip)
7. Rate limit: max 20 files per hour
8. Har action `/Logs/whatsapp_watcher.log` mein log karo

## Rules
- Kabhi bhi koi message automatically mat bhejo
- Already processed messages skip karo (sender+text ID track karo)
- DRY_RUN=true pe files mat banao, sirf log karo
- Max 20 action files per hour — limit reach hone pe warning log karo
- Har crash ke baad automatically restart ho
- Session `whatsapp_session/` mein save karo (QR sirf ek baar)

## Output File Format
`/Needs_Action/WHATSAPP_YYYYMMDD_HHMMSS.md`

## Install Commands
```bash
pip install playwright python-dotenv
playwright install chromium
```

## Run Command
```bash
python Skills/whatsapp-watcher/scripts/whatsapp_watcher.py
```
