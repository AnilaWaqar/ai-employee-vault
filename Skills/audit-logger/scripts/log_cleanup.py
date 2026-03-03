"""
Log Cleanup — Gold Tier Feature 8
Purane log files delete karo (30 din se zyada purane).
Monthly Task Scheduler se chalega.
"""

import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

VAULT    = Path("E:/HC/AI_Employee_Vault")
LOGS_DIR = VAULT / "Logs"
KEEP_DAYS = 30

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CLEANUP] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "log_cleanup.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger("log-cleanup")

# Yeh files kabhi delete mat karo
PROTECTED = {"audit-dashboard.md", "audit_logger.log", "log_cleanup.log", "watchdog.log"}


def run():
    now    = datetime.now()
    cutoff = now - timedelta(days=KEEP_DAYS)
    deleted = 0
    kept    = 0

    log.info("=" * 50)
    log.info(f"Log Cleanup — keeping last {KEEP_DAYS} days")
    log.info(f"Cutoff date: {cutoff.strftime('%Y-%m-%d')}")

    for f in LOGS_DIR.iterdir():
        if not f.is_file():
            continue
        if f.name in PROTECTED:
            continue

        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        if mtime < cutoff:
            try:
                f.unlink()
                log.info(f"Deleted: {f.name} (modified {mtime.strftime('%Y-%m-%d')})")
                deleted += 1
            except Exception as e:
                log.warning(f"Could not delete {f.name}: {e}")
        else:
            kept += 1

    log.info(f"Cleanup complete — deleted: {deleted}, kept: {kept}")
    print(f"Cleanup done: {deleted} files deleted, {kept} kept")


if __name__ == "__main__":
    run()
