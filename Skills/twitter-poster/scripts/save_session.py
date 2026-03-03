"""
Twitter Session Saver
Ek baar manually login karo — session save ho jaega
Phir twitter_poster.py automatically use karega
"""
from playwright.sync_api import sync_playwright
from pathlib import Path

SESSION_DIR = str(Path("E:/HC/AI_Employee_Vault/twitter_session"))

print("=" * 50)
print("Twitter Session Saver")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        SESSION_DIR,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
        viewport={"width": 1280, "height": 900}
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto("https://x.com/login")

    print("\nBrowser khul gaya!")
    print("Twitter mein login karo (Google se ya direct)")
    print("Login hone ke baad yahan wapas aao aur Enter dabao\n")
    input(">>> Login ke baad ENTER dabao: ")

    browser.close()
    print("\nSession save ho gaya!")
    print("Ab twitter_poster.py --test run karo")
