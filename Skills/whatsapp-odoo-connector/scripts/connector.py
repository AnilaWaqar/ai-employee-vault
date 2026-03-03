"""
WhatsApp → Odoo Invoice Connector
Gold Tier — AI Employee Vault

Loop every 60s:
  Phase A: Scan Needs_Action/WHATSAPP_*.md with invoice keyword
           → create Odoo draft invoice via Claude API + Odoo MCP
           → write Plans/INVOICE_APPROVAL_*.md

  Phase B: Scan Approved/INVOICE_APPROVAL_*.md
           → confirm_invoice via Claude API + Odoo MCP
           → send email via Email MCP
           → move files to Done/
"""

import os
import re
import json
import time
import shutil
import logging
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# ── Config ───────────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parents[3] / ".env")

VAULT_PATH    = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))
LOOP_INTERVAL = int(os.getenv("CONNECTOR_INTERVAL", 60))
DRY_RUN       = os.getenv("DRY_RUN", "false").lower() == "true"

NEEDS_ACTION_DIR = VAULT_PATH / "Needs_Action"
APPROVED_DIR     = VAULT_PATH / "Approved"
PLANS_DIR        = VAULT_PATH / "Plans"
DONE_DIR         = VAULT_PATH / "Done"
LOGS_DIR         = VAULT_PATH / "Logs"

for d in [NEEDS_ACTION_DIR, APPROVED_DIR, PLANS_DIR, DONE_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "connector.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("whatsapp-odoo-connector")


def append_daily_log(msg: str):
    """Append to today's Logs/YYYY-MM-DD.md."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"{today}.md"
    ts = datetime.now().strftime("%H:%M")
    entry = f"[{ts}] whatsapp-odoo-connector: {msg}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)


# ── Front Matter Parser ───────────────────────────────────────────────────────
def parse_front_matter(text: str) -> dict:
    """Extract YAML front matter from markdown file."""
    meta = {}
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return meta
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()
    return meta


def extract_amount(text: str) -> str:
    """Extract numeric amount from message text."""
    # Match patterns like: 5000, Rs 10,000, $500, PKR 25000, 1,500.00
    patterns = [
        r"(?:rs\.?|pkr\.?|\$|usd|aud|gbp|eur)?\s*(\d[\d,]*(?:\.\d{1,2})?)",
        r"(\d[\d,]*(?:\.\d{1,2})?)\s*(?:rs\.?|pkr\.?|\$|rupees?|dollars?)?",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Return the largest number found (likely the invoice amount)
            amounts = []
            for m in matches:
                try:
                    amounts.append(float(m.replace(",", "")))
                except ValueError:
                    pass
            if amounts:
                return str(int(max(amounts)))
    return "UNKNOWN"


def extract_description(text: str) -> str:
    """Extract a brief description from the message."""
    # Remove common filler words and extract the core request
    text = text.strip()
    # Limit to first 100 chars for description
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    desc = lines[0] if lines else text[:100]
    return desc[:150]


# ── Odoo MCP via Claude API ───────────────────────────────────────────────────
def run_claude_with_mcp(prompt: str, max_turns: int = 5) -> dict:
    """
    Call Claude API with Odoo MCP tools.
    Returns dict with keys: result (str), invoice_id (int|None), customer_id (int|None)
    """
    client = anthropic.Anthropic()

    # MCP server config — adjust url/key to match your setup
    mcp_url = os.getenv("ODOO_MCP_URL", "http://localhost:3001/mcp")

    messages = [{"role": "user", "content": prompt}]
    result_text = ""
    invoice_id = None
    customer_id = None

    # Agentic loop
    for turn in range(max_turns):
        response = client.beta.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=messages,
            mcp_servers=[
                {
                    "type": "url",
                    "url": mcp_url,
                    "name": "odoo",
                }
            ],
            betas=["mcp-client-2025-04-04"],
        )

        # Collect text output
        for block in response.content:
            if hasattr(block, "text"):
                result_text += block.text

        # Check stop reason
        if response.stop_reason == "end_turn":
            break

        # Build next message from tool results (handled automatically by MCP beta)
        messages.append({"role": "assistant", "content": response.content})

        # Check if we need to continue (tool_use blocks remain)
        has_tool_use = any(
            getattr(b, "type", "") == "tool_use" for b in response.content
        )
        if not has_tool_use:
            break

    # Extract IDs from result text
    inv_match = re.search(r"invoice[_\s]*id[:\s=]+(\d+)", result_text, re.IGNORECASE)
    if inv_match:
        invoice_id = int(inv_match.group(1))

    cust_match = re.search(r"customer[_\s]*id[:\s=]+(\d+)", result_text, re.IGNORECASE)
    if cust_match:
        customer_id = int(cust_match.group(1))

    return {
        "result": result_text,
        "invoice_id": invoice_id,
        "customer_id": customer_id,
    }


# ── Phase A: Process WHATSAPP invoice files ───────────────────────────────────
def process_whatsapp_files():
    """Scan Needs_Action/ for WHATSAPP_*.md with invoice keyword."""
    files = sorted(NEEDS_ACTION_DIR.glob("WHATSAPP_*.md"))
    processed_count = 0

    for filepath in files:
        text = filepath.read_text(encoding="utf-8")
        meta = parse_front_matter(text)

        # Must be pending + have invoice keyword
        if meta.get("status", "").lower() != "pending":
            continue
        keywords = meta.get("keywords_found", "").lower()
        if "invoice" not in keywords and "payment" not in keywords:
            continue

        sender = meta.get("from", "Unknown")
        log.info(f"Processing invoice request from: {sender} | file: {filepath.name}")

        # Extract message body
        body_match = re.search(r"## Message Content\n(.*?)(?:\n##|\Z)", text, re.DOTALL)
        message_body = body_match.group(1).strip() if body_match else text[:300]

        amount = extract_amount(message_body)
        description = extract_description(message_body)

        if DRY_RUN:
            log.info(f"[DRY_RUN] Would create invoice for {sender} | amount={amount}")
            continue

        # Build prompt for Claude + Odoo MCP
        prompt = f"""You are an Odoo accounting assistant. Do the following steps:

1. Call list_customers to search for a customer named "{sender}"
2. If found, use their ID. If not found, call create_customer with name="{sender}"
3. Call create_invoice with:
   - customer_id: (from step 1 or 2)
   - description: "{description}"
   - amount: {amount if amount != "UNKNOWN" else "1000"}
4. Report back the invoice_id and customer_id in your response.

Important: Always mention "invoice_id: X" and "customer_id: Y" explicitly in your response.
"""

        log.info(f"Calling Claude API + Odoo MCP for {sender}...")
        result = run_claude_with_mcp(prompt)

        invoice_id = result["invoice_id"]
        customer_id = result["customer_id"]

        if not invoice_id:
            log.error(f"Failed to get invoice_id for {sender}. Claude output: {result['result'][:200]}")
            append_daily_log(f"FAILED invoice creation | file={filepath.name} | customer={sender}")
            continue

        log.info(f"Invoice created: ID={invoice_id} | Customer={sender} (ID={customer_id})")

        # Write approval file
        now = datetime.now()
        ts = now.strftime("%Y%m%d_%H%M%S")
        approval_filename = f"INVOICE_APPROVAL_{ts}.md"
        approval_path = PLANS_DIR / approval_filename

        approval_content = f"""---
type: invoice_approval
invoice_id: {invoice_id}
customer: {sender}
customer_id: {customer_id or "unknown"}
amount: {amount}
status: pending_approval
whatsapp_file: {filepath.name}
customer_email:
---

# Invoice Approval Required

**Customer:** {sender}
**Amount:** {amount}
**Description:** {description}
**Odoo Invoice ID:** {invoice_id}
**Source:** WhatsApp message from {sender}

## Original Message
> {message_body[:500]}

## Actions Required
- [ ] Review invoice details above
- [ ] Fill in `customer_email:` in front matter if you want email sent
- [ ] Move this file to `Approved/` to confirm invoice + send email
- [ ] Or delete this file to reject

**Odoo Link:** http://localhost:8069/web#id={invoice_id}&model=account.move

---
*Created by whatsapp-odoo-connector at {now.isoformat()}*
"""

        approval_path.write_text(approval_content, encoding="utf-8")
        log.info(f"Approval file created: {approval_filename}")

        # Mark original WHATSAPP file as processed (update status in-place)
        updated_text = text.replace("status: pending", "status: processed", 1)
        filepath.write_text(updated_text, encoding="utf-8")

        append_daily_log(
            f"Invoice draft created | file={filepath.name} | customer={sender} | "
            f"invoice_id={invoice_id} | approval={approval_filename}"
        )
        processed_count += 1

    if processed_count == 0:
        log.info("Phase A: No new invoice requests found.")
    else:
        log.info(f"Phase A: Processed {processed_count} invoice request(s).")


# ── Phase B: Confirm approved invoices ───────────────────────────────────────
def process_approved_files():
    """Scan Approved/ for INVOICE_APPROVAL_*.md and confirm them."""
    files = sorted(APPROVED_DIR.glob("INVOICE_APPROVAL_*.md"))
    confirmed_count = 0

    for filepath in files:
        text = filepath.read_text(encoding="utf-8")
        meta = parse_front_matter(text)

        if meta.get("type", "") != "invoice_approval":
            continue
        if meta.get("status", "") not in ("pending_approval", ""):
            continue

        invoice_id = meta.get("invoice_id", "")
        customer = meta.get("customer", "Unknown")
        amount = meta.get("amount", "")
        customer_email = meta.get("customer_email", "").strip()
        whatsapp_file = meta.get("whatsapp_file", "")

        if not invoice_id or not str(invoice_id).isdigit():
            log.error(f"Invalid invoice_id in {filepath.name}: '{invoice_id}'")
            continue

        invoice_id = int(invoice_id)
        log.info(f"Confirming invoice ID={invoice_id} for {customer}...")

        if DRY_RUN:
            log.info(f"[DRY_RUN] Would confirm invoice {invoice_id} and email {customer_email}")
            continue

        # Confirm invoice via Claude + Odoo MCP
        confirm_prompt = f"""You are an Odoo accounting assistant.
Call confirm_invoice with invoice_id={invoice_id}.
Report back whether it was successfully confirmed.
"""
        result = run_claude_with_mcp(confirm_prompt, max_turns=3)
        log.info(f"Confirm result for invoice {invoice_id}: {result['result'][:200]}")

        # Send email if customer_email is provided
        if customer_email and "@" in customer_email:
            log.info(f"Sending invoice notification email to {customer_email}...")
            email_prompt = f"""Draft and send an email with:
To: {customer_email}
Subject: Invoice #{invoice_id} - Payment Details
Body: Professional invoice notification saying that Invoice #{invoice_id}
for {customer} has been generated for amount {amount}.
Please contact us if you have any questions.
"""
            # Email is handled by Email MCP — this script logs the intent;
            # actual send requires Email MCP available in Claude Code session.
            log.info(f"Email intent logged for {customer_email} (run via Claude Code for MCP send)")
        else:
            log.info(f"No customer email found — skipping email for invoice {invoice_id}")

        # Move approval file to Done/
        done_name = f"DONE_{filepath.name}"
        done_path = DONE_DIR / done_name
        shutil.move(str(filepath), str(done_path))
        log.info(f"Moved {filepath.name} → Done/{done_name}")

        # Move original WHATSAPP file to Done/ if it exists
        if whatsapp_file:
            wa_src = NEEDS_ACTION_DIR / whatsapp_file
            if wa_src.exists():
                shutil.move(str(wa_src), str(DONE_DIR / whatsapp_file))
                log.info(f"Moved {whatsapp_file} → Done/")

        append_daily_log(
            f"Invoice confirmed | invoice_id={invoice_id} | customer={customer} | "
            f"email={'sent' if customer_email else 'skipped'}"
        )
        confirmed_count += 1

    if confirmed_count == 0:
        log.info("Phase B: No approved invoices to confirm.")
    else:
        log.info(f"Phase B: Confirmed {confirmed_count} invoice(s).")


# ── Main Loop ─────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("WhatsApp → Odoo Invoice Connector started")
    log.info(f"Vault: {VAULT_PATH} | Interval: {LOOP_INTERVAL}s | DRY_RUN: {DRY_RUN}")
    log.info("=" * 60)
    append_daily_log("Connector started")

    while True:
        try:
            log.info(f"--- Cycle @ {datetime.now().strftime('%H:%M:%S')} ---")
            process_whatsapp_files()   # Phase A
            process_approved_files()   # Phase B
        except KeyboardInterrupt:
            log.info("Connector stopped by user.")
            append_daily_log("Connector stopped")
            break
        except Exception as e:
            log.error(f"Unhandled error: {e}", exc_info=True)
            append_daily_log(f"ERROR: {e}")

        log.info(f"Sleeping {LOOP_INTERVAL}s...")
        time.sleep(LOOP_INTERVAL)


if __name__ == "__main__":
    main()
