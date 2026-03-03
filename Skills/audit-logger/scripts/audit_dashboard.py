"""
Audit Dashboard Generator — Gold Tier Feature 8
Saare JSON logs analyze karo aur Logs/audit-dashboard.md banao.
Success rates, actor breakdown, platform stats, errors.
"""

import json
import re
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

VAULT    = Path("E:/HC/AI_Employee_Vault")
LOGS_DIR = VAULT / "Logs"
OUTPUT   = LOGS_DIR / "audit-dashboard.md"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AUDIT] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "audit_logger.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger("audit-logger")


def load_all_logs(days: int = 30) -> list:
    """Pichle N din ke saare JSON log entries load karo."""
    entries = []
    cutoff  = datetime.now() - timedelta(days=days)

    for log_file in sorted(LOGS_DIR.glob("*.json")):
        # Date parse karo filename se
        try:
            date_str = log_file.stem.split("_")[0]  # e.g. "2026-03-03" or "email_mcp_2026-03-03"
            # Last date part dhundo
            date_match = re.search(r"\d{4}-\d{2}-\d{2}", log_file.stem)
            if date_match:
                file_date = datetime.strptime(date_match.group(), "%Y-%m-%d")
                if file_date < cutoff:
                    continue
        except Exception:
            pass

        try:
            data = json.loads(log_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                entries.extend(data)
        except Exception as e:
            log.warning(f"Could not read {log_file.name}: {e}")

    return entries


def analyze(entries: list) -> dict:
    stats = {
        "total":          len(entries),
        "success":        0,
        "failed":         0,
        "dry_run":        0,
        "by_actor":       defaultdict(lambda: {"success": 0, "failed": 0}),
        "by_action":      defaultdict(lambda: {"success": 0, "failed": 0}),
        "by_date":        defaultdict(int),
        "errors":         [],
        "recent":         [],
    }

    for e in entries:
        result    = str(e.get("result", "")).lower()
        actor     = e.get("actor", "unknown")
        action    = e.get("action_type", "unknown")
        timestamp = e.get("timestamp", "")
        dry       = e.get("dry_run", False)

        # Date
        try:
            date = timestamp[:10]
            stats["by_date"][date] += 1
        except Exception:
            pass

        if dry:
            stats["dry_run"] += 1
            continue

        is_success = any(w in result for w in ["success", "sent", "created", "dry_run"]) or \
                     (result.startswith("success"))
        is_fail    = any(w in result for w in ["fail", "error", "timeout", "refused", "unauthorized",
                                                "forbidden", "rate_limit", "crash"])

        if is_success and not is_fail:
            stats["success"] += 1
            stats["by_actor"][actor]["success"] += 1
            stats["by_action"][action]["success"] += 1
        elif is_fail:
            stats["failed"] += 1
            stats["by_actor"][actor]["failed"] += 1
            stats["by_action"][action]["failed"] += 1
            # Recent errors (last 10)
            if len(stats["errors"]) < 10:
                stats["errors"].append({
                    "time":   timestamp[:16].replace("T", " "),
                    "actor":  actor,
                    "result": e.get("result", "")[:80],
                })
        else:
            stats["success"] += 1
            stats["by_actor"][actor]["success"] += 1
            stats["by_action"][action]["success"] += 1

        # Recent entries (last 5)
        if len(stats["recent"]) < 5:
            stats["recent"].append({
                "time":    timestamp[:16].replace("T", " "),
                "actor":   actor,
                "action":  action,
                "result":  e.get("result", "")[:50],
            })

    return stats


def generate_dashboard(stats: dict) -> str:
    now          = datetime.now()
    total        = stats["total"]
    success      = stats["success"]
    failed       = stats["failed"]
    dry          = stats["dry_run"]
    success_rate = f"{(success / max(success + failed, 1) * 100):.0f}%"

    # By actor table
    actor_rows = ""
    for actor, counts in sorted(stats["by_actor"].items()):
        s = counts["success"]
        f = counts["failed"]
        rate = f"{(s / max(s+f, 1) * 100):.0f}%"
        actor_rows += f"| {actor} | {s} | {f} | {rate} |\n"
    if not actor_rows:
        actor_rows = "| No data | - | - | - |\n"

    # By action table
    action_rows = ""
    for action, counts in sorted(stats["by_action"].items()):
        s = counts["success"]
        f = counts["failed"]
        action_rows += f"| {action} | {s} | {f} |\n"
    if not action_rows:
        action_rows = "| No data | - | - |\n"

    # Activity by date (last 7 days)
    date_rows = ""
    for i in range(6, -1, -1):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        count = stats["by_date"].get(d, 0)
        bar = "█" * min(count, 20) if count > 0 else "·"
        date_rows += f"| {d} | {count} | {bar} |\n"

    # Recent errors
    error_rows = ""
    for err in stats["errors"]:
        error_rows += f"| {err['time']} | {err['actor']} | {err['result']} |\n"
    if not error_rows:
        error_rows = "| - | - | No errors | \n"

    # Recent activity
    recent_rows = ""
    for r in stats["recent"]:
        recent_rows += f"| {r['time']} | {r['actor']} | {r['action']} | {r['result']} |\n"
    if not recent_rows:
        recent_rows = "| - | - | - | No data |\n"

    return f"""---
type: audit_dashboard
generated: {now.isoformat()}
period: Last 30 days
---

# Audit Dashboard

*Auto-generated: {now.strftime("%Y-%m-%d %H:%M")} | AI Employee Gold Tier*

---

## Overview

| Metric | Value |
|--------|-------|
| Total Actions | {total} |
| Successful | {success} |
| Failed | {failed} |
| Dry Run (skipped) | {dry} |
| **Success Rate** | **{success_rate}** |

---

## By Actor (Last 30 Days)

| Actor | Success | Failed | Rate |
|-------|---------|--------|------|
{actor_rows}
---

## By Action Type

| Action | Success | Failed |
|--------|---------|--------|
{action_rows}
---

## Daily Activity (Last 7 Days)

| Date | Actions | Chart |
|------|---------|-------|
{date_rows}
---

## Recent Errors (Last 10)

| Time | Actor | Error |
|------|-------|-------|
{error_rows}
---

## Recent Activity (Last 5)

| Time | Actor | Action | Result |
|------|-------|--------|--------|
{recent_rows}
---

*Next update: Run `python Skills/audit-logger/scripts/audit_dashboard.py`*
"""


def run():
    log.info("Generating audit dashboard...")
    entries   = load_all_logs(days=30)
    log.info(f"Loaded {len(entries)} log entries")
    stats     = analyze(entries)
    dashboard = generate_dashboard(stats)
    OUTPUT.write_text(dashboard, encoding="utf-8")
    log.info(f"Dashboard saved: {OUTPUT}")
    print(f"Audit dashboard generated: {OUTPUT}")


if __name__ == "__main__":
    run()
