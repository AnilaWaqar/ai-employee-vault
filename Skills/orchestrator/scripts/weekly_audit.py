"""
Weekly Audit — Silver Tier Feature 6
Har Sunday 10PM pe run hota hai (Windows Task Scheduler).
Pichle 7 din ka activity summary banao → Plans/WEEKLY_AUDIT_*.md
"""

import os
import re
import logging
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parents[3] / ".env")

VAULT_PATH = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))

DONE_DIR  = VAULT_PATH / "Done"
LOGS_DIR  = VAULT_PATH / "Logs"
PLANS_DIR = VAULT_PATH / "Plans"

# ── Logging ───────────────────────────────────────────────────────────────────
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "weekly_audit.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("weekly-audit")


def read_week_logs() -> dict:
    """Pichle 7 din ke log files padhta hai — stats nikalta hai."""
    stats = {
        "emails_processed": 0,
        "drafts_created": 0,
        "emails_sent": 0,
        "linkedin_posts": 0,
        "whatsapp_alerts": 0,
        "plans_created": 0,
        "approvals_reviewed": 0,
        "files_expired": 0,
        "files_rejected": 0,
        "total_actions": 0,
        "active_days": [],
    }

    today = datetime.now()
    for i in range(7):
        date     = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        log_file = LOGS_DIR / f"{date_str}.md"

        if not log_file.exists():
            continue

        stats["active_days"].append(date_str)
        try:
            text = log_file.read_text(encoding="utf-8").lower()

            # Count by action type
            stats["emails_sent"]        += len(re.findall(r'email sent|send_email.*sent', text))
            stats["drafts_created"]     += len(re.findall(r'draft created|draft response', text))
            stats["linkedin_posts"]     += len(re.findall(r'post successfully published|linkedin post.*posted', text))
            stats["whatsapp_alerts"]    += len(re.findall(r'whatsapp.*acknowledged|whatsapp message', text))
            stats["plans_created"]      += len(re.findall(r'plan created|plan creator', text))
            stats["approvals_reviewed"] += len(re.findall(r'approval reviewed|reviewed', text))
            stats["files_expired"]      += len(re.findall(r'expired', text))
            stats["files_rejected"]     += len(re.findall(r'rejected', text))

            all_actions = re.findall(r'^###\s+\d{2}:\d{2}:\d{2}', log_file.read_text(encoding="utf-8"), re.MULTILINE)
            stats["total_actions"] += len(all_actions)

        except Exception as e:
            log.warning(f"Could not read log {date_str}: {e}")

    return stats


def count_done_this_week() -> dict:
    """Done/ folder mein is hafte ki files count karo."""
    counts = {
        "SENT": 0, "FAILED": 0, "REJECTED": 0,
        "EXPIRED": 0, "REVIEWED": 0, "WHATSAPP": 0,
    }
    cutoff = datetime.now() - timedelta(days=7)
    try:
        for f in DONE_DIR.glob("*.md"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime >= cutoff:
                name = f.name.upper()
                for prefix in counts:
                    if name.startswith(prefix):
                        counts[prefix] += 1
                        break
    except Exception as e:
        log.warning(f"Done/ count error: {e}")
    return counts


def create_audit(stats: dict, done_counts: dict) -> Path:
    today    = datetime.now()
    week_end = today.strftime("%Y-%m-%d")
    week_start = (today - timedelta(days=6)).strftime("%Y-%m-%d")
    filename = f"WEEKLY_AUDIT_{today.strftime('%Y%m%d')}.md"
    filepath = PLANS_DIR / filename

    active_days_str = (
        ", ".join(stats["active_days"]) if stats["active_days"] else "No activity logged"
    )

    # Health score (simple)
    sent     = done_counts.get("SENT", 0)
    failed   = done_counts.get("FAILED", 0)
    success_rate = (
        f"{(sent / (sent + failed) * 100):.0f}%" if (sent + failed) > 0 else "N/A"
    )

    content = f"""---
type: weekly_audit
created: {today.isoformat()}
week: {week_start} to {week_end}
---

# Weekly Audit — {week_start} to {week_end}

Generated at **{today.strftime("%I:%M %p")}** on **{today.strftime("%A, %B %d %Y")}**.

## Activity Summary (Last 7 Days)

| Metric | Count |
|--------|-------|
| Total Actions Logged | {stats["total_actions"]} |
| Emails Sent | {stats["emails_sent"]} |
| Drafts Created | {stats["drafts_created"]} |
| LinkedIn Posts | {stats["linkedin_posts"]} |
| WhatsApp Alerts | {stats["whatsapp_alerts"]} |
| Plans Created | {stats["plans_created"]} |
| Approvals Reviewed | {stats["approvals_reviewed"]} |
| Files Expired (24h) | {stats["files_expired"]} |
| Files Rejected | {stats["files_rejected"]} |

## Done/ Folder This Week

| Status | Count |
|--------|-------|
| SENT (emails delivered) | {done_counts.get("SENT", 0)} |
| FAILED | {done_counts.get("FAILED", 0)} |
| REJECTED | {done_counts.get("REJECTED", 0)} |
| EXPIRED | {done_counts.get("EXPIRED", 0)} |
| REVIEWED | {done_counts.get("REVIEWED", 0)} |

**Email Success Rate:** {success_rate}

## Active Days
{active_days_str}

## System Health Check
- [ ] Check `pm2 status` — all 5 processes online?
- [ ] Review any FAILED items in Done/
- [ ] Clear old EXPIRED files if Done/ is cluttered
- [ ] Check `linkedin_session/` — still valid?
- [ ] Check `whatsapp_session/` — still logged in?

## Notes
- Audit auto-generated by weekly_audit.py
- Next audit: Next Sunday 10PM
"""

    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    log.info(f"Weekly audit created: {filename}")
    return filepath


def run():
    log.info("=" * 50)
    log.info(f"Weekly Audit — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log.info("=" * 50)

    stats      = read_week_logs()
    done_stats = count_done_this_week()

    log.info(f"Total actions this week: {stats['total_actions']}")
    log.info(f"Emails sent: {stats['emails_sent']}")
    log.info(f"LinkedIn posts: {stats['linkedin_posts']}")
    log.info(f"Active days: {len(stats['active_days'])}")

    audit_file = create_audit(stats, done_stats)
    log.info(f"Audit complete: {audit_file.name}")


if __name__ == "__main__":
    run()
