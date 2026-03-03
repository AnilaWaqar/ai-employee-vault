"""
Email Sender — Approved drafts ko Gmail API se send karo
Flow: Approved/ folder watch karo → email send karo → Done/ mein move karo
"""

import os
import re
import time
import base64
import shutil
from datetime import datetime
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
TOKEN_FILE = os.path.join(BASE_DIR, 'assets', 'token.json')
APPROVED_DIR = os.path.join(VAULT_DIR, 'Approved')
DONE_DIR = os.path.join(VAULT_DIR, 'Done')
LOGS_DIR = os.path.join(VAULT_DIR, 'Logs')

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, f"email_sender_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def parse_draft(filepath):
    """Draft .md file se To, Subject aur Body extract karo."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    to_match = re.search(r'\*\*To:\*\*\s*(.+)', content)
    subject_match = re.search(r'\*\*Subject:\*\*\s*(.+)', content)

    if not to_match or not subject_match:
        return None, None, None

    to_email = to_match.group(1).strip()
    subject = subject_match.group(1).strip()

    # Body extract karo --- ke beech se
    body_match = re.search(r'---\n\n(.*?)\n\n---', content, re.DOTALL)
    if body_match:
        body = body_match.group(1).strip()
    else:
        # Fallback — draft response heading ke baad ka content
        body_match = re.search(r'# Draft Response\n.+\n.+\n\n---\n\n(.+?)(\n\n---|\Z)', content, re.DOTALL)
        body = body_match.group(1).strip() if body_match else ''

    # Review notes remove karo
    body = re.sub(r'>\s?\*\*Review Note.*', '', body, flags=re.DOTALL).strip()

    return to_email, subject, body


def send_email(service, to_email, subject, body):
    """Gmail API se email bhejo."""
    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().messages().send(
        userId='me',
        body={'raw': raw}
    ).execute()

    return result.get('id')


def process_approved_folder():
    """Approved/ folder mein sab drafts check karo aur send karo."""
    os.makedirs(APPROVED_DIR, exist_ok=True)
    os.makedirs(DONE_DIR, exist_ok=True)

    files = [f for f in os.listdir(APPROVED_DIR) if f.endswith('.md')]

    if not files:
        log("Approved/ mein koi draft nahi.")
        return 0

    log(f"{len(files)} approved draft(s) mile.")
    service = get_service()
    sent_count = 0

    for filename in files:
        filepath = os.path.join(APPROVED_DIR, filename)
        log(f"Processing: {filename}")

        try:
            to_email, subject, body = parse_draft(filepath)

            if not to_email or not body:
                log(f"  ❌ Parse failed — To/Subject/Body nahi mili: {filename}")
                continue

            log(f"  → To: {to_email}")
            log(f"  → Subject: {subject}")

            msg_id = send_email(service, to_email, subject, body)
            log(f"  ✅ Sent! Gmail Message ID: {msg_id}")

            # Move to Done/
            dest = os.path.join(DONE_DIR, f"SENT_{filename}")
            shutil.move(filepath, dest)
            log(f"  → Moved to Done/SENT_{filename}")
            sent_count += 1

        except Exception as e:
            log(f"  ❌ Error sending {filename}: {e}")

    return sent_count


def main():
    log("=== Email Sender Started ===")
    log(f"Watching: {APPROVED_DIR}")

    while True:
        try:
            sent = process_approved_folder()
            if sent > 0:
                log(f"Total sent: {sent}")
        except Exception as e:
            log(f"Loop error: {e}")

        log("60 seconds mein dobara check karega...")
        time.sleep(60)


if __name__ == '__main__':
    main()
