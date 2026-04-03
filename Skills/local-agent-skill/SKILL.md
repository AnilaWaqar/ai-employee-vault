---
name: local-agent-skill
description: >
  Manages the Local Agent on the PC. Handles pending approvals,
  executes approved tasks, reads cloud signals, and updates Dashboard.
  Use this skill when user asks about pending approvals, local agent
  status, or wants to process approved files. Trigger on: "pending
  approvals", "local agent", "approve this", "what needs approval",
  "execute send", "process approved", "local agent status".
---

# Local Agent Skill

## Purpose
Manage approvals, check pending items, execute approved actions,
and read signals from Cloud Agent.

## Trigger Phrases
Use this skill when user says:
- "pending approvals dikhao"
- "local agent status"
- "approve this"
- "kya approve karna hai?"
- "execute send"
- "process approved files"
- "local agent kya kar raha hai"

## Input
- /Pending_Approval/ folder contents
- /Approved/ folder contents
- /Signals/ unread files
- /In_Progress/local/ claimed tasks

## Steps
1. List all files in /Pending_Approval/
2. Show summary to human (from, subject, action required)
3. Read any unread signals from /Signals/
4. Check /In_Progress/local/ for claimed tasks
5. For approved files in /Approved/ — trigger orchestrator.py
6. Log result to /Logs/YYYY-MM-DD.md
7. Update Dashboard.md
8. Move completed tasks to /Done/

## Output Format
- Pending approvals list with action required
- Signals summary
- Recent activity log

## Rules
- Local Agent ONLY executes after human moves file to /Approved/
- Never send emails without approved file in /Approved/
- Always log every action
- WhatsApp actions LOCAL ONLY — never on Cloud
- DRY_RUN=true must be supported
