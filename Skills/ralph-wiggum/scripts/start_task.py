"""
Ralph Wiggum Task Starter
Naya autonomous task shuru karo.

Usage:
  python start_task.py "Process all emails in Needs_Action/" TASK_EMAIL_001
  python start_task.py "Generate CEO briefing" TASK_BRIEFING_001
"""

import sys
import json
from datetime import datetime
from pathlib import Path

VAULT     = Path("E:/HC/AI_Employee_Vault")
TASK_FILE = VAULT / ".current_task"


def start_task(task_desc: str, task_id: str, max_loops: int = 10):
    task_data = {
        "task_id":     task_id,
        "task":        task_desc,
        "done_marker": f"{task_id}_complete",
        "started":     datetime.now().isoformat(),
        "max_loops":   max_loops,
        "loop_count":  0
    }
    TASK_FILE.write_text(json.dumps(task_data, indent=2), encoding="utf-8")
    print(f"Task started: {task_id}")
    print(f"Description: {task_desc}")
    print(f"Done marker: {task_id}_complete")
    print(f"Max loops: {max_loops}")
    print(f"\nTask file: {TASK_FILE}")
    print("\nAb Claude Code mein is task ko run karo.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python start_task.py <task_description> <task_id>")
        print('Example: python start_task.py "Process emails" TASK_EMAIL_001')
        sys.exit(1)

    task_desc = sys.argv[1]
    task_id   = sys.argv[2]
    max_loops = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    start_task(task_desc, task_id, max_loops)
