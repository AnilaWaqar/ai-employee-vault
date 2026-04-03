"""
signals_reader.py — Platinum Tier Phase 7.5
Local PC pe run hoga.
Cloud Agent ke signals padhta hai aur respond karta hai.
Orchestrator.py ke saath milke kaam karta hai.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

VAULT        = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))
SIGNALS      = VAULT / "Signals"
SIGNALS_ACK  = VAULT / "Signals" / "Acknowledged"
DASHBOARD    = VAULT / "Dashboard.md"
LOGS_DIR     = VAULT / "Logs"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SIGNAL_READER] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "signals_reader.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("signals_reader")


def update_dashboard(message: str):
    """Dashboard.md mein signal entry add karo."""
    if not DASHBOARD.exists():
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n- [{timestamp}] 📡 Signal: {message}"
    try:
        current = DASHBOARD.read_text(encoding="utf-8")
        marker = "## Cloud Agent Updates"
        if marker in current:
            updated = current.replace(marker, f"{marker}{entry}")
        else:
            updated = current + f"\n\n{marker}{entry}\n"
        DASHBOARD.write_text(updated, encoding="utf-8")
    except Exception as e:
        log.error(f"Dashboard update failed: {e}")


def handle_signal(signal_type: str, signal_file: Path):
    """Signal type ke hisaab se action lo."""
    log.info(f"Signal received: {signal_type}")

    if signal_type == "HEALTH_CHECK":
        log.info("Cloud Agent alive hai.")
        update_dashboard("Cloud Agent alive ✅")

    elif signal_type == "CLOUD_DOWN":
        log.warning("ALERT: Cloud Agent offline!")
        update_dashboard("⚠️ ALERT: Cloud Agent OFFLINE!")

    elif signal_type == "APPROVAL_EXPIRED":
        log.warning(f"Approval expired: {signal_file.name}")
        update_dashboard(f"⚠️ Approval expired: {signal_file.stem}")

    elif signal_type == "SYNC_CONFLICT":
        log.warning("Git sync conflict — MANUAL RESOLUTION NEEDED!")
        update_dashboard("⚠️ Git CONFLICT — manual resolution chahiye!")

    elif signal_type == "TASK_FAILED":
        log.warning(f"Task failed: {signal_file.name}")
        update_dashboard(f"❌ Task failed: {signal_file.stem}")

    else:
        log.info(f"Unknown signal: {signal_type}")

    # Signal acknowledge karo
    SIGNALS_ACK.mkdir(parents=True, exist_ok=True)
    dest = SIGNALS_ACK / signal_file.name
    shutil.move(str(signal_file), str(dest))
    log.info(f"Acknowledged: {signal_file.name}")


def read_signals():
    """Saare unread signals padho aur handle karo."""
    SIGNALS.mkdir(parents=True, exist_ok=True)

    signal_files = [f for f in SIGNALS.glob("*.md")]
    if not signal_files:
        log.info("Koi naya signal nahi.")
        return

    log.info(f"{len(signal_files)} signal(s) mili.")

    for signal_file in signal_files:
        # Signal type detect karo filename se
        name = signal_file.name
        if "HEALTH_CHECK" in name:
            handle_signal("HEALTH_CHECK", signal_file)
        elif "CLOUD_DOWN" in name:
            handle_signal("CLOUD_DOWN", signal_file)
        elif "APPROVAL_EXPIRED" in name:
            handle_signal("APPROVAL_EXPIRED", signal_file)
        elif "SYNC_CONFLICT" in name:
            handle_signal("SYNC_CONFLICT", signal_file)
        elif "TASK_FAILED" in name:
            handle_signal("TASK_FAILED", signal_file)
        else:
            handle_signal("UNKNOWN", signal_file)


if __name__ == "__main__":
    log.info("Signals Reader started")
    read_signals()
    log.info("Done.")
