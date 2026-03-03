"""
WhatsApp Watcher — Silver Tier Feature 1
Playwright se WhatsApp Web monitor karo.
Business keywords detect ho toh /Needs_Action/ mein file banao.
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── Config ──────────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parents[3] / ".env")

VAULT_PATH        = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))
CHECK_INTERVAL    = int(os.getenv("CHECK_INTERVAL", 60))
DRY_RUN           = os.getenv("DRY_RUN", "false").lower() == "true"
MAX_PER_HOUR      = int(os.getenv("MAX_ACTIONS_PER_HOUR", 20))

NEEDS_ACTION_DIR  = VAULT_PATH / "Needs_Action"
LOGS_DIR          = VAULT_PATH / "Logs"
SESSION_DIR       = VAULT_PATH / "whatsapp_session"
PROCESSED_FILE    = VAULT_PATH / "Skills" / "whatsapp-watcher" / "assets" / "processed_ids.json"

KEYWORDS = [
    "urgent", "asap", "emergency", "invoice", "payment",
    "quote", "meeting", "deadline", "schedule", "help",
    "issue", "problem", "project", "task", "delivery",
]

HIGH_PRIORITY_KEYWORDS = {"urgent", "asap", "emergency"}

# ── Logging ──────────────────────────────────────────────────────────────────
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "whatsapp_watcher.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("whatsapp-watcher")


# ── Processed IDs ────────────────────────────────────────────────────────────
def load_processed() -> set:
    if PROCESSED_FILE.exists():
        return set(json.loads(PROCESSED_FILE.read_text(encoding="utf-8")))
    return set()


def save_processed(processed: set):
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.write_text(json.dumps(list(processed), indent=2), encoding="utf-8")


def make_msg_id(sender: str, text: str) -> str:
    raw = f"{sender}::{text[:100]}"
    return hashlib.md5(raw.encode()).hexdigest()


# ── Keyword Matching ─────────────────────────────────────────────────────────
def find_keywords(text: str) -> list[str]:
    lower = text.lower()
    return [kw for kw in KEYWORDS if kw in lower]


def get_priority(keywords: list[str]) -> str:
    if any(kw in HIGH_PRIORITY_KEYWORDS for kw in keywords):
        return "high"
    return "normal"


# ── Action File ──────────────────────────────────────────────────────────────
def create_action_file(sender: str, text: str, keywords: list[str]):
    now = datetime.now()
    timestamp_file = now.strftime("%Y%m%d_%H%M%S")
    timestamp_iso  = now.isoformat()
    priority       = get_priority(keywords)
    kw_str         = ", ".join(keywords)
    kw_ticks       = ", ".join(f"`{kw}`" for kw in keywords)
    priority_label = "HIGH PRIORITY" if priority == "high" else "NORMAL PRIORITY"

    suggested = ["- [ ] Read and respond to message"]
    if "invoice" in keywords:
        suggested.append("- [ ] Generate invoice if requested")
    if any(kw in HIGH_PRIORITY_KEYWORDS for kw in keywords):
        suggested.append("- [ ] Mark as priority if urgent")
    if "meeting" in keywords or "schedule" in keywords:
        suggested.append("- [ ] Check calendar and confirm availability")
    if "payment" in keywords:
        suggested.append("- [ ] Check payment details and confirm")

    content = f"""---
type: whatsapp_message
from: {sender}
received: {timestamp_iso}
keywords_found: {kw_str}
priority: {priority}
status: pending
requires_approval: true
---

## Message Content
{text}

## Detected Keywords
{kw_ticks}

## Priority
{priority_label}

## Suggested Actions
{chr(10).join(suggested)}
"""

    filename = f"WHATSAPP_{timestamp_file}.md"
    dest = NEEDS_ACTION_DIR / filename

    if DRY_RUN:
        log.info(f"[DRY_RUN] Would create: {filename} | from={sender} | keywords={kw_str}")
        return

    NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    log.info(f"[CREATED] {filename} | from={sender} | priority={priority} | keywords={kw_str}")


# ── WhatsApp Scraper ─────────────────────────────────────────────────────────
def get_unread_messages(page) -> list[dict]:
    """WhatsApp Web se unread conversations aur messages extract karo."""
    messages = []
    try:
        # Multiple selectors try karo — WhatsApp Web DOM aksar change hota hai
        unread_selectors = [
            'span[data-testid="icon-unread-count"]',
            'span[aria-label*="unread message"]',
            'span[aria-label*="unread"]',
            'span[aria-label*="Unread"]',
            'span._ahxt',
            'div[role="gridcell"] span[aria-label*="unread"]',
        ]

        unread_chats = []
        for sel in unread_selectors:
            found = page.query_selector_all(sel)
            if found:
                log.info(f"Unread selector matched: {sel} ({len(found)} chats)")
                unread_chats = found
                break

        if not unread_chats:
            return messages

        for chat_el in unread_chats:
            try:
                # Parent chat row dhundo
                chat_row = chat_el.evaluate_handle(
                    "el => el.closest('[data-testid=\"cell-frame-container\"]') "
                    "|| el.closest('div[role=\"listitem\"]') "
                    "|| el.closest('div[tabindex=\"-1\"]')"
                )
                if not chat_row:
                    continue

                # Sender name — multiple selectors
                sender = "Unknown"
                for s_sel in [
                    '[data-testid="cell-frame-title"]',
                    'span[dir="auto"][title]',
                    'span[dir="ltr"]',
                ]:
                    sender_el = chat_row.query_selector(s_sel)
                    if sender_el:
                        t = sender_el.inner_text().strip()
                        if t:
                            sender = t
                            break

                # Message preview — multiple selectors
                preview = ""
                for p_sel in [
                    '[data-testid="last-msg-status"] ~ span',
                    'span.x78zum5 span',
                    '[data-testid="cell-frame-secondary-detail"] span',
                    'div[data-testid="cell-frame-secondary"] span span',
                    'span[dir="ltr"].x1iyjqo2',
                ]:
                    preview_el = chat_row.query_selector(p_sel)
                    if preview_el:
                        t = preview_el.inner_text().strip()
                        if t:
                            preview = t
                            break

                if sender and sender != "Unknown":
                    log.info(f"Unread chat: {sender} | preview: {preview[:60]}")
                    messages.append({"sender": sender, "text": preview})

            except Exception as e:
                log.warning(f"Chat parse error: {e}")
                continue

    except Exception as e:
        log.warning(f"Chat list parse error: {e}")

    return messages


def open_chat_and_read(page, sender: str) -> list[str]:
    """Specific chat kholo aur recent messages paro."""
    texts = []
    try:
        # Search box se chat dhundo
        search = page.query_selector('[data-testid="chat-list-search"]')
        if search:
            search.click()
            search.fill(sender)
            page.wait_for_timeout(1500)

            first_result = page.query_selector('[data-testid="cell-frame-container"]')
            if first_result:
                first_result.click()
                page.wait_for_timeout(1500)

                # Visible messages paro
                msg_els = page.query_selector_all(
                    '[data-testid="msg-container"] span.selectable-text'
                )
                for el in msg_els[-10:]:  # Last 10 messages
                    t = el.inner_text().strip()
                    if t:
                        texts.append(t)

            # Search clear karo
            search.fill("")
            page.wait_for_timeout(500)

    except Exception as e:
        log.warning(f"Chat read error for {sender}: {e}")

    return texts


# ── Rate Limiter ─────────────────────────────────────────────────────────────
class RateLimiter:
    def __init__(self, max_per_hour: int):
        self.max_per_hour = max_per_hour
        self.timestamps: deque = deque()

    def can_proceed(self) -> bool:
        now = datetime.now()
        cutoff = now - timedelta(hours=1)
        # 1 ghante se purani timestamps hataao
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()
        return len(self.timestamps) < self.max_per_hour

    def record(self):
        self.timestamps.append(datetime.now())


# ── Main Loop ────────────────────────────────────────────────────────────────
def run():
    processed = load_processed()
    rate_limiter = RateLimiter(MAX_PER_HOUR)

    log.info("=" * 60)
    log.info("WhatsApp Watcher started")
    log.info(f"Vault: {VAULT_PATH}")
    log.info(f"DRY_RUN: {DRY_RUN}")
    log.info(f"Check interval: {CHECK_INTERVAL}s")
    log.info(f"Max actions/hour: {MAX_PER_HOUR}")
    log.info("=" * 60)

    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=True,
            args=["--no-sandbox"],
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        log.info("Browser launched. WhatsApp Web khul raha hai...")
        page.goto("https://web.whatsapp.com")

        # QR scan ka wait karo — multiple selectors try karo
        log.info("Agar pehli baar hai toh QR code scan karo...")
        login_selectors = [
            '[data-testid="chat-list-search"]',
            '[data-testid="search"]',
            '[aria-label="Search input textbox"]',
            '[title="Search input textbox"]',
            '#side',
            'div[contenteditable="true"]',
        ]
        logged_in = False
        for sel in login_selectors:
            try:
                page.wait_for_selector(sel, timeout=20_000)
                logged_in = True
                log.info(f"WhatsApp Web successfully logged in. (selector: {sel})")
                break
            except PWTimeout:
                continue
        if not logged_in:
            log.error("Login timeout. QR scan nahi hua. Script band ho rahi hai.")
            browser.close()
            return

        # Main monitoring loop
        while True:
            try:
                log.info("--- Checking for new messages ---")

                # Unread chats ki list lao
                messages = get_unread_messages(page)
                log.info(f"Unread chats found: {len(messages)}")

                for msg in messages:
                    sender = msg["sender"]
                    text   = msg["text"]

                    msg_id = make_msg_id(sender, text)

                    # Duplicate check
                    if msg_id in processed:
                        continue

                    # Keyword match
                    keywords = find_keywords(text)
                    if not keywords:
                        # Preview mein keyword nahi — full chat kholo
                        full_texts = open_chat_and_read(page, sender)
                        for full_text in full_texts:
                            full_id = make_msg_id(sender, full_text)
                            if full_id in processed:
                                continue
                            kws = find_keywords(full_text)
                            if kws:
                                if not rate_limiter.can_proceed():
                                    log.warning(
                                        f"Rate limit reached ({MAX_PER_HOUR}/hr). "
                                        f"Skipping: {sender}"
                                    )
                                    break
                                create_action_file(sender, full_text, kws)
                                rate_limiter.record()
                                processed.add(full_id)
                        processed.add(msg_id)
                        save_processed(processed)
                        continue

                    # Rate limit check
                    if not rate_limiter.can_proceed():
                        log.warning(
                            f"Rate limit reached ({MAX_PER_HOUR}/hr). "
                            f"Skipping: {sender} — '{text[:50]}'"
                        )
                        processed.add(msg_id)
                        save_processed(processed)
                        continue

                    create_action_file(sender, text, keywords)
                    rate_limiter.record()
                    processed.add(msg_id)
                    save_processed(processed)

            except PWTimeout:
                log.warning("Page timeout — page reload karo")
                try:
                    page.reload(wait_until="networkidle", timeout=30_000)
                    page.wait_for_selector(
                        '[data-testid="chat-list-search"]', timeout=30_000
                    )
                except Exception:
                    log.error("Reload failed. Next cycle mein retry...")

            except Exception as e:
                log.error(f"Unexpected error: {e}", exc_info=True)

            log.info(f"Next check in {CHECK_INTERVAL}s...")
            page.wait_for_timeout(CHECK_INTERVAL * 1000)


if __name__ == "__main__":
    run()
