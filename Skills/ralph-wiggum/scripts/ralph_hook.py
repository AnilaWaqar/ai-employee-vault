"""
Ralph Wiggum Stop Hook — Gold Tier Feature 6
Claude Code ka Stop Hook — task complete check karo.
Agar task incomplete hai toh Claude ko re-inject karo.

Claude Code Stop Hook format:
- Exit 0 = Claude band ho jaaye
- Exit 2 = Claude ko inject karo (stdout mein message)
"""

import sys
import json
from datetime import datetime
from pathlib import Path

VAULT = Path("E:/HC/AI_Employee_Vault")
TASK_FILE = VAULT / ".current_task"
DONE_DIR  = VAULT / "Done"
LOG_FILE  = VAULT / "Logs" / "ralph_hook.log"


def log(msg: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")


def main():
    # .current_task file nahi hai → Claude normally band ho
    if not TASK_FILE.exists():
        log("No .current_task found — allowing Claude to stop")
        sys.exit(0)

    # Task file padho
    try:
        task_data = json.loads(TASK_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"Task file parse error: {e} — allowing stop")
        sys.exit(0)

    task_id     = task_data.get("task_id", "")
    task_desc   = task_data.get("task", "")
    done_marker = task_data.get("done_marker", f"{task_id}_complete")
    max_loops   = task_data.get("max_loops", 10)
    loop_count  = task_data.get("loop_count", 0)

    # Max loops check — infinite loop se bachao
    if loop_count >= max_loops:
        log(f"Max loops ({max_loops}) reached for task: {task_id} — forcing stop")
        TASK_FILE.unlink(missing_ok=True)
        sys.exit(0)

    # Done/ mein done_marker file check karo
    done_files = [f.name for f in DONE_DIR.glob("*.md")]
    for done_file in done_files:
        if done_marker.lower() in done_file.lower():
            log(f"Task COMPLETE: {task_id} — marker found: {done_file}")
            TASK_FILE.unlink(missing_ok=True)
            sys.exit(0)

    # Task abhi incomplete hai — loop count update karo
    loop_count += 1
    task_data["loop_count"] = loop_count
    TASK_FILE.write_text(json.dumps(task_data, indent=2), encoding="utf-8")

    log(f"Task INCOMPLETE: {task_id} (loop {loop_count}/{max_loops}) — re-injecting")

    # Claude ko inject karo
    inject_msg = f"""Continue working on the current task (Loop {loop_count}/{max_loops}):

**Task:** {task_desc}

**Task ID:** {task_id}
**Done Marker:** Create a file in /Done/ containing "{done_marker}" in the filename when complete.

Check what has been done so far and continue until the task is fully complete.
If already done, create the done marker file now."""

    print(inject_msg)
    sys.exit(2)


if __name__ == "__main__":
    main()
