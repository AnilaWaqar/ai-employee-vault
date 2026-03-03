---
name: error-recovery
description: Watchdog system for AI Employee. Monitors all background processes,
detects crashes, auto-restarts (max 3 attempts), and alerts on failure.
---

# Error Recovery + Watchdog

## Role
Tu AI Employee ka System Guardian hai. Saare processes monitor karta hai
aur crash detect hone par auto-restart karta hai.

---

## Script
`watchdog.py` (vault root mein)

---

## Monitored Processes

| Process | Script |
|---------|--------|
| master-pipeline | `Skills/gmail-watcher/scripts/master_pipeline.py` |
| whatsapp-watcher | `Skills/whatsapp-watcher/scripts/whatsapp_watcher.py` |
| linkedin-poster | `Skills/linkedin-poster/scripts/linkedin_poster.py` |
| orchestrator | `orchestrator.py` |
| plan-creator | `Skills/plan-creator/scripts/plan_creator.py` |

---

## Recovery Logic

```
Process down?
  → Restart attempt 1/3
  → Restart attempt 2/3
  → Restart attempt 3/3
  → All failed → ALERT in Needs_Action/ + Dashboard update
```

---

## State File
`Skills/error-recovery/watchdog_state.json`

Tracks restart count aur last restart time per process.

---

## Run

```bash
# Foreground
python watchdog.py

# Background
pythonw watchdog.py
```

---

## Alert Format

`Needs_Action/ALERT_{PROCESS}_{TIMESTAMP}.md`

Dashboard.md mein bhi warning line add hoti hai.
