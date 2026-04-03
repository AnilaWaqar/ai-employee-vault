---
name: signals-monitor-skill
description: >
  Reads and responds to agent signals from the /Signals/ folder.
  Use this skill when user asks about agent alerts, cloud signals,
  sync errors, or agent communication. Trigger on: "check signals",
  "any alerts", "agent signals", "cloud sent signal", "signal folder",
  "agent alert", "sync conflict", "cloud down", "approval expired".
---

# Signals Monitor Skill

## Purpose
Read unread signals from /Signals/, summarize for human, and
move read signals to /Signals/Acknowledged/.

## Trigger Phrases
Use this skill when user says:
- "check signals"
- "koi alerts hain?"
- "agent signals dikhao"
- "cloud sent signal"
- "signal folder check karo"
- "cloud down signal"
- "approval expired"

## Input
- /Signals/ folder — unread .md signal files
- /Signals/Acknowledged/ — already processed signals

## Steps
1. List all unread .md files in /Signals/ (exclude Acknowledged/)
2. For each signal file, read and extract: type, timestamp, message
3. Show summary to human in a table
4. For CLOUD_DOWN → flag as urgent, update Dashboard.md
5. For SYNC_CONFLICT → show conflict details, ask human to resolve
6. For APPROVAL_EXPIRED → list which tasks expired
7. For TASK_FAILED → show which task and error
8. For HEALTH_CHECK → show Cloud Agent is alive
9. Move all read signals to /Signals/Acknowledged/
10. Log to /Logs/YYYY-MM-DD.md

## Output Format
Table showing:
| Signal Type | Timestamp | Message | Action Taken |

## Scripts
- `signals_writer.py` — Cloud VM pe run hoga, signals likhta hai
- `signals_reader.py` — Local PC pe run hoga, signals padhta hai

## Rules
- NEVER auto-resolve git conflicts — always escalate to human
- NEVER delete signal files — only move to Acknowledged/
- Always update Dashboard.md after reading CLOUD_DOWN signal
- Log every signal read to /Logs/
- signals_writer.py Cloud VM pe hoga, signals_reader.py Local PC pe
