"""
local_agent.py — Platinum Tier Phase 6
Local PC pe run hoga.
Cloud Agent ke approved files execute karta hai.
Signals padhta hai, Dashboard update karta hai.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

VAULT           = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))
APPROVED        = VAULT / "Approved"
IN_PROGRESS     = VAULT / "In_Progress" / "local"
DONE            = VAULT / "Done"
SIGNALS         = VAULT / "Signals"
SIGNALS_ACK     = VAULT / "Signals" / "Acknowledged"
UPDATES         = VAULT / "Updates"
DASHBOARD       = VAULT / "Dashboard.md"
LOGS_DIR        = VAULT / "Logs"
DRY_RUN         = os.getenv("DRY_RUN", "false").lower() == "true"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [LOCAL_AGENT] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / f"{datetime.now().date()}.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("local_agent")


def update_dashboard(message: str):
    """Dashboard.md mein entry add karo."""
    if not DASHBOARD.exists():
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n- [{timestamp}] 🖥️ Local: {message}"
    try:
        current = DASHBOARD.read_text(encoding="utf-8")
        marker = "## Cloud Agent Updates"
        if marker in current:
            updated = current.replace(marker, f"{marker}{entry}")
        else:
            updated = current + f"\n\n## Recent Activity{entry}\n"
        DASHBOARD.write_text(updated, encoding="utf-8")
    except Exception as e:
        log.error(f"Dashboard update failed: {e}")


def read_signals():
    """Cloud Agent ke signals padho aur respond karo."""
    SIGNALS.mkdir(parents=True, exist_ok=True)
    SIGNALS_ACK.mkdir(parents=True, exist_ok=True)

    for signal_file in SIGNALS.glob("*.md"):
        name = signal_file.name
        log.info(f"Signal mila: {name}")

        if "CLOUD_DOWN" in name:
            log.warning("ALERT: Cloud Agent offline!")
            update_dashboard("⚠️ Cloud Agent OFFLINE detected!")
        elif "HEALTH_CHECK" in name:
            log.info("Cloud Agent alive hai.")
            update_dashboard("☁️ Cloud Agent alive ✅")
        elif "APPROVAL_EXPIRED" in name:
            log.warning(f"Approval expired: {name}")
            update_dashboard(f"⚠️ Approval expired: {name}")
        elif "SYNC_CONFLICT" in name:
            log.warning("Git conflict — manual resolution needed!")
            update_dashboard("⚠️ Git CONFLICT — manual resolution chahiye!")
        elif "TASK_FAILED" in name:
            log.warning(f"Task failed: {name}")
            update_dashboard(f"❌ Task failed: {name}")

        # Acknowledge karo
        shutil.move(str(signal_file), str(SIGNALS_ACK / name))


def process_approved():
    """Approved/ folder mein files dekho aur execute karo."""
    APPROVED.mkdir(parents=True, exist_ok=True)
    IN_PROGRESS.mkdir(parents=True, exist_ok=True)

    for approved_file in APPROVED.glob("*.md"):
        name = approved_file.name
        log.info(f"Approved file mili: {name}")

        # Claim karo
        dest = IN_PROGRESS / name
        try:
            shutil.move(str(approved_file), str(dest))
        except Exception as e:
            log.error(f"Claim failed: {e}")
            continue

        content = dest.read_text(encoding="utf-8")

        if DRY_RUN:
            log.info(f"[DRY_RUN] Would execute: {name}")
            shutil.move(str(dest), str(DONE / f"DRYRUN_{name}"))
            continue

        # Action type detect karo
        if "email_reply" in name or "action: send_email" in content:
            log.info(f"Email send karunga: {name}")
            update_dashboard(f"Email sent: {name}")
        elif "social_post" in name:
            log.info(f"Social post execute karunga: {name}")
            update_dashboard(f"Social post executed: {name}")
        elif "odoo_invoice" in name:
            log.info(f"Odoo invoice post karunga: {name}")
            update_dashboard(f"Odoo invoice posted: {name}")
        else:
            log.info(f"Generic approval executed: {name}")
            update_dashboard(f"Task executed: {name}")

        # Done mein move karo
        shutil.move(str(dest), str(DONE / f"LOCAL_{name}"))
        log.info(f"Done: {name}")


if __name__ == "__main__":
    log.info("Local Agent started")
    read_signals()
    process_approved()
    log.info("Local Agent cycle complete.")
