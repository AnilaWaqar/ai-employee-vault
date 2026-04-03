"""
platinum_demo.py — Platinum Tier Phase 8
Demo checklist run karta hai — PASS/FAIL per step.
Local PC pe run hoga.
"""

import os
import sys
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Windows encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

VAULT    = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))
VM_IP    = os.getenv("CLOUD_VM_IP", "13.200.252.166")
LOGS_DIR = VAULT / "Logs"
DRY_RUN  = os.getenv("DRY_RUN", "false").lower() == "true"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
results = []


def check(name: str, passed: bool, detail: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"{status} | {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    results.append({"check": name, "passed": passed, "detail": detail})
    return passed


def check_git_sync():
    try:
        result = subprocess.run(
            ["git", "status"], cwd=str(VAULT),
            capture_output=True, text=True, timeout=10
        )
        check("Git sync active", result.returncode == 0)
    except Exception as e:
        check("Git sync active", False, str(e))


def check_odoo():
    try:
        resp = requests.get(f"http://{VM_IP}:8069/web/health", timeout=5)
        check("Odoo accessible", resp.status_code == 200)
    except Exception as e:
        check("Odoo accessible", False, str(e))


def check_signals():
    signals = list((VAULT / "Signals").glob("*.md"))
    check("Signals folder clean", len(signals) == 0, f"{len(signals)} unread")


def check_updates():
    updates = list((VAULT / "Updates").glob("cloud_*.md"))
    check("Updates processed", len(updates) == 0, f"{len(updates)} unprocessed")


def check_in_progress():
    cloud = list((VAULT / "In_Progress" / "cloud").glob("*.md"))
    local = list((VAULT / "In_Progress" / "local").glob("*.md"))
    check("In_Progress/cloud clean", len(cloud) == 0, f"{len(cloud)} tasks")
    check("In_Progress/local clean", len(local) == 0, f"{len(local)} tasks")


def check_pending():
    pending = list((VAULT / "Pending_Approval").glob("*.md"))
    check("Pending_Approval status", True, f"{len(pending)} items waiting")


def check_dashboard():
    dashboard = VAULT / "Dashboard.md"
    check("Dashboard.md exists", dashboard.exists())


def save_report():
    date = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"demo_{date}.md"
    passed = sum(1 for r in results if r["passed"])
    total = len(results)

    content = f"# Platinum Demo Report\nDate: {datetime.now().isoformat()}\nScore: {passed}/{total}\n\n## Results\n"
    for r in results:
        icon = "[PASS]" if r["passed"] else "[FAIL]"
        content += f"- {icon} {r['check']}"
        if r["detail"]:
            content += f" — {r['detail']}"
        content += "\n"

    log_file.write_text(content, encoding="utf-8")
    print(f"\nReport saved: {log_file.name}")


def run():
    print("=" * 50)
    print("Platinum Tier — Demo Checklist")
    print(f"DRY_RUN: {DRY_RUN}")
    print("=" * 50)

    check_git_sync()
    check_odoo()
    check_signals()
    check_updates()
    check_in_progress()
    check_pending()
    check_dashboard()

    print("=" * 50)
    passed = sum(1 for r in results if r["passed"])
    print(f"Final Score: {passed}/{len(results)}")
    save_report()


if __name__ == "__main__":
    run()
