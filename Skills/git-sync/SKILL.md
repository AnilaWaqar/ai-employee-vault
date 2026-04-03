---
name: git-sync
description: >
  Monitor vault Git sync status, detect conflicts, report health, and alert
  human when sync fails. Use this skill whenever the user mentions sync,
  git conflict, vault not syncing, check sync status, git pull failed,
  push failed, SYNC_ERROR, or cloud/local out of sync.
---

# Git Sync Skill

## Purpose
Monitor the vault's GitHub sync health, detect conflicts or errors, and
alert the human — never auto-resolve conflicts.

## Trigger Phrases
Use this skill when user says:
- "check sync status"
- "git sync failed" / "push failed" / "pull failed"
- "vault not syncing" / "cloud out of sync"
- "is the vault up to date?"
- "SYNC_ERROR signal"
- "sync theek hai?"
- "git conflict"

## Input
- Vault root git status
- /Updates/git_sync_activity.md (last sync timestamp)
- /Signals/SYNC_ERROR.md (if exists)
- git log (last 3 commits)

## Steps

1. **Check git status** in vault root:
   ```bash
   cd E:/HC/AI_Employee_Vault && git status
   ```
   Report: branch, ahead/behind, untracked files, conflicts.

2. **Check last sync timestamp** from Updates/git_sync_activity.md:
   - Read last line of file
   - If file missing or older than 10 minutes → flag as stale

3. **Check for conflict signal** at Signals/SYNC_ERROR.md:
   - If exists → read it and report the error to human
   - If absent → sync is healthy

4. **Check git log** for last 3 commits:
   ```bash
   git log --oneline -3
   ```
   Confirm latest commit matches expected auto-sync pattern.

5. **Report status** in this format:
   ```
   Git Sync Status — [timestamp]
   ──────────────────────────────
   Branch:      main
   Remote:      origin (github.com/...)
   Last sync:   [time from activity log]
   Local ahead: [N commits]
   Conflicts:   None / [list files]
   Signal:      None / SYNC_ERROR (see Signals/)
   Health:      ✅ OK / ⚠️ WARNING / ❌ ERROR
   ```

6. **If conflict detected:**
   - Do NOT auto-resolve
   - Write details to Signals/SYNC_ERROR.md (if not already written)
   - Tell human: exact files conflicting, recommended resolution steps
   - Update Dashboard.md with warning

7. **If sync is healthy:** confirm status to human, no action needed.

## Output Format
Plain text status report as shown in Step 5.
Always end with Health line (✅/⚠️/❌).

## Rules
- Never run `git merge --abort` or `git reset --hard` without explicit human approval
- Never delete Signals/SYNC_ERROR.md — only the sync script clears it after successful sync
- Never commit credentials, .env, or session files
- If in doubt about a conflict → escalate to human, do not guess

## Error Handling
- If `git status` fails (not a git repo): report "Vault is not a git repository — run git init"
- If Updates/git_sync_activity.md missing: report "Sync script may not be running — start git_sync.py"
- If Signals/SYNC_ERROR.md exists: always surface it, never ignore
