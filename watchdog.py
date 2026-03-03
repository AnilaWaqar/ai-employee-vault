"""
Watchdog — Gold Tier Feature 7
AI Employee ke saare processes monitor karo.
Crash detect ho toh auto-restart karo (max 3 attempts).
Failure pe Dashboard.md alert + Needs_Action/ file banao.
"""

import os
import sys
import time
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────
VAULT = Path("E:/HC/AI_Employee_Vault")
load_dotenv(VAULT / ".env")

LOGS_DIR        = VAULT / "Logs"
NEEDS_ACTION    = VAULT / "Needs_Action"
DASHBOARD       = VAULT / "Dashboard.md"
STATE_FILE      = VAULT / "Skills" / "error-recovery" / "watchdog_state.json"
CHECK_INTERVAL  = 30   # seconds
MAX_RESTARTS    = 3

LOGS_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WATCHDOG] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "watchdog.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("watchdog")

# ── Monitored Processes ───────────────────────────────────────────────────────
PROCESSES = {
    "master-pipeline": {
        "script": "Skills/gmail-watcher/scripts/master_pipeline.py",
        "name":   "Gmail Master Pipeline",
    },
    "whatsapp-watcher": {
        "script": "Skills/whatsapp-watcher/scripts/whatsapp_watcher.py",
        "name":   "WhatsApp Watcher",
    },
    "linkedin-poster": {
        "script": "Skills/linkedin-poster/scripts/linkedin_poster.py",
        "name":   "LinkedIn Poster",
    },
    "orchestrator": {
        "script": "orchestrator.py",
        "name":   "Orchestrator",
    },
    "plan-creator": {
        "script": "Skills/plan-creator/scripts/plan_creator.py",
        "name":   "Plan Creator",
    },
}


# ── State Management ──────────────────────────────────────────────────────────
def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {key: {"restarts": 0, "last_restart": None, "pid": None} for key in PROCESSES}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ── Process Detection ─────────────────────────────────────────────────────────
def get_running_scripts() -> dict:
    """Chal rahe Python processes aur unke scripts."""
    running = {}
    try:
        result = subprocess.run(
            ["wmic", "process", "where", "name='python.exe'", "get", "ProcessId,CommandLine"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or "CommandLine" in line:
                continue
            parts = line.rsplit(None, 1)
            if len(parts) == 2:
                cmd, pid = parts[0].strip(), parts[1].strip()
                if pid.isdigit():
                    running[cmd] = int(pid)
    except Exception as e:
        log.warning(f"Process list error: {e}")
    return running


def is_running(script_path: str, running_scripts: dict) -> tuple:
    """Script chal raha hai? (bool, pid)"""
    script_norm = script_path.replace("/", "\\").lower()
    for cmd, pid in running_scripts.items():
        if script_norm in cmd.replace("/", "\\").lower():
            return True, pid
    return False, None


# ── Process Restart ───────────────────────────────────────────────────────────
def restart_process(key: str, config: dict) -> bool:
    script = str(VAULT / config["script"])
    log.info(f"Restarting: {config['name']} ({script})")
    try:
        proc = subprocess.Popen(
            ["python", script],
            cwd=str(VAULT),
            stdout=open(LOGS_DIR / f"{key}.log", "a"),
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        log.info(f"Restarted: {config['name']} (PID {proc.pid})")
        return True
    except Exception as e:
        log.error(f"Restart failed for {config['name']}: {e}")
        return False


# ── Alert System ──────────────────────────────────────────────────────────────
def create_alert(key: str, config: dict, reason: str):
    now       = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename  = f"ALERT_{key.upper()}_{timestamp}.md"
    filepath  = NEEDS_ACTION / filename
    NEEDS_ACTION.mkdir(exist_ok=True)

    content = f"""---
type: system_alert
process: {key}
process_name: {config['name']}
alert_time: {now.isoformat()}
reason: {reason}
priority: high
requires_approval: false
---

# SYSTEM ALERT — {config['name']} Down

**Time:** {now.strftime("%Y-%m-%d %H:%M:%S")}
**Process:** {config['name']}
**Reason:** {reason}

## Action Required

- [ ] Check process logs: `Logs/{key}.log`
- [ ] Restart manually: `python {config['script']}`
- [ ] Check for errors in the script

## Auto-Recovery

Watchdog ne {MAX_RESTARTS} baar restart try kiya — sab fail ho gaye.
Manual intervention required.
"""
    filepath.write_text(content, encoding="utf-8")
    log.warning(f"ALERT created: {filename}")


def update_dashboard_alert(key: str, config: dict):
    if not DASHBOARD.exists():
        return
    try:
        text = DASHBOARD.read_text(encoding="utf-8")
        alert_line = f"\n> ⚠️ **WATCHDOG ALERT** — {config['name']} down at {datetime.now().strftime('%H:%M:%S')}\n"
        if "WATCHDOG ALERT" not in text:
            text = alert_line + text
        else:
            import re
            text = re.sub(r"> .*WATCHDOG ALERT.*\n", alert_line, text)
        DASHBOARD.write_text(text, encoding="utf-8")
    except Exception as e:
        log.warning(f"Dashboard update failed: {e}")


# ── Main Loop ─────────────────────────────────────────────────────────────────
def run():
    log.info("=" * 60)
    log.info("Watchdog started")
    log.info(f"Monitoring {len(PROCESSES)} processes | Check every {CHECK_INTERVAL}s")
    log.info("=" * 60)

    state = load_state()

    while True:
        running = get_running_scripts()

        for key, config in PROCESSES.items():
            is_up, pid = is_running(config["script"], running)

            if is_up:
                # Process chal raha hai — restart count reset karo
                if state[key]["restarts"] > 0:
                    log.info(f"Recovered: {config['name']} (PID {pid})")
                    state[key]["restarts"] = 0
                state[key]["pid"] = pid
            else:
                # Process down hai
                restarts = state[key]["restarts"]

                if restarts < MAX_RESTARTS:
                    log.warning(f"DOWN: {config['name']} — restart attempt {restarts + 1}/{MAX_RESTARTS}")
                    success = restart_process(key, config)
                    if success:
                        state[key]["restarts"] = restarts + 1
                        state[key]["last_restart"] = datetime.now().isoformat()
                    time.sleep(5)
                else:
                    # Max restarts exhausted — alert banao
                    if restarts == MAX_RESTARTS:
                        log.error(f"FAILED: {config['name']} — max restarts reached, creating alert")
                        create_alert(key, config, f"Process crashed {MAX_RESTARTS} times")
                        update_dashboard_alert(key, config)
                        state[key]["restarts"] = MAX_RESTARTS + 1  # Alert sent marker

        save_state(state)
        log.info(f"Check complete — next in {CHECK_INTERVAL}s")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()
