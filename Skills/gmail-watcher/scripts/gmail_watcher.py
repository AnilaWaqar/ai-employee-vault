"""
Gmail Watcher — unread+important emails fetch karo
aur Needs_Action folder mein .md files banao
Har 120 seconds mein repeat karta hai
"""

import os
import time
import json
import base64
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
TOKEN_FILE = os.path.join(BASE_DIR, 'assets', 'token.json')
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'assets', 'credentials.json')
NEEDS_ACTION_DIR = os.path.join(VAULT_DIR, 'Needs_Action')
LOGS_DIR = os.path.join(VAULT_DIR, 'Logs')
PROCESSED_FILE = os.path.join(BASE_DIR, 'assets', 'processed_ids.json')

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, f"gmail_watcher_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


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


def save_email_md(email_id, sender, subject, date, body, snippet):
    os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)
    safe_id = email_id[:16]
    filename = f"EMAIL_{safe_id}.md"
    filepath = os.path.join(NEEDS_ACTION_DIR, filename)

    content = f"""---
email_id: {email_id}
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

    return filename


def fetch_emails(service, processed_ids):
    new_count = 0
    try:
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD', 'IMPORTANT'],
            maxResults=10
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            log("Koi naya email nahi mila.")
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

                filename = save_email_md(msg_id, sender, subject, date, body, snippet)
                processed_ids.add(msg_id)
                new_count += 1
                log(f"Email saved: {filename} | From: {sender} | Subject: {subject}")

            except Exception as e:
                log(f"Email process error ({msg_id}): {e}")

        save_processed(processed_ids)

    except Exception as e:
        log(f"Fetch error: {e}")

    return new_count


def main():
    log("=== Gmail Watcher Started ===")
    log(f"Vault: {VAULT_DIR}")
    log(f"Needs_Action: {NEEDS_ACTION_DIR}")

    processed_ids = load_processed()
    log(f"Previously processed emails: {len(processed_ids)}")

    while True:
        try:
            log("--- Checking Gmail ---")
            service = get_service()
            new = fetch_emails(service, processed_ids)
            log(f"Naye emails: {new}")
        except Exception as e:
            log(f"Main loop error: {e}")

        log("120 seconds mein dobara check karega...")
        time.sleep(120)


if __name__ == '__main__':
    main()
