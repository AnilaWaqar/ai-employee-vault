"""
cloud_orchestrator.py — Platinum Tier Phase 4
Cloud Agent: watches Needs_Action/email/, drafts replies via Claude API,
creates approval files in Pending_Approval/ for Local Agent to review.

NEVER sends emails directly — all sends require human/Local Agent approval.

Usage (Cloud VM):
  python cloud_orchestrator.py

Environment variables required:
  CLAUDE_API_KEY       — Anthropic API key
  VAULT_PATH           — Override vault path (optional)

PM2:
  pm2 start cloud_orchestrator.py --interpreter python3 --name cloud-orchestrator
"""

import os
import time
import logging
import shutil
from pathlib import Path
from datetime import datetime

import anthropic
from dotenv import load_dotenv

load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────────
VAULT = Path(os.getenv("VAULT_PATH", "/home/ubuntu/AI_Employee_Vault"))

NEEDS_ACTION     = VAULT / "Needs_Action" / "email"
IN_PROGRESS      = VAULT / "In_Progress" / "cloud"
PENDING_APPROVAL = VAULT / "Pending_Approval"
UPDATES          = VAULT / "Updates"
SIGNALS          = VAULT / "Signals"
DONE             = VAULT / "Done"

CYCLE_INTERVAL = 120  # seconds

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [cloud-agent] %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("cloud_orchestrator")

# ── Claude API ────────────────────────────────────────────────────────────────
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None

SYSTEM_PROMPT = """You are an AI Employee assistant.
You read incoming email files and draft professional reply emails.

Rules:
- Be professional and concise
- Match the tone of the original email
- Never promise things without human approval
- If the email is sensitive (legal, financial, security, HR), say: SENSITIVE — requires human review
- Output ONLY the email reply text, no explanation or preamble
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def write_activity(message: str):
    """Append to Updates/cloud_activity.md"""
    UPDATES.mkdir(exist_ok=True)
    activity_file = UPDATES / "cloud_activity.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with activity_file.open("a") as f:
        f.write(f"[{timestamp}] {message}\n")


def write_signal(name: str, message: str):
    """Write a signal file for agent-to-agent communication."""
    SIGNALS.mkdir(exist_ok=True)
    signal_file = SIGNALS / name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""---
type: signal
created: {timestamp}
status: unresolved
---

{message}
"""
    signal_file.write_text(content)
    logger.warning(f"Signal written: {signal_file.name}")


def clear_signal(name: str):
    signal_file = SIGNALS / name
    if signal_file.exists():
        signal_file.unlink()


# ── Core Logic ────────────────────────────────────────────────────────────────

def claim_task(task_file: Path) -> bool:
    """
    Claim-by-move: atomically move file from Needs_Action/email/ to In_Progress/cloud/.
    First agent to move wins. If file already moved → return False.
    """
    try:
        dest = IN_PROGRESS / task_file.name
        task_file.rename(dest)
        logger.info(f"Claimed: {task_file.name}")
        return True
    except (FileNotFoundError, PermissionError):
        logger.info(f"Already claimed by another agent: {task_file.name}")
        return False


def draft_reply(task_file: Path) -> tuple[str, bool]:
    """
    Call Claude API to draft a reply for the email.
    Returns (draft_text, is_sensitive).
    """
    content = task_file.read_text(encoding="utf-8")

    if not claude_client:
        logger.warning("No CLAUDE_API_KEY — using placeholder draft")
        return f"[PLACEHOLDER DRAFT — set CLAUDE_API_KEY]\n\nOriginal email: {task_file.name}", False

    try:
        response = claude_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Draft a reply to this email:\n\n{content}"
                }
            ]
        )
        draft = response.content[0].text.strip()
        is_sensitive = draft.upper().startswith("SENSITIVE")
        return draft, is_sensitive

    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return f"[DRAFT FAILED — API error: {e}]", False


def create_approval_file(task_file: Path, draft: str, is_sensitive: bool):
    """Write approval request to Pending_Approval/ for human/Local Agent review."""
    PENDING_APPROVAL.mkdir(exist_ok=True)

    status_note = "⚠️ SENSITIVE — requires manual human review" if is_sensitive else "Ready for approval"
    timestamp = datetime.now().isoformat()

    approval_content = f"""---
type: approval_request
agent: cloud
action: email_send
task_ref: {task_file.name}
created: {timestamp}
expires: 24h
status: pending
sensitive: {str(is_sensitive).lower()}
---

## Cloud Agent Draft Reply

{draft}

---

## Status
{status_note}

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.
"""

    approval_file = PENDING_APPROVAL / f"CLOUD_{task_file.stem}_approval.md"
    approval_file.write_text(approval_content, encoding="utf-8")
    logger.info(f"Approval file created: {approval_file.name}")

    write_activity(
        f"Drafted reply for {task_file.name} → {approval_file.name}"
        + (" [SENSITIVE]" if is_sensitive else "")
    )


def process_tasks():
    """Scan Needs_Action/email/ and process any new EMAIL_*.md files."""
    if not NEEDS_ACTION.exists():
        NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
        return

    task_files = list(NEEDS_ACTION.glob("EMAIL_*.md"))
    if not task_files:
        return

    logger.info(f"Found {len(task_files)} task(s) in Needs_Action/email/")

    for task_file in task_files:
        if not claim_task(task_file):
            continue

        claimed = IN_PROGRESS / task_file.name

        try:
            draft, is_sensitive = draft_reply(claimed)
            create_approval_file(claimed, draft, is_sensitive)
            clear_signal("CLOUD_DOWN.md")

        except Exception as e:
            logger.error(f"Failed to process {claimed.name}: {e}")
            write_signal(
                "CLOUD_DOWN.md",
                f"## Cloud Agent Error\n\nFailed to process `{claimed.name}`:\n\n```\n{e}\n```\n\nManual intervention required."
            )
            # Move failed task back to Needs_Action so it can be retried
            try:
                shutil.move(str(claimed), str(NEEDS_ACTION / task_file.name))
            except Exception:
                pass


def run():
    logger.info(f"Cloud Orchestrator started — vault: {VAULT} — cycle: {CYCLE_INTERVAL}s")

    # Ensure all required directories exist
    for d in [NEEDS_ACTION, IN_PROGRESS, PENDING_APPROVAL, UPDATES, SIGNALS]:
        d.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            process_tasks()
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            write_signal(
                "CLOUD_DOWN.md",
                f"## Cloud Orchestrator Crashed\n\n```\n{e}\n```"
            )
        time.sleep(CYCLE_INTERVAL)


if __name__ == "__main__":
    run()
