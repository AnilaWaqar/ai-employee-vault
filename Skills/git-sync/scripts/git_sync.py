"""
git_sync.py — Platinum Tier Phase 3
Auto-sync vault to GitHub every 5 minutes.
Runs on BOTH Local PC and Cloud VM.

Usage:
  python git_sync.py                    # uses VAULT_PATH below
  python git_sync.py --cloud            # uses Cloud VM path

PM2:
  pm2 start git_sync.py --interpreter python3 --name git-sync
"""

import subprocess
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime

# ── Paths ───────────────────────────────────────────────────────────────────
LOCAL_PATH = Path("E:/HC/AI_Employee_Vault")
CLOUD_PATH = Path("/home/ubuntu/AI_Employee_Vault")

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [git-sync] %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("git_sync")

SYNC_INTERVAL = 300  # 5 minutes


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def write_signal(vault: Path, message: str):
    """Write a conflict/error signal so agents can detect it."""
    signals_dir = vault / "Signals"
    signals_dir.mkdir(exist_ok=True)
    signal_file = signals_dir / "SYNC_ERROR.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""---
type: sync_error
created: {timestamp}
status: unresolved
---

## Git Sync Error

**Time:** {timestamp}

**Message:**
{message}

## Resolution
Human must manually resolve. Options:
- `git status` to see conflict
- `git merge --abort` to cancel
- Manually edit conflicting files then `git add . && git commit`

After resolving, delete this file.
"""
    signal_file.write_text(content)
    logger.warning(f"Signal written: {signal_file}")


def clear_signal(vault: Path):
    """Remove SYNC_ERROR signal if sync is healthy."""
    signal_file = vault / "Signals" / "SYNC_ERROR.md"
    if signal_file.exists():
        signal_file.unlink()
        logger.info("Cleared SYNC_ERROR signal — sync healthy")


def write_update(vault: Path, message: str):
    """Append activity to Updates/git_sync_activity.md"""
    updates_dir = vault / "Updates"
    updates_dir.mkdir(exist_ok=True)
    activity_file = updates_dir / "git_sync_activity.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with activity_file.open("a") as f:
        f.write(f"[{timestamp}] {message}\n")


def sync_vault(vault: Path):
    """Pull latest, then push any local changes."""
    logger.info(f"Syncing vault: {vault}")

    # 1. Stash any unstaged changes before pulling
    stash = run_git(["stash"], vault)
    stashed = "No local changes" not in stash.stdout and stash.returncode == 0

    # 2. Pull with rebase
    pull = run_git(["pull", "--rebase", "origin", "main"], vault)
    if pull.returncode != 0:
        err = pull.stderr.strip()
        logger.error(f"Pull failed: {err}")
        # Restore stash before giving up
        if stashed:
            run_git(["stash", "pop"], vault)
        write_signal(vault, f"Pull failed:\n```\n{err}\n```")
        return

    # 3. Restore stashed changes
    if stashed:
        pop = run_git(["stash", "pop"], vault)
        if pop.returncode != 0:
            logger.warning(f"Stash pop had conflicts: {pop.stderr.strip()}")

    # 2. Check for local changes
    status = run_git(["status", "--porcelain"], vault)
    if not status.stdout.strip():
        logger.info("No local changes — vault is up to date")
        clear_signal(vault)
        return

    # 3. Stage all tracked + new files (excluding gitignored)
    run_git(["add", "."], vault)

    # 4. Commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit = run_git(
        ["commit", "-m", f"Auto-sync {timestamp}"],
        vault,
    )
    if commit.returncode != 0:
        err = commit.stderr.strip()
        # "nothing to commit" is not an error
        if "nothing to commit" in err or "nothing to commit" in commit.stdout:
            logger.info("Nothing to commit after staging")
            clear_signal(vault)
            return
        logger.error(f"Commit failed: {err}")
        write_signal(vault, f"Commit failed:\n```\n{err}\n```")
        return

    # 5. Push
    push = run_git(["push", "origin", "main"], vault)
    if push.returncode != 0:
        err = push.stderr.strip()
        logger.error(f"Push failed: {err}")
        write_signal(vault, f"Push failed:\n```\n{err}\n```")
        return

    logger.info(f"Vault synced to GitHub — {timestamp}")
    write_update(vault, f"Vault synced to GitHub")
    clear_signal(vault)


def main():
    parser = argparse.ArgumentParser(description="AI Employee Vault Git Sync")
    parser.add_argument(
        "--cloud",
        action="store_true",
        help="Use Cloud VM path instead of local Windows path",
    )
    args = parser.parse_args()

    vault = CLOUD_PATH if args.cloud else LOCAL_PATH

    if not vault.exists():
        logger.error(f"Vault path not found: {vault}")
        return

    logger.info(f"Git sync started — vault: {vault} — interval: {SYNC_INTERVAL}s")

    while True:
        try:
            sync_vault(vault)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    main()
