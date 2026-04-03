"""
HITL Orchestrator — Silver Tier Feature 4
Approved/ aur Rejected/ folders watch karo.
File type dekho, sahi action lo, Done/ mein archive karo.
Pending_Approval/ mein 24h se purani files expire karo.
"""

import os
import re
import sys
import time
import base64
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText

from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parent / ".env")

VAULT_PATH      = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))
DRY_RUN         = os.getenv("DRY_RUN", "false").lower() == "true"
WATCH_INTERVAL  = 30   # seconds
EXPIRE_HOURS    = 24

APPROVED_DIR    = VAULT_PATH / "Approved"
REJECTED_DIR    = VAULT_PATH / "Rejected"
PENDING_DIR     = VAULT_PATH / "Pending_Approval"
DONE_DIR        = VAULT_PATH / "Done"
LOGS_DIR        = VAULT_PATH / "Logs"
DASHBOARD       = VAULT_PATH / "Dashboard.md"
TOKEN_FILE      = VAULT_PATH / "Skills/gmail-watcher/assets/token.json"
SIGNALS_DIR     = VAULT_PATH / "Signals"
SIGNALS_ACK_DIR = VAULT_PATH / "Signals" / "Acknowledged"

# Files handled by other scripts — orchestrator skip karega
SKIP_PREFIXES = ("LINKEDIN_", "DRAFT_", "SENT_", "FAILED_")

# ── Logging ───────────────────────────────────────────────────────────────────
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "orchestrator.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("orchestrator")


# ── Frontmatter Parser ────────────────────────────────────────────────────────
def parse_frontmatter(filepath: Path) -> dict:
    """YAML frontmatter (--- block) se key-value pairs extract karo."""
    meta = {}
    try:
        text = filepath.read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.find("---", 3)
            if end != -1:
                block = text[3:end].strip()
                for line in block.splitlines():
                    if ":" in line:
                        k, _, v = line.partition(":")
                        meta[k.strip().lower()] = v.strip()
    except Exception as e:
        log.warning(f"Frontmatter parse error ({filepath.name}): {e}")
    return meta


# ── Gmail Email Sender ────────────────────────────────────────────────────────
def send_email_gmail(to: str, subject: str, body: str) -> str | None:
    """Gmail API se email bhejo. Message ID return karo."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        service = build("gmail", "v1", credentials=creds)
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        return result.get("id")

    except Exception as e:
        log.error(f"Gmail send error: {e}")
        return None


# ── Body Extractor ────────────────────────────────────────────────────────────
def extract_email_fields(filepath: Path) -> tuple[str, str, str]:
    """Approval file se To, Subject, Body nikaalo."""
    text = filepath.read_text(encoding="utf-8")

    to_match      = re.search(r'\*\*To:\*\*\s*(.+)', text)
    subject_match = re.search(r'\*\*Subject:\*\*\s*(.+)', text)
    body_match    = re.search(r'---\n\n(.*?)\n\n---', text, re.DOTALL)

    to      = to_match.group(1).strip()      if to_match      else ""
    subject = subject_match.group(1).strip() if subject_match else "(No Subject)"
    body    = body_match.group(1).strip()    if body_match    else ""

    # Review notes remove karo
    body = re.sub(r'>\s?\*\*Review Note.*', '', body, flags=re.DOTALL).strip()

    return to, subject, body


# ── Archive Helper ─────────────────────────────────────────────────────────────
def archive(filepath: Path, prefix: str):
    """File Done/ mein prefix ke saath move karo."""
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    dest = DONE_DIR / f"{prefix}_{filepath.name}"
    try:
        shutil.move(str(filepath), str(dest))
        log.info(f"Archived → Done/{dest.name}")
    except Exception as e:
        log.error(f"Archive failed ({filepath.name}): {e}")


# ── Audit Log ─────────────────────────────────────────────────────────────────
def audit(action: str, filename: str, result: str, detail: str = ""):
    date = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"{date}.md"
    entry = (
        f"\n### {datetime.now().strftime('%H:%M:%S')} - Orchestrator: {action}\n"
        f"- File: `{filename}`\n"
        f"- Result: **{result}**\n"
    )
    if detail:
        entry += f"- Detail: {detail}\n"
    entry += f"- DRY_RUN: {DRY_RUN}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)


# ── Dashboard Updater ─────────────────────────────────────────────────────────
def update_dashboard():
    """Dashboard.md mein folder counts update karo."""
    try:
        counts = {
            "Needs_Action":    len(list((VAULT_PATH / "Needs_Action").glob("*.md"))),
            "Drafts":          len(list((VAULT_PATH / "Drafts").glob("*.md"))),
            "Pending_Approval":len(list(PENDING_DIR.glob("*.md"))),
            "Approved":        len(list(APPROVED_DIR.glob("*.md"))),
            "Done":            len(list(DONE_DIR.glob("*.md"))),
            "Rejected":        len(list(REJECTED_DIR.glob("*.md"))),
        }
        if not DASHBOARD.exists():
            return
        text = DASHBOARD.read_text(encoding="utf-8")
        for folder, count in counts.items():
            text = re.sub(
                rf'(\*\*{folder}\*\*.*?)\d+',
                lambda m, c=count: m.group(0)[:-len(str(int(m.group(0).split()[-1])))] + str(c),
                text
            )
        DASHBOARD.write_text(text, encoding="utf-8")
        log.info("Dashboard.md updated.")
    except Exception as e:
        log.warning(f"Dashboard update failed: {e}")


# ── Signals Reader ────────────────────────────────────────────────────────────
def read_signals():
    """Cloud Agent ke signals /Signals/ se padho aur respond karo."""
    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
    SIGNALS_ACK_DIR.mkdir(parents=True, exist_ok=True)

    for signal_file in SIGNALS_DIR.glob("*.md"):
        try:
            content = signal_file.read_text(encoding="utf-8")
            name = signal_file.name

            if "CLOUD_DOWN" in name:
                log.warning("SIGNAL: Cloud Agent offline detected!")
                audit("signal", name, "alert", "Cloud Agent DOWN")
            elif "APPROVAL_EXPIRED" in name:
                log.warning(f"SIGNAL: Approval expired — {name}")
                audit("signal", name, "alert", "Approval expired")
            elif "SYNC_CONFLICT" in name:
                log.warning("SIGNAL: Git sync conflict — manual resolution needed!")
                audit("signal", name, "alert", "Git conflict detected")
            elif "TASK_FAILED" in name:
                log.warning(f"SIGNAL: Task failed — {name}")
                audit("signal", name, "alert", "Task failed on cloud")
            elif "HEALTH_CHECK" in name:
                log.info(f"SIGNAL: Cloud Agent alive — {name}")
                audit("signal", name, "ok", "Health check received")
            else:
                log.info(f"SIGNAL: Unknown signal — {name}")

            # Signal acknowledge karo
            dest = SIGNALS_ACK_DIR / signal_file.name
            shutil.move(str(signal_file), str(dest))

        except Exception as e:
            log.error(f"Signal read error ({signal_file.name}): {e}")


# ── Process Approved/ ─────────────────────────────────────────────────────────
def process_approved():
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    files = [f for f in APPROVED_DIR.glob("*.md")]
    if not files:
        return

    log.info(f"Approved/ mein {len(files)} file(s) mili.")

    for filepath in files:
        name = filepath.name

        # Skip — other scripts handle these
        if any(name.startswith(p) for p in SKIP_PREFIXES):
            log.info(f"Skip (handled by other script): {name}")
            continue

        meta = parse_frontmatter(filepath)
        action = meta.get("action", "")
        ftype  = meta.get("type", "")

        log.info(f"Processing: {name} | action={action} | type={ftype}")

        # ── send_email action ──────────────────────────────────────────────
        if action == "send_email":
            to, subject, body = extract_email_fields(filepath)
            if not to or not body:
                log.error(f"Email fields missing in {name} — moving to Done/FAILED_*")
                archive(filepath, "FAILED")
                audit("send_email", name, "failed", "Missing To/Body fields")
                continue

            if DRY_RUN:
                log.info(f"[DRY_RUN] Would send email to: {to} | Subject: {subject}")
                archive(filepath, "DRYRUN")
                audit("send_email", name, "dry_run", f"To: {to}")
            else:
                msg_id = send_email_gmail(to, subject, body)
                if msg_id:
                    log.info(f"Email sent! ID: {msg_id} | To: {to}")
                    archive(filepath, "SENT")
                    audit("send_email", name, "sent", f"To: {to} | MsgID: {msg_id}")
                else:
                    log.error(f"Email send failed: {name}")
                    archive(filepath, "FAILED")
                    audit("send_email", name, "failed", f"To: {to}")

        # ── linkedin_post action — skip (linkedin_poster.py handles it) ───
        elif action == "linkedin_post":
            log.info(f"Skip linkedin_post — linkedin_poster.py handles it: {name}")

        # ── whatsapp_reply action — log only (no auto-reply) ──────────────
        elif action == "whatsapp_reply":
            log.info(f"WhatsApp reply approved — manual send required: {name}")
            archive(filepath, "WHATSAPP_REVIEWED")
            audit("whatsapp_reply", name, "acknowledged", "Human must reply manually")

        # ── APPROVAL_REQUIRED emails — human reviewed ─────────────────────
        elif name.startswith("APPROVAL_REQUIRED_"):
            log.info(f"Approval reviewed by human: {name}")
            archive(filepath, "REVIEWED")
            audit("approval_reviewed", name, "reviewed", f"type: {ftype}")

        # ── WHATSAPP_URGENT — human acknowledged ──────────────────────────
        elif name.startswith("WHATSAPP_"):
            log.info(f"WhatsApp alert acknowledged: {name}")
            archive(filepath, "WHATSAPP_REVIEWED")
            audit("whatsapp_urgent", name, "acknowledged")

        # ── Unknown file — archive as reviewed ────────────────────────────
        else:
            log.warning(f"Unknown file type in Approved/: {name} — archiving as REVIEWED")
            archive(filepath, "REVIEWED")
            audit("unknown", name, "reviewed")


# ── Process Rejected/ ─────────────────────────────────────────────────────────
def process_rejected():
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)
    files = list(REJECTED_DIR.glob("*.md"))
    if not files:
        return

    log.info(f"Rejected/ mein {len(files)} file(s) mili.")
    for filepath in files:
        log.info(f"Rejected: {filepath.name}")
        archive(filepath, "REJECTED")
        audit("rejected", filepath.name, "rejected", "Human moved to Rejected/")


# ── Expire Pending_Approval/ ──────────────────────────────────────────────────
def expire_pending():
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now() - timedelta(hours=EXPIRE_HOURS)
    files = list(PENDING_DIR.glob("*.md"))

    for filepath in files:
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
        if mtime < cutoff:
            age_hours = (datetime.now() - mtime).seconds // 3600
            log.warning(f"Expired ({age_hours}h old): {filepath.name}")
            archive(filepath, "EXPIRED")
            audit("expired", filepath.name, "expired", f"Age: {age_hours}h > {EXPIRE_HOURS}h limit")


# ── Main Loop ─────────────────────────────────────────────────────────────────
def run():
    log.info("=" * 60)
    log.info("HITL Orchestrator started")
    log.info(f"Vault:    {VAULT_PATH}")
    log.info(f"DRY_RUN:  {DRY_RUN}")
    log.info(f"Interval: {WATCH_INTERVAL}s | Expiry: {EXPIRE_HOURS}h")
    log.info("=" * 60)

    DONE_DIR.mkdir(parents=True, exist_ok=True)
    cycle = 0

    while True:
        cycle += 1
        log.info(f"--- Cycle {cycle} ---")
        try:
            read_signals()
            process_approved()
            process_rejected()
            # Expiry check har 10th cycle pe (every ~5 min)
            if cycle % 10 == 0:
                expire_pending()
            update_dashboard()
        except Exception as e:
            log.error(f"Cycle error: {e}", exc_info=True)

        log.info(f"Next check in {WATCH_INTERVAL}s...")
        time.sleep(WATCH_INTERVAL)


if __name__ == "__main__":
    run()
