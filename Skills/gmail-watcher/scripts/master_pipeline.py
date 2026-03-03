"""
Master Pipeline — Sab scripts ek saath chalao
Gmail Watcher + Email Sender + Dashboard Updater
Har 120 seconds mein automatically sab check karta hai
"""

import os
import time
import json
import base64
import shutil
import re
from datetime import datetime
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
TOKEN_FILE = os.path.join(BASE_DIR, 'assets', 'token.json')
NEEDS_ACTION_DIR = os.path.join(VAULT_DIR, 'Needs_Action')
APPROVED_DIR = os.path.join(VAULT_DIR, 'Approved')
DONE_DIR = os.path.join(VAULT_DIR, 'Done')
DRAFTS_DIR = os.path.join(VAULT_DIR, 'Drafts')
LOGS_DIR = os.path.join(VAULT_DIR, 'Logs')
PROCESSED_FILE = os.path.join(BASE_DIR, 'assets', 'processed_ids.json')
DASHBOARD_FILE = os.path.join(VAULT_DIR, 'Dashboard.md')

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]


# ─────────────────────────────────────────
# LOGGER
# ─────────────────────────────────────────

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, f"pipeline_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


# ─────────────────────────────────────────
# GMAIL SERVICE
# ─────────────────────────────────────────

def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


# ─────────────────────────────────────────
# STEP 1 — GMAIL WATCHER
# ─────────────────────────────────────────

def load_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            return set(json.load(f))
    return set()


def save_processed(ids):
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(list(ids), f)


def get_body(payload):
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
    else:
        data = payload['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return body.strip()


def fetch_emails(service, processed_ids):
    new_count = 0
    os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)
    try:
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD', 'IMPORTANT'],
            maxResults=10
        ).execute()
        messages = results.get('messages', [])
        if not messages:
            return 0
        for msg in messages:
            msg_id = msg['id']
            if msg_id in processed_ids:
                continue
            try:
                full_msg = service.users().messages().get(
                    userId='me', id=msg_id, format='full'
                ).execute()
                headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}
                sender = headers.get('From', 'Unknown')
                subject = headers.get('Subject', 'No Subject')
                date = headers.get('Date', 'Unknown')
                snippet = full_msg.get('snippet', '')
                body = get_body(full_msg['payload'])

                filename = f"EMAIL_{msg_id[:16]}.md"
                filepath = os.path.join(NEEDS_ACTION_DIR, filename)
                content = f"""---
email_id: {msg_id}
sender: {sender}
subject: {subject}
date: {date}
status: needs_action
fetched_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# {subject}

**From:** {sender}
**Date:** {date}

---

## Email Content

{body if body else snippet}

---

**Action Required:** Review and respond if needed
"""
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

                processed_ids.add(msg_id)
                new_count += 1
                log(f"[WATCHER] New email: {filename} | From: {sender} | Subject: {subject}")
            except Exception as e:
                log(f"[WATCHER] Error processing {msg_id}: {e}")
        save_processed(processed_ids)
    except Exception as e:
        log(f"[WATCHER] Fetch error: {e}")
    return new_count


# ─────────────────────────────────────────
# STEP 2 — EMAIL SENDER
# ─────────────────────────────────────────

def parse_draft(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    to_match = re.search(r'\*\*To:\*\*\s*(.+)', content)
    subject_match = re.search(r'\*\*Subject:\*\*\s*(.+)', content)
    if not to_match or not subject_match:
        return None, None, None
    to_email = to_match.group(1).strip()
    subject = subject_match.group(1).strip()
    body_match = re.search(r'---\n\n(.*?)\n\n---', content, re.DOTALL)
    body = body_match.group(1).strip() if body_match else ''
    body = re.sub(r'>\s?\*\*Review Note.*', '', body, flags=re.DOTALL).strip()
    return to_email, subject, body


def send_approved_emails(service):
    os.makedirs(APPROVED_DIR, exist_ok=True)
    os.makedirs(DONE_DIR, exist_ok=True)
    files = [f for f in os.listdir(APPROVED_DIR) if f.endswith('.md')]
    if not files:
        return 0
    sent_count = 0
    for filename in files:
        filepath = os.path.join(APPROVED_DIR, filename)
        try:
            to_email, subject, body = parse_draft(filepath)
            if not to_email or not body:
                log(f"[SENDER] Parse failed: {filename}")
                continue
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            result = service.users().messages().send(
                userId='me', body={'raw': raw}
            ).execute()
            log(f"[SENDER] ✅ Sent to {to_email} | Subject: {subject} | ID: {result.get('id')}")
            dest = os.path.join(DONE_DIR, f"SENT_{filename}")
            shutil.move(filepath, dest)
            sent_count += 1
        except Exception as e:
            log(f"[SENDER] Error sending {filename}: {e}")
    return sent_count


# ─────────────────────────────────────────
# STEP 3 — DASHBOARD UPDATER
# ─────────────────────────────────────────

def update_dashboard():
    try:
        needs_action = len([f for f in os.listdir(NEEDS_ACTION_DIR) if f.endswith('.md')]) if os.path.exists(NEEDS_ACTION_DIR) else 0
        drafts = len([f for f in os.listdir(DRAFTS_DIR) if f.endswith('.md')]) if os.path.exists(DRAFTS_DIR) else 0
        pending = len([f for f in os.listdir(os.path.join(VAULT_DIR, 'Pending_Approval')) if f.endswith('.md')]) if os.path.exists(os.path.join(VAULT_DIR, 'Pending_Approval')) else 0
        done = len(os.listdir(DONE_DIR)) if os.path.exists(DONE_DIR) else 0

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        content = f"""# Gmail AI Employee - Dashboard

**Last Updated**: {now}

---

## Current Status

| Metric | Count | Location |
|--------|-------|----------|
| Pending Tasks | {needs_action} | Needs_Action/ |
| Drafts Ready | {drafts} | Drafts/ |
| Pending Approval | {pending} | Pending_Approval/ |
| Completed Tasks | {done} | Done/ |

---

## System Health

| Component | Status | Last Check |
|-----------|--------|------------|
| Gmail Watcher | ✅ Running | {now} |
| Email Sender | ✅ Running | {now} |
| Master Pipeline | ✅ Active | {now} |

---

## Skills Connected

| Skill | Status |
|-------|--------|
| Gmail Watcher | ✅ Active |
| Inbox Processor | ✅ Active |
| Email Sender | ✅ Active |
| Dashboard Updater | ✅ Active |

---

**Auto-updated by**: `master_pipeline`
"""
        with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        log(f"[DASHBOARD] Updated — Needs_Action:{needs_action} | Drafts:{drafts} | Pending:{pending} | Done:{done}")
    except Exception as e:
        log(f"[DASHBOARD] Update error: {e}")


# ─────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────

def main():
    log("=" * 50)
    log("=== MASTER PIPELINE STARTED ===")
    log(f"=== Vault: {VAULT_DIR} ===")
    log("=" * 50)

    processed_ids = load_processed()
    log(f"Previously processed emails: {len(processed_ids)}")

    while True:
        log("--- Pipeline Cycle Start ---")
        try:
            service = get_service()

            # Step 1 — Fetch new emails
            new_emails = fetch_emails(service, processed_ids)
            log(f"[WATCHER] New emails fetched: {new_emails}")

            # Step 2 — Send approved drafts
            sent = send_approved_emails(service)
            log(f"[SENDER] Emails sent: {sent}")

            # Step 3 — Update dashboard
            update_dashboard()

        except Exception as e:
            log(f"[PIPELINE] Cycle error: {e}")

        log("--- Cycle complete. 120s mein dobara ---")
        time.sleep(120)


if __name__ == '__main__':
    main()
