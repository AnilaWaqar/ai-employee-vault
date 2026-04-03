"""
signals_writer.py — Platinum Tier Phase 7.5
Cloud VM pe run hoga.
Cloud Agent signal likhta hai /Signals/ mein.
Local Agent yeh signals padhta hai aur respond karta hai.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

VAULT   = Path(os.getenv("VAULT_PATH", "/home/ubuntu/AI_Employee_Vault"))
SIGNALS = VAULT / "Signals"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SIGNAL_WRITER] %(message)s"
)
log = logging.getLogger("signals_writer")


def write_signal(signal_type: str, message: str, data: dict = None):
    """
    Cloud Agent signal likhta hai /Signals/ mein.

    Signal types:
      HEALTH_CHECK      — Regular ping (har ghante)
      APPROVAL_EXPIRED  — 24hr se approval nahi mila
      TASK_FAILED       — Task process nahi hua
      SYNC_CONFLICT     — Git conflict detect hua
      CLOUD_DOWN        — Cloud Agent crash/restart (watchdog likhta hai)
    """
    SIGNALS.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    signal_file = SIGNALS / f"{signal_type}_{timestamp}.md"

    content = f"""---
signal_type: {signal_type}
written_by: cloud_agent
timestamp: {datetime.now().isoformat()}
status: unread
---

## Signal: {signal_type}

{message}

## Data
```json
{json.dumps(data or {}, indent=2)}
```

## To Acknowledge
Yeh file /Signals/Acknowledged/ mein move ho jayegi jab Local Agent padh le.
"""
    signal_file.write_text(content, encoding="utf-8")
    log.info(f"Signal written: {signal_file.name}")
    return signal_file


def send_health_check(uptime: str = "unknown", tasks_done: int = 0):
    """Har ghante Cloud Agent health check bhejta hai."""
    write_signal(
        "HEALTH_CHECK",
        f"Cloud Agent alive aur chal raha hai.",
        {"uptime": uptime, "tasks_processed": tasks_done}
    )


def send_approval_expired(task_name: str):
    """24 ghante mein koi approval nahi mila."""
    write_signal(
        "APPROVAL_EXPIRED",
        f"Task ko 24 ghante se approval nahi mila — expire ho gaya.",
        {"task": task_name}
    )


def send_task_failed(task_name: str, error: str):
    """Task process nahi hua."""
    write_signal(
        "TASK_FAILED",
        f"Task process karte waqt error aayi.",
        {"task": task_name, "error": error}
    )


def send_sync_conflict(details: str):
    """Git sync conflict detect hua."""
    write_signal(
        "SYNC_CONFLICT",
        f"Git sync conflict — manual resolution chahiye!",
        {"details": details}
    )


if __name__ == "__main__":
    # Test signal
    send_health_check(uptime="1h", tasks_done=5)
    log.info("Test health check signal bheja gaya.")
