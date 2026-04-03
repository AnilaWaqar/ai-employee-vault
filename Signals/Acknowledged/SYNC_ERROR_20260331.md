---
type: sync_error
created: 2026-03-31 06:54:23
status: unresolved
---

## Git Sync Error

**Time:** 2026-03-31 06:54:23

**Message:**
Pull failed:
```
error: cannot pull with rebase: You have unstaged changes.
error: Please commit or stash them.
```

## Resolution
Human must manually resolve. Options:
- `git status` to see conflict
- `git merge --abort` to cancel
- Manually edit conflicting files then `git add . && git commit`

After resolving, delete this file.
