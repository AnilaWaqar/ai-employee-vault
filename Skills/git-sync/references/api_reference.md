# Git Sync — API Reference

## Git Commands Used
- `git pull --rebase origin main` — Pull latest changes
- `git add .` — Stage all changes
- `git commit -m "Auto-sync YYYY-MM-DD HH:MM"` — Commit
- `git push origin main` — Push to GitHub
- `git status --porcelain` — Check for local changes
- `git diff --cached --name-only` — List staged files

## Environment Variables
- `VAULT_PATH` — Path to vault root
- `SYNC_INTERVAL` — Seconds between syncs (default: 300)

## Rules
- NEVER auto-resolve git conflicts
- On conflict → write to /Signals/SYNC_CONFLICT.md
- Escalate to human always
