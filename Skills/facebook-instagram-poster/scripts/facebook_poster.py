"""
Facebook Auto-Poster — Playwright Browser Automation
Vault: E:/HC/AI_Employee_Vault
Tier: Gold — Feature 2
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# --- Config ---
VAULT = Path("E:/HC/AI_Employee_Vault")
load_dotenv(VAULT / ".env")

FB_EMAIL    = os.getenv("FB_EMAIL", "")
FB_PASSWORD = os.getenv("FB_PASSWORD", "")
FB_PAGE_URL = os.getenv("FB_PAGE_URL", "https://www.facebook.com")
DRY_RUN     = os.getenv("DRY_RUN", "false").lower() == "true"
SESSION_DIR = str(VAULT / "facebook_session")

LOG_FILE = VAULT / "Logs" / "facebook_poster.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [FB] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


def log_action(action: str, target: str, result: str, content: str = ""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action,
        "actor": "facebook-poster",
        "target": target,
        "result": result,
        "content_preview": content[:100] if content else "",
        "dry_run": DRY_RUN
    }
    audit_log = VAULT / "Logs" / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    logs = []
    if audit_log.exists():
        try:
            logs = json.loads(audit_log.read_text(encoding="utf-8"))
        except:
            logs = []
    logs.append(entry)
    audit_log.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding="utf-8")


def post_to_facebook(post_content: str):
    """Facebook pe post karo Playwright se"""

    if not FB_EMAIL or not FB_PASSWORD:
        log.error("FB_EMAIL ya FB_PASSWORD .env mein nahi hai!")
        return False

    if DRY_RUN:
        log.info(f"[DRY RUN] Facebook pe post hoti: {post_content[:80]}...")
        log_action("facebook_post", FB_PAGE_URL, "dry_run", post_content)
        return True

    with sync_playwright() as p:
        log.info("Browser launch ho raha hai...")
        browser = p.chromium.launch_persistent_context(
            SESSION_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            # --- Login check ---
            log.info("Facebook khul raha hai...")
            page.goto("https://www.facebook.com", timeout=30000)
            page.wait_for_timeout(3000)

            # Agar login page aaye toh login karo
            if "login" in page.url or page.locator('[name="email"]').count() > 0:
                log.info("Login kar raha hai...")
                page.fill('[name="email"]', FB_EMAIL)
                page.fill('[name="pass"]', FB_PASSWORD)
                # Try multiple login button selectors
                login_selectors = [
                    '[data-testid="royal_login_button"]',
                    'button[type="submit"]',
                    'input[type="submit"]',
                    '[name="login"]',
                ]
                for sel in login_selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn.count() > 0:
                            btn.click()
                            log.info(f"Login button clicked: {sel}")
                            break
                    except:
                        continue
                page.wait_for_timeout(5000)

            # --- 2FA Check ---
            if "two_step_verification" in page.url or "two_factor" in page.url:
                log.info("2FA detect hua — browser mein 90 seconds mein code enter karo!")
                # Browser window mein message dikhao
                try:
                    page.evaluate("document.title = '>>> ENTER 2FA CODE NOW <<<'")
                except:
                    pass
                # Wait for URL to leave 2FA page (user enters code manually)
                try:
                    page.wait_for_url(
                        lambda url: "two_step" not in url and "two_factor" not in url,
                        timeout=90000
                    )
                    log.info("2FA complete ho gaya!")
                except:
                    log.warning("2FA timeout — 90 seconds mein code enter nahi hua")
                page.wait_for_timeout(3000)

            log.info("Login ho gaya")

            # --- Page pe jao ---
            log.info(f"Page pe ja raha hai: {FB_PAGE_URL}")
            page.goto(FB_PAGE_URL, timeout=30000)
            page.wait_for_timeout(3000)

            # --- Post box click karo ---
            log.info("Post box dhund raha hai...")
            post_box_selectors = [
                '[aria-label="Create a post"]',
                '[aria-label="What\'s on your mind"]',
                'div[role="button"]:has-text("What\'s on your mind")',
                'div[role="button"]:has-text("Write something")',
            ]
            clicked = False
            for selector in post_box_selectors:
                try:
                    el = page.locator(selector).first
                    if el.count() > 0:
                        el.click()
                        clicked = True
                        log.info(f"Post box mila: {selector}")
                        break
                except:
                    continue

            if not clicked:
                log.error("Post box nahi mila — Facebook UI change ho gai hai")
                log_action("facebook_post", FB_PAGE_URL, "failed_no_postbox", post_content)
                return False

            page.wait_for_timeout(2000)

            # --- Content type karo ---
            log.info("Content type kar raha hai...")
            page.keyboard.type(post_content, delay=30)
            page.wait_for_timeout(2000)

            # Hashtag autocomplete dismiss karo (Escape press)
            page.keyboard.press("Escape")
            page.wait_for_timeout(1500)

            page.screenshot(path=str(VAULT / "Logs" / "fb_before_post.png"))

            # --- Step 1: Next button (agar ho) ---
            try:
                next_btn = page.get_by_role("button", name="Next")
                if next_btn.count() > 0 and next_btn.is_visible():
                    next_btn.click()
                    log.info("Next button click ho gaya")
                    page.wait_for_timeout(3000)
                    page.screenshot(path=str(VAULT / "Logs" / "fb_after_next.png"))
            except Exception as e:
                log.debug(f"Next btn: {e}")
                # Fallback: text match
                try:
                    page.locator("text=Next").last.click()
                    log.info("Next (text) click ho gaya")
                    page.wait_for_timeout(3000)
                except:
                    pass

            # --- Step 2: Post / Share button ---
            posted = False
            post_texts = ["Post", "Share now", "Share", "Publish"]
            for txt in post_texts:
                try:
                    btn = page.get_by_role("button", name=txt)
                    if btn.count() > 0 and btn.is_visible():
                        btn.click()
                        posted = True
                        log.info(f"Post button click: '{txt}'")
                        break
                except:
                    pass
                try:
                    btn = page.locator(f"text={txt}").last
                    if btn.count() > 0 and btn.is_visible():
                        btn.click()
                        posted = True
                        log.info(f"Post (text) click: '{txt}'")
                        break
                except:
                    pass

            if not posted:
                page.screenshot(path=str(VAULT / "Logs" / "fb_post_debug.png"))
                log.error("Post button nahi mila")
                log_action("facebook_post", FB_PAGE_URL, "failed_no_postbtn", post_content)
                return False

            page.wait_for_timeout(4000)
            log.info("Post successfully publish ho gaya!")
            log_action("facebook_post", FB_PAGE_URL, "success", post_content)
            # Screenshot lo aur page reload karo
            screenshot_path = str(VAULT / "Logs" / "fb_after_post.png")
            page.screenshot(path=screenshot_path)
            log.info(f"Screenshot saved: {screenshot_path}")
            # Page pe wapis jao aur 30 sec hold karo taake user dekh sake
            page.goto(FB_PAGE_URL, timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=str(VAULT / "Logs" / "fb_page_after.png"))
            log.info("60 seconds hold — browser band hone se pehle post check kar lo...")
            page.wait_for_timeout(60000)
            return True

        except PlaywrightTimeout as e:
            log.error(f"Timeout error: {e}")
            log_action("facebook_post", FB_PAGE_URL, f"timeout: {str(e)}", post_content)
            return False
        except Exception as e:
            log.error(f"Error: {e}")
            log_action("facebook_post", FB_PAGE_URL, f"error: {str(e)}", post_content)
            return False
        finally:
            browser.close()


def process_approved_file(filepath: Path):
    """Approved/ folder se Facebook post file process karo"""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    post_content = ""
    in_content = False
    for line in lines:
        if line.strip() == "## Post Content":
            in_content = True
            continue
        if in_content and line.startswith("## "):
            break
        if in_content:
            post_content += line + "\n"

    post_content = post_content.strip()
    if not post_content:
        log.error(f"Post content nahi mili file mein: {filepath.name}")
        return False

    log.info(f"Posting from: {filepath.name}")
    success = post_to_facebook(post_content)

    done_dir = VAULT / "Done"
    prefix = "SENT" if success else "FAILED"
    dest = done_dir / f"{prefix}_{filepath.name}"
    filepath.rename(dest)
    log.info(f"File moved to Done/: {dest.name}")
    return success


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python facebook_poster.py <approved_file_path>")
        print("       python facebook_poster.py --test")
        sys.exit(1)

    if sys.argv[1] == "--test":
        test_content = "🤖 AI Employee test post — Gold Tier Feature 2 working! #AIEmployee #Automation"
        log.info("Test mode — directly posting...")
        success = post_to_facebook(test_content)
        print("SUCCESS!" if success else "FAILED!")
    else:
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"File nahi mili: {filepath}")
            sys.exit(1)
        process_approved_file(filepath)
