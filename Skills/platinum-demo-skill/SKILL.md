---
name: platinum-demo-skill
description: >
  Runs through the full Platinum tier demo scenario and verifies
  all components are working. Use this skill when preparing for
  demo, testing the offline resilience scenario, or checking
  Platinum status. Trigger on: "run demo", "test platinum",
  "offline test", "prepare demo", "demo video", "check platinum
  status", "platinum demo", "dual agent test".
---

# Platinum Demo Skill

## Purpose
Execute and verify the complete Platinum tier demo scenario
including the offline resilience test.

## Trigger Phrases
Use this skill when user says:
- "run demo"
- "test platinum"
- "offline test karo"
- "prepare demo"
- "demo video"
- "check platinum status"
- "dual agent test"
- "sab theek chal raha hai?"

## Input
- Cloud VM SSH access (13.200.252.166)
- /Signals/, /Updates/, /In_Progress/, /Pending_Approval/ folders
- Odoo health endpoint
- git sync status

## Steps
1. Check PM2 status on Cloud VM (via SSH)
2. Check git_sync.py running on both sides
3. Check Odoo health at http://13.200.252.166:8069
4. Check /Signals/ for any unread alerts
5. Check /Updates/ for cloud activity
6. Check /In_Progress/cloud/ for active tasks
7. Check /Pending_Approval/ for drafts from Cloud Agent
8. Send a test email to monitored account (if requested)
9. Verify Cloud Agent detects and drafts it
10. Verify draft appears in /Pending_Approval/
11. Move to /Approved/ and verify Local Agent executes
12. Verify task moves to /Done/
13. Print PASS/FAIL checklist for each step

## Output Format
Checklist with PASS/FAIL per step:
- [ ] Cloud VM online
- [ ] Git sync active
- [ ] Odoo accessible
- [ ] Cloud Agent processing
- [ ] Local Agent executing
- [ ] Dashboard updated

## Rules
- DRY_RUN=true shows steps without executing
- Log all results to /Logs/demo_YYYY-MM-DD.md
- Report any FAIL immediately to human
