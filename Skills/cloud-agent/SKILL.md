---
name: cloud-agent
description: >
  Monitor Cloud Agent health, check draft status, manage claimed tasks,
  and alert human if cloud is down or stuck. Use this skill whenever the
  user mentions cloud agent, cloud drafts, check cloud status, what did
  cloud draft, cloud offline, cloud agent down, CLOUD_DOWN signal,
  In_Progress/cloud, or cloud orchestrator.
---

# Cloud Agent Skill

## Purpose
Monitor the Cloud Agent (cloud_orchestrator.py) health, report what it has
drafted, detect if it is down, and surface signals to the human.

## Trigger Phrases
Use this skill when user says:
- "check cloud agent status"
- "what did cloud draft?"
- "cloud agent down" / "cloud offline"
- "CLOUD_DOWN signal"
- "what's in In_Progress/cloud?"
- "cloud orchestrator not working"
- "cloud kya kar raha hai"
- "check cloud"

## Input
- /In_Progress/cloud/ folder contents
- /Pending_Approval/ folder (CLOUD_ prefix files)
- /Updates/cloud_activity.md (last activity)
- /Signals/CLOUD_DOWN.md (if exists)

## Steps

1. **Check In_Progress/cloud/** for claimed tasks:
   ```
   List files in: In_Progress/cloud/
   ```
   Report count and filenames.

2. **Check Pending_Approval/** for cloud drafts:
   ```
   List files matching: CLOUD_*_approval.md
   ```
   For each file: show task_ref, created timestamp, sensitive flag.

3. **Check Signals/CLOUD_DOWN.md**:
   - If exists → read and report the error to human
   - If absent → cloud agent is healthy

4. **Check Updates/cloud_activity.md**:
   - Read last 5 lines
   - Report last activity timestamp
   - If last activity > 10 minutes ago → flag as potentially stale

5. **Report status** in this format:
   ```
   Cloud Agent Status — [timestamp]
   ──────────────────────────────────
   In Progress:    [N tasks claimed]
   Drafts pending: [N approval files]
   Last activity:  [timestamp]
   Signal:         None / CLOUD_DOWN (see Signals/)
   Health:         ✅ OK / ⚠️ WARNING / ❌ ERROR

   Pending Approvals:
   - CLOUD_EMAIL_xyz_approval.md (sensitive: false)
   - ...
   ```

6. **If CLOUD_DOWN signal exists:**
   - Do NOT restart the agent automatically
   - Report exact error to human
   - Suggest: SSH to VM and check `pm2 logs cloud-orchestrator`

7. **If drafts are pending approval:**
   - List them clearly
   - Remind human: move to /Approved to send, or /Rejected to discard

## Output Format
Status report as shown in Step 5.
Always end with Health line (✅/⚠️/❌).

## Rules
- Never approve or reject drafts on behalf of human
- Never restart cloud_orchestrator.py automatically
- Never move files from In_Progress/cloud/ back to Needs_Action/ — only the script does that on error
- CLOUD_ prefix files in Pending_Approval/ were drafted by Cloud Agent — always show them clearly
- Sensitive drafts (sensitive: true) must be flagged prominently

## Error Handling
- If In_Progress/cloud/ missing: "Cloud agent folders not set up — run Phase 4 setup"
- If Updates/cloud_activity.md missing: "Cloud agent may never have run — check CLAUDE_API_KEY in .env"
- If CLOUD_DOWN.md exists: surface the error, do not auto-fix
