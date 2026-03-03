"""
Windows Task Scheduler Setup — Silver Tier Feature 6
2 scheduled tasks register karo:
  1. AI-Employee-Daily-Briefing  → Daily 8:00 AM
  2. AI-Employee-Weekly-Audit    → Every Sunday 10:00 PM
Run as Administrator for best results.
"""

import subprocess
import sys
from pathlib import Path

VAULT_PATH   = Path("E:/HC/AI_Employee_Vault")
PYTHON_EXE   = sys.executable  # current Python interpreter

DAILY_SCRIPT  = str(VAULT_PATH / "Skills/orchestrator/scripts/daily_briefing.py").replace("/", "\\")
WEEKLY_SCRIPT = str(VAULT_PATH / "Skills/orchestrator/scripts/weekly_audit.py").replace("/", "\\")
WORK_DIR      = str(VAULT_PATH).replace("/", "\\")
PYTHON_WIN    = PYTHON_EXE.replace("/", "\\")


def run_ps(script: str, desc: str) -> bool:
    """PowerShell script run karo."""
    print(f"[..] {desc}")
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"[OK] {desc}")
        return True
    else:
        print(f"[ERROR] {desc}")
        print(f"       {result.stderr.strip()}")
        return False


def create_daily_briefing():
    ps = f"""
$action  = New-ScheduledTaskAction `
    -Execute "{PYTHON_WIN}" `
    -Argument '"{DAILY_SCRIPT}"' `
    -WorkingDirectory "{WORK_DIR}"

$trigger = New-ScheduledTaskTrigger -Daily -At "08:00AM"

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Unregister-ScheduledTask -TaskName "AI-Employee-Daily-Briefing" -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName "AI-Employee-Daily-Briefing" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "AI Employee daily briefing — Dashboard + Plans update" `
    -RunLevel Highest `
    -Force
"""
    return run_ps(ps, "Creating Daily Briefing task (8:00 AM)")


def create_weekly_audit():
    ps = f"""
$action  = New-ScheduledTaskAction `
    -Execute "{PYTHON_WIN}" `
    -Argument '"{WEEKLY_SCRIPT}"' `
    -WorkingDirectory "{WORK_DIR}"

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "10:00PM"

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 2)

Unregister-ScheduledTask -TaskName "AI-Employee-Weekly-Audit" -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName "AI-Employee-Weekly-Audit" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "AI Employee weekly audit — 7-day activity summary" `
    -RunLevel Highest `
    -Force
"""
    return run_ps(ps, "Creating Weekly Audit task (Sunday 10:00 PM)")


def verify_tasks():
    ps = """
Get-ScheduledTask | Where-Object {$_.TaskName -like "AI-Employee-*"} |
    Select-Object TaskName, State |
    Format-Table -AutoSize
"""
    print("\n[..] Verifying registered tasks...")
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        capture_output=True, text=True
    )
    print(result.stdout.strip() if result.stdout.strip() else "(No output)")


def main():
    print("=" * 55)
    print("  AI Employee — Windows Task Scheduler Setup")
    print("=" * 55)
    print(f"  Python:       {PYTHON_WIN}")
    print(f"  Daily script: {DAILY_SCRIPT}")
    print(f"  Weekly script:{WEEKLY_SCRIPT}")
    print(f"  Work dir:     {WORK_DIR}")
    print("=" * 55)
    print()

    ok1 = create_daily_briefing()
    ok2 = create_weekly_audit()

    verify_tasks()

    print()
    print("=" * 55)
    if ok1 and ok2:
        print("  Setup Complete!")
        print("  Daily Briefing  → Every day at 8:00 AM")
        print("  Weekly Audit    → Every Sunday at 10:00 PM")
        print()
        print("  Output files:")
        print("  Plans/BRIEFING_YYYYMMDD.md")
        print("  Plans/WEEKLY_AUDIT_YYYYMMDD.md")
    else:
        print("  Partial setup — some tasks may have failed.")
        print("  Try running as Administrator.")
    print("=" * 55)


if __name__ == "__main__":
    main()
