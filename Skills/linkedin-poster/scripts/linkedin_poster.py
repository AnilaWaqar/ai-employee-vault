"""
LinkedIn Auto-Poster — Silver Tier Feature 3
Approved/ folder watch karo. File mile toh Playwright se LinkedIn pe post karo.
Kabhi bhi bina approval ke post nahi karta.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parents[3] / ".env")

VAULT_PATH        = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))
DRY_RUN           = os.getenv("DRY_RUN", "false").lower() == "true"
MAX_PER_HOUR      = int(os.getenv("MAX_ACTIONS_PER_HOUR", 20))
WATCH_INTERVAL    = 30  # seconds

APPROVED_DIR      = VAULT_PATH / "Approved"
PENDING_DIR       = VAULT_PATH / "Pending_Approval"
DONE_DIR          = VAULT_PATH / "Done"
REJECTED_DIR      = VAULT_PATH / "Rejected"
LOGS_DIR          = VAULT_PATH / "Logs"
SESSION_DIR       = VAULT_PATH / "linkedin_session"

# ── Logging ───────────────────────────────────────────────────────────────────
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "linkedin_poster.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("linkedin-poster")


# ── Rate Limiter ──────────────────────────────────────────────────────────────
class RateLimiter:
    def __init__(self, max_per_hour: int):
        self.max_per_hour = max_per_hour
        self.timestamps: deque = deque()

    def can_proceed(self) -> bool:
        now = datetime.now()
        cutoff = now - timedelta(hours=1)
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()
        return len(self.timestamps) < self.max_per_hour

    def record(self):
        self.timestamps.append(datetime.now())


# ── File Parser ───────────────────────────────────────────────────────────────
def parse_approval_file(filepath: Path) -> dict | None:
    """Approval file se content extract karo."""
    try:
        text = filepath.read_text(encoding="utf-8")

        # type check — sirf linkedin_post handle karo
        if "action: linkedin_post" not in text:
            return None

        # Post content extract karo
        content = ""
        if "## Post Content" in text:
            parts = text.split("## Post Content")
            if len(parts) > 1:
                # Next section tak content lo
                raw = parts[1].strip()
                # "## To APPROVE" ya next heading tak kato
                for stop in ["## To APPROVE", "## To REJECT", "## Notes"]:
                    if stop in raw:
                        raw = raw.split(stop)[0]
                content = raw.strip()

        if not content:
            log.warning(f"Post content nahi mila: {filepath.name}")
            return None

        return {
            "filename": filepath.name,
            "filepath": filepath,
            "content":  content,
        }

    except Exception as e:
        log.error(f"File parse error {filepath.name}: {e}")
        return None


# ── LinkedIn Poster ───────────────────────────────────────────────────────────
def post_to_linkedin(page, content: str) -> bool:
    """Playwright se LinkedIn pe post karo."""
    try:
        log.info("LinkedIn feed khol raha hai...")
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_timeout(2000)

        # Post box click karo — multiple selectors try karo
        post_btn_selectors = [
            'button:has-text("Start a post")',
            'div:has-text("Start a post") >> nth=0',
            '[aria-label="Start a post"]',
            '[aria-label*="Start a post"]',
            '.share-box-feed-entry__trigger',
            'div[class*="share-box-feed-entry__trigger"]',
            'div[class*="share-creation-state__placeholder"]',
            'span:has-text("Start a post")',
        ]

        clicked = False
        for sel in post_btn_selectors:
            try:
                btn = page.wait_for_selector(sel, timeout=5000)
                if btn:
                    btn.click()
                    log.info(f"Post button clicked: {sel}")
                    clicked = True
                    break
            except PWTimeout:
                continue

        if not clicked:
            log.error("Post button nahi mila LinkedIn pe.")
            return False

        page.wait_for_timeout(2000)

        # Text editor mein content type karo
        editor_selectors = [
            'div[aria-label*="Text editor for creating content"]',
            'div[aria-label*="text editor" i]',
            'div[data-placeholder*="What do you want to talk about"]',
            'div[data-placeholder*="post" i]',
            'div.ql-editor',
            'div[role="textbox"]',
            'div[contenteditable="true"]',
        ]

        typed = False
        for sel in editor_selectors:
            try:
                editor = page.wait_for_selector(sel, timeout=5000)
                if editor:
                    editor.click()
                    editor.fill(content)
                    log.info(f"Content typed in editor: {sel}")
                    typed = True
                    break
            except PWTimeout:
                continue

        if not typed:
            log.error("Text editor nahi mila LinkedIn pe.")
            return False

        page.wait_for_timeout(1500)

        if DRY_RUN:
            log.info(f"[DRY_RUN] Post likhna tha: {content[:80]}...")
            # Modal band karo
            try:
                page.keyboard.press("Escape")
            except Exception:
                pass
            return True

        # Post button click karo
        submit_selectors = [
            'button[aria-label="Post"]',
            'button.share-actions__primary-action',
            'button[data-control-name="share.post"]',
            'button.artdeco-button--primary',
        ]

        posted = False
        for sel in submit_selectors:
            try:
                submit_btn = page.wait_for_selector(sel, timeout=5000)
                if submit_btn and submit_btn.is_enabled():
                    submit_btn.click()
                    log.info(f"Post submit clicked: {sel}")
                    posted = True
                    break
            except PWTimeout:
                continue

        if not posted:
            log.error("Submit button nahi mila.")
            return False

        page.wait_for_timeout(3000)
        log.info("Post successfully published!")
        return True

    except Exception as e:
        log.error(f"LinkedIn posting error: {e}", exc_info=True)
        return False


# ── Archive File ──────────────────────────────────────────────────────────────
def archive_file(filepath: Path, success: bool):
    """Post ke baad file Done/ mein move karo."""
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    status = "SENT" if success else "FAILED"
    dest = DONE_DIR / f"{status}_{filepath.name}"
    try:
        filepath.rename(dest)
        log.info(f"Archived: {dest.name}")
    except Exception as e:
        log.error(f"Archive error: {e}")


# ── Audit Log ─────────────────────────────────────────────────────────────────
def audit_log(filename: str, content_preview: str, result: str):
    import json
    date = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"{date}.md"
    entry = (
        f"\n### {datetime.now().strftime('%H:%M:%S')} - LinkedIn Post\n"
        f"- File: `{filename}`\n"
        f"- Preview: {content_preview[:80]}...\n"
        f"- DRY_RUN: {DRY_RUN}\n"
        f"- Result: **{result}**\n"
    )
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)


# ── Main Loop ─────────────────────────────────────────────────────────────────
def run():
    rate_limiter = RateLimiter(MAX_PER_HOUR)

    log.info("=" * 60)
    log.info("LinkedIn Auto-Poster started")
    log.info(f"Vault: {VAULT_PATH}")
    log.info(f"DRY_RUN: {DRY_RUN}")
    log.info(f"Watch interval: {WATCH_INTERVAL}s")
    log.info(f"Max posts/hour: {MAX_PER_HOUR}")
    log.info("=" * 60)

    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            args=["--no-sandbox"],
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        log.info("Browser launched. LinkedIn khul raha hai...")
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30_000)

        # Login check
        log.info("Agar pehli baar hai toh LinkedIn login karo...")
        page.wait_for_timeout(3000)

        logged_in = False

        # Primary check: URL-based (most reliable — /feed/ = logged in, /login or /authwall = not)
        current_url = page.url
        if "feed" in current_url and "login" not in current_url and "authwall" not in current_url:
            logged_in = True
            log.info(f"LinkedIn logged in (URL check: {current_url})")

        # Fallback: selector-based check
        if not logged_in:
            login_selectors = [
                'nav.global-nav',                              # Global nav bar (always present)
                '.global-nav__me',                            # "Me" button in nav
                'input.search-global-typeahead__input',       # Search bar
                'div[data-view-name="feed-identity-module"]', # Profile module (new UI)
                'div[class*="share-box"]',                    # Post box (any variant)
                'button[aria-label*="post"]',                 # Post button (case-insensitive partial)
                '.scaffold-layout__main',                     # Main feed layout
                'div.feed-identity-module',                   # Old selector
            ]
            for sel in login_selectors:
                try:
                    page.wait_for_selector(sel, timeout=10_000)
                    logged_in = True
                    log.info(f"LinkedIn logged in. (selector: {sel})")
                    break
                except PWTimeout:
                    continue

        if not logged_in:
            log.error("Login timeout. LinkedIn login nahi hua. Script band ho rahi hai.")
            browser.close()
            return

        log.info(f"Approved/ folder watch kar raha hai har {WATCH_INTERVAL}s...")

        # Watch loop
        while True:
            try:
                linkedin_files = sorted(
                    APPROVED_DIR.glob("LINKEDIN_*.md"),
                    key=lambda f: f.stat().st_mtime
                )

                if not linkedin_files:
                    log.info("Koi approved LinkedIn post nahi. Next check in 30s...")
                else:
                    for filepath in linkedin_files:
                        if not rate_limiter.can_proceed():
                            log.warning(f"Rate limit reached ({MAX_PER_HOUR}/hr). Skip.")
                            break

                        post_data = parse_approval_file(filepath)
                        if not post_data:
                            log.warning(f"Skip (invalid/non-linkedin file): {filepath.name}")
                            continue

                        log.info(f"Processing: {filepath.name}")
                        log.info(f"Content preview: {post_data['content'][:80]}...")

                        success = post_to_linkedin(page, post_data["content"])
                        rate_limiter.record()
                        archive_file(filepath, success)
                        audit_log(
                            filepath.name,
                            post_data["content"],
                            "posted" if success else "failed"
                        )

            except Exception as e:
                log.error(f"Watch loop error: {e}", exc_info=True)

            time.sleep(WATCH_INTERVAL)


if __name__ == "__main__":
    run()
