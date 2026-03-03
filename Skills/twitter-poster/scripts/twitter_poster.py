"""
Twitter/X Auto-Poster — Playwright Browser Automation
Vault: E:/HC/AI_Employee_Vault
Tier: Gold — Feature 3
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# --- Config ---
VAULT = Path("E:/HC/AI_Employee_Vault")
load_dotenv(VAULT / ".env")

TWITTER_EMAIL    = os.getenv("TWITTER_EMAIL", "")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")
DRY_RUN          = os.getenv("DRY_RUN", "false").lower() == "true"
SESSION_DIR      = str(VAULT / "twitter_session")

LOG_FILE = VAULT / "Logs" / "twitter_poster.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [TWITTER] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

TWITTER_CHAR_LIMIT = 280


def log_action(action: str, result: str, content: str = ""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action,
        "actor": "twitter-poster",
        "target": "x.com",
        "result": result,
        "content_preview": content[:100] if content else "",
        "dry_run": DRY_RUN
    }
    audit_log = VAULT / "Logs" / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    logs = []
    if audit_log.exists():
        try:
            logs = json.loads(audit_log.read_text(encoding="utf-8"))
        except Exception:
            logs = []
    logs.append(entry)
    audit_log.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding="utf-8")


def post_tweet(tweet_text: str) -> bool:
    """Twitter/X pe tweet post karo Playwright se"""

    if len(tweet_text) > TWITTER_CHAR_LIMIT:
        log.error(f"Tweet too long: {len(tweet_text)} chars (max {TWITTER_CHAR_LIMIT})")
        return False

    if not TWITTER_EMAIL or not TWITTER_PASSWORD:
        log.error("TWITTER_EMAIL ya TWITTER_PASSWORD .env mein nahi hai!")
        return False

    if DRY_RUN:
        log.info(f"[DRY RUN] Tweet hoti: {tweet_text[:80]}...")
        log_action("tweet_post", "dry_run", tweet_text)
        return True

    with sync_playwright() as p:
        log.info("Browser launch ho raha hai...")
        browser = p.chromium.launch_persistent_context(
            SESSION_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            log.info("Twitter/X khul raha hai...")
            page.goto("https://x.com/home", timeout=30000)
            page.wait_for_timeout(4000)
            page.screenshot(path=str(VAULT / "Logs" / "tw_state.png"))

            # --- Login check ---
            is_logged_in = (
                page.locator('[data-testid="tweetTextarea_0"]').count() > 0 or
                page.locator('[data-testid="SideNav_NewTweet_Button"]').count() > 0 or
                page.locator('[aria-label="Post"]').count() > 0
            )

            if not is_logged_in:
                log.info("Login page detect hua — login kar raha hai...")
                page.goto("https://x.com/i/flow/login", timeout=30000)
                page.wait_for_timeout(3000)

                # Email/Username enter karo
                log.info("Email type kar raha hai...")
                email_selectors = [
                    'input[autocomplete="username"]',
                    'input[name="text"]',
                    'input[type="text"]',
                ]
                for sel in email_selectors:
                    try:
                        el = page.locator(sel).first
                        if el.count() > 0 and el.is_visible():
                            el.click()
                            el.type(TWITTER_EMAIL, delay=50)
                            log.info(f"Email typed via: {sel}")
                            break
                    except:
                        continue

                page.wait_for_timeout(1000)
                page.keyboard.press("Enter")
                page.wait_for_timeout(3000)
                page.screenshot(path=str(VAULT / "Logs" / "tw_after_email.png"))

                # Username verification (Twitter kabhi kabhi maangta hai)
                if page.locator('input[data-testid="ocfEnterTextTextInput"]').count() > 0:
                    log.info("Username verification maang raha hai...")
                    page.locator('input[data-testid="ocfEnterTextTextInput"]').type(
                        TWITTER_USERNAME or TWITTER_EMAIL.split("@")[0], delay=50
                    )
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(3000)

                # Check karo — email ke baad already home pe toh nahi aa gaye?
                page.wait_for_timeout(4000)
                log.info(f"After email URL: {page.url}")

                if "home" in page.url or "/x.com/" in page.url:
                    log.info("Google session se auto-login ho gaya!")
                else:
                    # Password field dhundo
                    log.info("Password type kar raha hai...")
                    try:
                        page.wait_for_selector('input[name="password"]', timeout=8000)
                        el = page.locator('input[name="password"]').first
                        el.click()
                        el.type(TWITTER_PASSWORD, delay=50)
                        log.info("Password typed")
                        page.wait_for_timeout(1000)
                        page.keyboard.press("Enter")
                        page.wait_for_timeout(5000)
                    except:
                        log.warning("Password field nahi mila — skip kar raha hai")

                page.screenshot(path=str(VAULT / "Logs" / "tw_after_login.png"))
                log.info(f"After login URL: {page.url}")

                # 2FA check
                if "challenge" in page.url or "verify" in page.url:
                    log.info("2FA detect hua — browser mein 90 seconds mein code enter karo!")
                    try:
                        page.wait_for_url(
                            lambda url: "challenge" not in url and "verify" not in url,
                            timeout=90000
                        )
                        log.info("2FA complete!")
                    except:
                        log.warning("2FA timeout")
                    page.wait_for_timeout(3000)

                log.info("Login ho gaya")
                page.goto("https://x.com/home", timeout=30000)
                page.wait_for_timeout(4000)

            # --- Directly compose page pe jao ---
            log.info("Compose page pe ja raha hai...")
            page.goto("https://x.com/compose/post", timeout=30000)
            page.wait_for_timeout(4000)
            page.screenshot(path=str(VAULT / "Logs" / "tw_compose.png"))
            log.info(f"Compose URL: {page.url}")

            compose_selectors = [
                '[data-testid="tweetTextarea_0"]',
                '[data-testid="tweetTextarea_0_label"]',
                '[aria-label="Post text"]',
                'div[role="textbox"][aria-multiline="true"]',
                'div[contenteditable="true"]',
            ]

            composed = False
            for sel in compose_selectors:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0:
                        el.wait_for(state="visible", timeout=5000)
                        el.click()
                        page.wait_for_timeout(1000)
                        el.type(tweet_text, delay=30)
                        composed = True
                        log.info(f"Tweet typed via: {sel}")
                        break
                except:
                    continue

            if not composed:
                page.screenshot(path=str(VAULT / "Logs" / "tw_compose_debug.png"))
                log.error("Tweet box nahi mila")
                log_action("tweet_post", "failed_no_composebox", tweet_text)
                page.wait_for_timeout(60000)
                return False

            page.wait_for_timeout(2000)
            page.screenshot(path=str(VAULT / "Logs" / "tw_before_post.png"))

            # --- Post button click ---
            posted = False
            post_selectors = [
                '[data-testid="tweetButton"]',
                '[data-testid="tweetButtonInline"]',
            ]
            for sel in post_selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.count() > 0 and btn.is_visible() and btn.is_enabled():
                        btn.click()
                        posted = True
                        log.info(f"Post button clicked: {sel}")
                        break
                except:
                    continue

            if not posted:
                page.screenshot(path=str(VAULT / "Logs" / "tw_postbtn_debug.png"))
                log.error("Post button nahi mila")
                log_action("tweet_post", "failed_no_postbtn", tweet_text)
                page.wait_for_timeout(60000)
                return False

            page.wait_for_timeout(5000)
            page.screenshot(path=str(VAULT / "Logs" / "tw_after_post.png"))
            log.info("Tweet successfully post ho gaya!")
            log_action("tweet_post", "success", tweet_text)
            log.info("60 seconds hold — tweet check kar lo browser band hone se pehle...")
            page.wait_for_timeout(60000)
            return True

        except PlaywrightTimeout as e:
            log.error(f"Timeout: {e}")
            log_action("tweet_post", f"timeout: {str(e)}", tweet_text)
            try:
                page.screenshot(path=str(VAULT / "Logs" / "tw_error.png"))
                page.wait_for_timeout(60000)
            except:
                pass
            return False
        except Exception as e:
            log.error(f"Error: {e}")
            log_action("tweet_post", f"error: {str(e)}", tweet_text)
            try:
                page.screenshot(path=str(VAULT / "Logs" / "tw_error.png"))
                page.wait_for_timeout(60000)
            except:
                pass
            return False
        finally:
            browser.close()


def process_approved_file(filepath: Path) -> bool:
    """Approved/ folder se Twitter post file process karo"""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    tweet_text = ""
    in_content = False
    for line in lines:
        if line.strip() == "## Tweet Content":
            in_content = True
            continue
        if in_content and line.startswith("## "):
            break
        if in_content:
            tweet_text += line + "\n"

    tweet_text = tweet_text.strip()
    if not tweet_text:
        log.error(f"Tweet content nahi mili: {filepath.name}")
        return False

    log.info(f"Processing: {filepath.name}")
    success = post_tweet(tweet_text)

    done_dir = VAULT / "Done"
    done_dir.mkdir(exist_ok=True)
    prefix = "SENT" if success else "FAILED"
    dest = done_dir / f"{prefix}_{filepath.name}"
    filepath.rename(dest)
    log.info(f"File moved: Done/{dest.name}")
    return success


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python twitter_poster.py --test")
        print("  python twitter_poster.py <approved_file_path>")
        sys.exit(1)

    if sys.argv[1] == "--test":
        test_tweet = f"AI Employee test tweet — Gold Tier Feature 3 working! #AIEmployee #Automation"
        log.info("Test mode...")
        success = post_tweet(test_tweet)
        print("SUCCESS!" if success else "FAILED!")
    else:
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"File nahi mili: {filepath}")
            sys.exit(1)
        ok = process_approved_file(filepath)
        sys.exit(0 if ok else 1)
