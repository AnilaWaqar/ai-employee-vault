"""
Instagram Auto-Poster — Playwright Browser Automation
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

IG_USERNAME = os.getenv("IG_USERNAME", "")
IG_PASSWORD = os.getenv("IG_PASSWORD", "")
DRY_RUN     = os.getenv("DRY_RUN", "false").lower() == "true"
SESSION_DIR = str(VAULT / "instagram_session")

LOG_FILE = VAULT / "Logs" / "instagram_poster.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [IG] %(message)s",
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
        "actor": "instagram-poster",
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


def post_to_instagram(caption: str, image_path: str = None):
    """Instagram pe post karo Playwright se"""

    if not IG_USERNAME or not IG_PASSWORD:
        log.error("IG_USERNAME ya IG_PASSWORD .env mein nahi hai!")
        return False

    if DRY_RUN:
        log.info(f"[DRY RUN] Instagram pe post hoti: {caption[:80]}...")
        log_action("instagram_post", "instagram.com", "dry_run", caption)
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
            # --- Login check ---
            log.info("Instagram khul raha hai...")
            page.goto("https://www.instagram.com", timeout=30000)
            page.wait_for_timeout(4000)

            # Screenshot lo current state dekho
            page.screenshot(path=str(VAULT / "Logs" / "ig_state.png"))
            log.info(f"Current URL: {page.url}")

            # Login check — agar home feed nahi dikh raha toh login karo
            is_logged_in = page.locator('[aria-label="New post"]').count() > 0 or \
                           page.locator('[aria-label="Home"]').count() > 0
            if not is_logged_in:
                log.info("Login kar raha hai...")
                # Username — click karo phir type karo
                try:
                    username_inp = page.locator('input').first
                    username_inp.click()
                    page.wait_for_timeout(500)
                    username_inp.fill("")
                    username_inp.type(IG_USERNAME, delay=50)
                    log.info(f"Username typed: {IG_USERNAME}")
                except Exception as e:
                    log.error(f"Username fill failed: {e}")
                page.wait_for_timeout(800)
                # Password — Tab se jao ya directly click
                try:
                    page.keyboard.press("Tab")
                    page.wait_for_timeout(500)
                    pwd_inp = page.locator('input[type="password"]').first
                    pwd_inp.click()
                    pwd_inp.fill("")
                    pwd_inp.type(IG_PASSWORD, delay=50)
                    log.info("Password typed")
                except Exception as e:
                    log.error(f"Password fill failed: {e}")
                page.wait_for_timeout(500)
                page.keyboard.press("Enter")
                page.wait_for_timeout(6000)

                # 2FA check
                if "challenge" in page.url or "two_factor" in page.url or "verify" in page.url:
                    log.info("Instagram 2FA — browser mein 90 sec mein code enter karo!")
                    try:
                        page.wait_for_url(
                            lambda url: "challenge" not in url and "two_factor" not in url and "verify" not in url,
                            timeout=90000
                        )
                        log.info("2FA complete!")
                    except:
                        log.warning("2FA timeout")
                    page.wait_for_timeout(3000)

                # "Save Info" popup dismiss
                for txt in ["Not Now", "Not now", "Skip"]:
                    try:
                        btn = page.locator(f'button:has-text("{txt}")').first
                        if btn.count() > 0 and btn.is_visible():
                            btn.click()
                            page.wait_for_timeout(2000)
                            break
                    except:
                        pass

                # Notifications popup
                page.wait_for_timeout(2000)
                for txt in ["Not Now", "Not now", "Skip", "Later"]:
                    try:
                        btn = page.locator(f'button:has-text("{txt}")').first
                        if btn.count() > 0 and btn.is_visible():
                            btn.click()
                            page.wait_for_timeout(2000)
                            break
                    except:
                        pass

                log.info("Login ho gaya")
                page.screenshot(path=str(VAULT / "Logs" / "ig_after_login.png"))

            # --- New Post button ---
            log.info("New post button dhund raha hai...")
            page.wait_for_timeout(2000)
            new_post_selectors = [
                '[aria-label="New post"]',
                'svg[aria-label="New post"]',
                'a[href="/create/style/"]',
                'a[href="/create/"]',
                '[aria-label="Create"]',
            ]
            clicked = False
            for selector in new_post_selectors:
                try:
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.click()
                        clicked = True
                        log.info(f"New post button mila: {selector}")
                        page.wait_for_timeout(2000)
                        break
                except:
                    continue

            if not clicked:
                page.screenshot(path=str(VAULT / "Logs" / "ig_no_newpost.png"))
                log.error("New post button nahi mila — 60 sec hold kar raha hoon dekho browser mein")
                log_action("instagram_post", "instagram.com", "failed_no_newpost", caption)
                page.wait_for_timeout(60000)
                return False

            page.wait_for_timeout(2000)

            # --- Image upload ---
            if not image_path or not Path(image_path).exists():
                log.error("Instagram ko image chahiye — image_path provide karo")
                page.wait_for_timeout(60000)
                return False

            log.info(f"Image upload kar raha hai: {image_path}")
            # File input Instagram ke "New post" click ke baad aata hai
            page.wait_for_timeout(2000)
            page.screenshot(path=str(VAULT / "Logs" / "ig_after_newpost.png"))

            # File input set karo
            with page.expect_file_chooser() as fc_info:
                # Click on "Select from computer" or any upload trigger
                for sel in [
                    'button:has-text("Select from computer")',
                    'button:has-text("Select from")',
                    '[role="button"]:has-text("Select from computer")',
                    'input[type="file"]',
                ]:
                    try:
                        el = page.locator(sel).first
                        if el.count() > 0 and el.is_visible():
                            el.click()
                            break
                    except:
                        pass
            fc_info.value.set_files(image_path)
            log.info("Image file set ho gaya")
            page.wait_for_timeout(3000)
            page.screenshot(path=str(VAULT / "Logs" / "ig_after_upload.png"))

            # Next → Next → Caption step
            for step in ["Crop step", "Filter step"]:
                try:
                    next_btn = page.get_by_role("button", name="Next")
                    if next_btn.count() > 0 and next_btn.is_visible():
                        next_btn.click()
                        log.info(f"Next click ({step})")
                        page.wait_for_timeout(2000)
                except:
                    pass

            page.screenshot(path=str(VAULT / "Logs" / "ig_caption_step.png"))

            # --- Caption type karo ---
            log.info("Caption type kar raha hai...")
            page.wait_for_timeout(1000)
            caption_selectors = [
                '[aria-label="Write a caption..."]',
                'textarea[aria-label="Write a caption..."]',
                'div[aria-label="Write a caption..."]',
                'div[role="textbox"]',
            ]
            typed = False
            for selector in caption_selectors:
                try:
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.click()
                        el.type(caption, delay=30)
                        typed = True
                        log.info(f"Caption type ho gaya via: {selector}")
                        break
                except:
                    continue

            if not typed:
                log.warning("Caption box nahi mila")

            page.wait_for_timeout(2000)

            # --- Share button ---
            shared = False
            for txt in ["Share", "Publish"]:
                try:
                    btn = page.get_by_role("button", name=txt)
                    if btn.count() > 0 and btn.is_visible():
                        btn.click()
                        shared = True
                        log.info(f"Share/Publish click: {txt}")
                        break
                except:
                    pass

            if not shared:
                page.screenshot(path=str(VAULT / "Logs" / "ig_share_debug.png"))
                log.error("Share button nahi mila")
                log_action("instagram_post", "instagram.com", "failed_no_sharebtn", caption)
                page.wait_for_timeout(60000)
                return False

            page.wait_for_timeout(5000)
            log.info("Instagram post successfully publish ho gaya!")
            log_action("instagram_post", "instagram.com", "success", caption)
            log.info("60 seconds hold — post check kar lo browser band hone se pehle...")
            page.wait_for_timeout(60000)
            return True

        except PlaywrightTimeout as e:
            log.error(f"Timeout: {e}")
            log_action("instagram_post", "instagram.com", f"timeout: {str(e)}", caption)
            page.screenshot(path=str(VAULT / "Logs" / "ig_error.png"))
            log.info("60 seconds hold (error state)...")
            page.wait_for_timeout(60000)
            return False
        except Exception as e:
            log.error(f"Error: {e}")
            log_action("instagram_post", "instagram.com", f"error: {str(e)}", caption)
            try:
                page.screenshot(path=str(VAULT / "Logs" / "ig_error.png"))
                log.info("60 seconds hold (error state)...")
                page.wait_for_timeout(60000)
            except:
                pass
            return False
        finally:
            browser.close()


def process_approved_file(filepath: Path):
    """Approved/ folder se Instagram post file process karo"""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    caption = ""
    image_path = None
    in_content = False

    for line in lines:
        if line.strip() == "## Post Content":
            in_content = True
            continue
        if in_content and line.startswith("image_path:"):
            image_path = line.split(":", 1)[1].strip()
            continue
        if in_content and line.startswith("## "):
            break
        if in_content:
            caption += line + "\n"

    caption = caption.strip()
    if not caption:
        log.error(f"Caption nahi mili: {filepath.name}")
        return False

    log.info(f"Posting from: {filepath.name}")
    success = post_to_instagram(caption, image_path)

    done_dir = VAULT / "Done"
    prefix = "SENT" if success else "FAILED"
    dest = done_dir / f"{prefix}_{filepath.name}"
    filepath.rename(dest)
    log.info(f"File moved to Done/: {dest.name}")
    return success


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python instagram_poster.py <approved_file_path>")
        print("       python instagram_poster.py --test")
        sys.exit(1)

    if sys.argv[1] == "--test":
        test_caption = "AI Employee test post - Gold Tier Feature 2 working!\n#AIEmployee #Automation #Python"
        test_image = str(VAULT / "Logs" / "ig_test_image.png")
        log.info("Test mode — directly posting with image...")
        success = post_to_instagram(test_caption, test_image)
        print("SUCCESS!" if success else "FAILED!")
    else:
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"File nahi mili: {filepath}")
            sys.exit(1)
        process_approved_file(filepath)
