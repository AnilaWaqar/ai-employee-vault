"""
Plan Creator — Silver Tier Feature 5
Needs_Action/ folder watch karo. Naya file mile toh:
1. Sensitivity check karo (Company_Handbook rules)
2. Plans/PLAN_*.md banao with checkboxes
3. Sensitive files → Pending_Approval/ mein bhi flag karo
4. Dashboard update karo
"""

import os
import json
import time
import re
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parents[3] / ".env")

VAULT_PATH      = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))
DRY_RUN         = os.getenv("DRY_RUN", "false").lower() == "true"
WATCH_INTERVAL  = 60   # seconds

NEEDS_ACTION_DIR = VAULT_PATH / "Needs_Action"
PLANS_DIR        = VAULT_PATH / "Plans"
PENDING_DIR      = VAULT_PATH / "Pending_Approval"
LOGS_DIR         = VAULT_PATH / "Logs"
DASHBOARD        = VAULT_PATH / "Dashboard.md"
PROCESSED_FILE   = Path(__file__).parent.parent / "assets" / "processed_plans.json"

# ── Sensitive & Priority Keywords (from Company_Handbook.md) ──────────────────
SENSITIVE_KEYWORDS = [
    "legal", "lawsuit", "complaint", "violation", "termination",
    "confidential", "password reset", "security alert", "otp",
    "hacked", "breach", "fraud", "harassment", "personal emergency",
    "security", "account compromise", "disciplinary",
]

HIGH_PRIORITY_KEYWORDS = [
    "urgent", "asap", "deadline", "critical", "emergency", "important",
]

# ── Logging ───────────────────────────────────────────────────────────────────
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "plan_creator.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("plan-creator")


# ── Processed IDs ─────────────────────────────────────────────────────────────
def load_processed() -> set:
    try:
        if PROCESSED_FILE.exists():
            return set(json.loads(PROCESSED_FILE.read_text(encoding="utf-8")))
    except Exception:
        pass
    return set()


def save_processed(ids: set):
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.write_text(json.dumps(sorted(ids), indent=2), encoding="utf-8")


# ── Frontmatter Parser ────────────────────────────────────────────────────────
def parse_frontmatter(filepath: Path) -> dict:
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
        meta["_raw"] = text
    except Exception as e:
        log.warning(f"Frontmatter parse error ({filepath.name}): {e}")
    return meta


# ── Detectors ─────────────────────────────────────────────────────────────────
def detect_task_type(filename: str) -> str:
    if filename.startswith("EMAIL_"):
        return "email"
    elif filename.startswith("WHATSAPP_"):
        return "whatsapp"
    else:
        return "file_drop"


def detect_sensitivity(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in SENSITIVE_KEYWORDS if kw in text_lower]


def detect_priority(meta: dict, text: str) -> str:
    p = meta.get("priority", "").lower()
    if p in ("high", "urgent"):
        return "high"
    kws = meta.get("keywords_found", "")
    for kw in HIGH_PRIORITY_KEYWORDS:
        if kw in kws.lower() or kw in text.lower():
            return "high"
    return "normal"


# ── Plan Creator ──────────────────────────────────────────────────────────────
def create_plan(filepath: Path, meta: dict, task_type: str,
                priority: str, sensitive_kws: list) -> tuple[Path, str]:

    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_name = f"PLAN_{ts}_{filepath.stem}.md"
    plan_path = PLANS_DIR / plan_name

    from_field = meta.get("from", meta.get("sender", "Unknown"))
    subject    = meta.get("subject", meta.get("from", filepath.name))
    approval   = "YES" if sensitive_kws else "NO"
    reason     = (f"Sensitive keywords found: `{', '.join(sensitive_kws)}`"
                  if sensitive_kws else "Safe to process — no sensitive content detected")

    if task_type == "email":
        steps = (
            "- [x] Email file detected in Needs_Action/\n"
            "- [x] Sensitivity check performed\n"
            "- [x] Plan created automatically\n"
            "- [ ] Draft response created → Drafts/\n"
            "- [ ] Human review complete\n"
            "- [ ] Email sent → Done/"
        )
    elif task_type == "whatsapp":
        steps = (
            "- [x] WhatsApp message detected in Needs_Action/\n"
            "- [x] Sensitivity check performed\n"
            "- [x] Plan created automatically\n"
            "- [ ] Reply suggestion created → Drafts/\n"
            "- [ ] Human review complete\n"
            "- [ ] Human replied manually on WhatsApp"
        )
    else:
        steps = (
            "- [x] File detected in Needs_Action/\n"
            "- [x] Sensitivity check performed\n"
            "- [x] Plan created automatically\n"
            "- [ ] Action determined by human\n"
            "- [ ] Task completed → Done/"
        )

    content = f"""---
created: {datetime.now().isoformat()}
status: in_progress
triggered_by: {filepath.name}
task_type: {task_type}
priority: {priority}
approval_required: {approval.lower()}
skill_used: plan-creator
---

# Plan: {subject}

## Source
- **File:** `{filepath.name}`
- **Type:** {task_type}
- **From:** {from_field}
- **Priority:** {priority.upper()}

## Objective
Process `{filepath.name}` — {task_type} message from **{from_field}**.

## Steps
{steps}

## Approval Required
**{approval}** — {reason}

## Notes
- Plan auto-created by plan-creator at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- DRY_RUN: {DRY_RUN}
"""

    if not DRY_RUN:
        PLANS_DIR.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(content, encoding="utf-8")
        log.info(f"Plan created: {plan_name}")
    else:
        log.info(f"[DRY_RUN] Would create plan: {plan_name}")

    return plan_path, plan_name


# ── Approval Request Creator ───────────────────────────────────────────────────
def create_approval_request(filepath: Path, meta: dict,
                             sensitive_kws: list, plan_name: str):

    from_field = meta.get("from", meta.get("sender", "Unknown"))
    subject    = meta.get("subject", filepath.name)
    preview    = meta.get("_raw", "")[:300].replace("\n", " ").strip()
    dest       = PENDING_DIR / f"APPROVAL_REQUIRED_{filepath.name}"

    content = f"""---
type: APPROVAL_REQUIRED
triggered_by: {filepath.name}
task_type: {meta.get("type", "unknown")}
from: {from_field}
subject: {subject}
sensitive_keywords: {', '.join(sensitive_kws)}
plan_file: {plan_name}
flagged_at: {datetime.now().strftime("%Y-%m-%d")}
priority: HIGH
status: pending_review
---

# Sensitive Content — Human Review Required

**From:** {from_field}
**Subject/Context:** {subject}
**Flagged Keywords:** `{', '.join(sensitive_kws)}`
**Related Plan:** `Plans/{plan_name}`

## Content Preview
{preview}...

## Why Flagged
Sensitive keywords detected — this content requires manual human review
before any action is taken.

## Action Required
- [ ] Review original file: `Needs_Action/{filepath.name}`
- [ ] Decide on appropriate response
- [ ] Move this file to `/Done/` when resolved

**Move to `/Approved/` if orchestrator action is needed.**
**Move to `/Rejected/` to dismiss.**
"""

    if not DRY_RUN:
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        log.info(f"Approval request created: {dest.name}")
    else:
        log.info(f"[DRY_RUN] Would create approval request: {dest.name}")

    return dest


# ── Audit Log ─────────────────────────────────────────────────────────────────
def audit(filename: str, task_type: str, priority: str,
          plan_name: str, sensitive: list):
    date     = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"{date}.md"
    entry = (
        f"\n### {datetime.now().strftime('%H:%M:%S')} - Plan Created\n"
        f"- File: `{filename}`\n"
        f"- Type: {task_type} | Priority: {priority.upper()}\n"
        f"- Plan: `Plans/{plan_name}`\n"
        f"- Sensitive: {', '.join(sensitive) if sensitive else 'None'}\n"
        f"- DRY_RUN: {DRY_RUN}\n"
    )
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)


# ── Dashboard Update ──────────────────────────────────────────────────────────
def update_dashboard():
    try:
        if not DASHBOARD.exists():
            return
        counts = {
            "Needs_Action":     len(list(NEEDS_ACTION_DIR.glob("*.md"))),
            "Plans":            len(list(PLANS_DIR.glob("*.md"))),
            "Pending_Approval": len(list(PENDING_DIR.glob("*.md"))),
        }
        text = DASHBOARD.read_text(encoding="utf-8")
        for folder, count in counts.items():
            text = re.sub(
                rf'(\*\*{folder}\*\*.*?)\d+',
                lambda m, c=count: m.group(0)[:-len(str(int(m.group(0).split()[-1])))] + str(c),
                text
            )
        DASHBOARD.write_text(text, encoding="utf-8")
    except Exception as e:
        log.warning(f"Dashboard update failed: {e}")


# ── Main Loop ─────────────────────────────────────────────────────────────────
def run():
    log.info("=" * 60)
    log.info("Plan Creator started")
    log.info(f"Vault:    {VAULT_PATH}")
    log.info(f"DRY_RUN:  {DRY_RUN}")
    log.info(f"Interval: {WATCH_INTERVAL}s")
    log.info("=" * 60)

    NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)
    processed = load_processed()

    while True:
        files = list(NEEDS_ACTION_DIR.glob("*.md"))
        new_files = [f for f in files if f.name not in processed]

        if new_files:
            log.info(f"{len(new_files)} new file(s) in Needs_Action/")
        else:
            log.info(f"No new files. Next check in {WATCH_INTERVAL}s...")

        for filepath in new_files:
            try:
                log.info(f"Processing: {filepath.name}")
                meta        = parse_frontmatter(filepath)
                raw_text    = meta.get("_raw", filepath.name)
                task_type   = detect_task_type(filepath.name)
                sensitive   = detect_sensitivity(raw_text)
                priority    = detect_priority(meta, raw_text)

                log.info(f"  Type={task_type} | Priority={priority} | Sensitive={sensitive or 'None'}")

                # Create plan
                _, plan_name = create_plan(filepath, meta, task_type, priority, sensitive)

                # Create approval request if sensitive
                if sensitive:
                    create_approval_request(filepath, meta, sensitive, plan_name)
                    log.warning(f"  Flagged as sensitive → Pending_Approval/")

                # Audit log
                audit(filepath.name, task_type, priority, plan_name, sensitive)

                processed.add(filepath.name)
                save_processed(processed)

            except Exception as e:
                log.error(f"Error processing {filepath.name}: {e}", exc_info=True)

        update_dashboard()
        time.sleep(WATCH_INTERVAL)


if __name__ == "__main__":
    run()
