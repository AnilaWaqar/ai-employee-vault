"""
Daily Briefing — Silver Tier Feature 6
Har roz 8AM pe run hota hai (Windows Task Scheduler).
Dashboard update karo + Plans/ mein briefing file banao.
"""

import os
import re
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parents[3] / ".env")

VAULT_PATH = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))

NEEDS_ACTION_DIR = VAULT_PATH / "Needs_Action"
DRAFTS_DIR       = VAULT_PATH / "Drafts"
PENDING_DIR      = VAULT_PATH / "Pending_Approval"
APPROVED_DIR     = VAULT_PATH / "Approved"
DONE_DIR         = VAULT_PATH / "Done"
REJECTED_DIR     = VAULT_PATH / "Rejected"
PLANS_DIR        = VAULT_PATH / "Plans"
LOGS_DIR         = VAULT_PATH / "Logs"
DASHBOARD        = VAULT_PATH / "Dashboard.md"

# ── Logging ───────────────────────────────────────────────────────────────────
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "daily_briefing.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("daily-briefing")


def count_files(folder: Path, pattern: str = "*.md") -> int:
    try:
        return len(list(folder.glob(pattern)))
    except Exception:
        return 0


def read_recent_log() -> str:
    """Aaj ka log file padhta hai — recent activity summary."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"{today}.md"
    if not log_file.exists():
        return "No activity logged today yet."
    try:
        text = log_file.read_text(encoding="utf-8")
        # Count actions
        actions = re.findall(r'^###\s+\d{2}:\d{2}:\d{2}', text, re.MULTILINE)
        return f"{len(actions)} action(s) logged today."
    except Exception:
        return "Could not read today's log."


def update_dashboard(counts: dict):
    try:
        if not DASHBOARD.exists():
            return
        text = DASHBOARD.read_text(encoding="utf-8")
        for folder, count in counts.items():
            text = re.sub(
                rf'(\*\*{folder}\*\*.*?)\d+',
                lambda m, c=count: m.group(0)[:-len(str(int(m.group(0).split()[-1])))] + str(c),
                text
            )
        # Update last updated timestamp
        text = re.sub(
            r'(Last Updated:?\s*)[\d\-: ]+',
            lambda m: m.group(1) + datetime.now().strftime("%Y-%m-%d %H:%M"),
            text
        )
        DASHBOARD.write_text(text, encoding="utf-8")
        log.info("Dashboard.md updated.")
    except Exception as e:
        log.warning(f"Dashboard update failed: {e}")


def create_briefing(counts: dict, activity: str) -> Path:
    today     = datetime.now().strftime("%Y%m%d")
    filename  = f"BRIEFING_{today}.md"
    filepath  = PLANS_DIR / filename

    # Determine system health
    needs_action = counts.get("Needs_Action", 0)
    pending      = counts.get("Pending_Approval", 0)
    alerts       = []
    if needs_action > 5:
        alerts.append(f"⚠️  {needs_action} emails waiting in Needs_Action/ — process soon")
    if pending > 3:
        alerts.append(f"⚠️  {pending} items in Pending_Approval/ — review needed")
    if not alerts:
        alerts.append("✅ System healthy — no urgent items")

    content = f"""---
type: daily_briefing
created: {datetime.now().isoformat()}
date: {datetime.now().strftime("%Y-%m-%d")}
---

# Daily Briefing — {datetime.now().strftime("%A, %B %d %Y")}

Generated at **{datetime.now().strftime("%I:%M %p")}** by AI Employee.

## System Status

| Folder | Count |
|--------|-------|
| Needs_Action | {counts.get("Needs_Action", 0)} |
| Drafts | {counts.get("Drafts", 0)} |
| Pending_Approval | {counts.get("Pending_Approval", 0)} |
| Approved (waiting) | {counts.get("Approved", 0)} |
| Done | {counts.get("Done", 0)} |
| Rejected | {counts.get("Rejected", 0)} |
| Plans | {counts.get("Plans", 0)} |

## Today's Activity
{activity}

## Alerts
{chr(10).join(alerts)}

## Processes Running (PM2)
- `master-pipeline` — Gmail fetch + send + dashboard
- `whatsapp-watcher` — WhatsApp Web monitor
- `linkedin-poster` — LinkedIn post queue
- `orchestrator` — Approved/Rejected handler
- `plan-creator` — Needs_Action/ plan generator

## Action Items
- [ ] Review `Needs_Action/` if count > 0
- [ ] Review `Pending_Approval/` items
- [ ] Check `pm2 status` for any crashed processes
- [ ] Run `/inbox-processor` if emails are waiting
"""

    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    log.info(f"Briefing created: {filename}")
    return filepath


def run():
    log.info("=" * 50)
    log.info(f"Daily Briefing — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log.info("=" * 50)

    counts = {
        "Needs_Action":     count_files(NEEDS_ACTION_DIR),
        "Drafts":           count_files(DRAFTS_DIR),
        "Pending_Approval": count_files(PENDING_DIR),
        "Approved":         count_files(APPROVED_DIR),
        "Done":             count_files(DONE_DIR),
        "Rejected":         count_files(REJECTED_DIR),
        "Plans":            count_files(PLANS_DIR),
    }

    for folder, count in counts.items():
        log.info(f"  {folder}: {count}")

    activity = read_recent_log()
    log.info(f"Activity: {activity}")

    update_dashboard(counts)
    briefing = create_briefing(counts, activity)

    log.info("Daily briefing complete.")
    log.info(f"Briefing file: {briefing.name}")


if __name__ == "__main__":
    run()
