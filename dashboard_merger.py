"""
Dashboard Merger — Platinum Tier Phase 7
/Updates/ folder se Cloud Agent ki activity padho
aur Dashboard.md mein merge karo.
Har ghante run hota hai (PM2 cron ya Task Scheduler).
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

VAULT        = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))
UPDATES_DIR  = VAULT / "Updates"
PROCESSED    = VAULT / "Updates" / "processed"
DASHBOARD    = VAULT / "Dashboard.md"
LOGS_DIR     = VAULT / "Logs"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [MERGER] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "dashboard_merger.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("dashboard_merger")


def strip_frontmatter(content: str) -> str:
    """YAML frontmatter remove karo, sirf body return karo."""
    lines = content.split("\n")
    body_lines = []
    in_front = False
    dashes_seen = 0

    for line in lines:
        if line.strip() == "---":
            dashes_seen += 1
            in_front = dashes_seen < 2
            continue
        if not in_front:
            body_lines.append(line)

    return "\n".join(body_lines).strip()


def merge_updates():
    """Updates/ folder se cloud activity Dashboard.md mein merge karo."""
    UPDATES_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    update_files = sorted(UPDATES_DIR.glob("cloud_*.md"))
    if not update_files:
        log.info("Koi naya update nahi mila.")
        return

    if not DASHBOARD.exists():
        log.error("Dashboard.md nahi mila!")
        return

    new_entries = []
    for update_file in update_files:
        try:
            content = update_file.read_text(encoding="utf-8")
            body = strip_frontmatter(content)
            if body:
                timestamp = datetime.now().strftime("%H:%M")
                new_entries.append(f"- [{timestamp}] ☁️ Cloud: {body}")

            # Processed mein move karo
            shutil.move(str(update_file), str(PROCESSED / update_file.name))
            log.info(f"Processed: {update_file.name}")

        except Exception as e:
            log.error(f"Update read error ({update_file.name}): {e}")

    if not new_entries:
        log.info("Koi content nahi mila updates mein.")
        return

    # Dashboard mein merge karo
    current = DASHBOARD.read_text(encoding="utf-8")
    update_section = "\n".join(new_entries)
    marker = "## Cloud Agent Updates"

    if marker in current:
        updated = current.replace(
            marker,
            f"{marker}\n{update_section}"
        )
    else:
        updated = current + f"\n\n{marker}\n{update_section}\n"

    DASHBOARD.write_text(updated, encoding="utf-8")
    log.info(f"{len(new_entries)} update(s) Dashboard.md mein merge ho gayi.")


if __name__ == "__main__":
    log.info("Dashboard Merger started")
    merge_updates()
    log.info("Done.")
