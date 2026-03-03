---
name: whatsapp-odoo-connector
description: WhatsApp se invoice requests detect karo, Odoo mein invoice banao,
  aur human approval ke baad confirm + email bhejo. Use karo jab WhatsApp pe
  kisi ne invoice manga ho (keyword: invoice, payment, quote).
---

# WhatsApp → Odoo Invoice Connector

## Overview
Yeh skill `Needs_Action/WHATSAPP_*.md` files scan karti hai jisme `invoice`
keyword ho. Customer ka invoice Odoo mein draft karta hai, approval file banata
hai, aur approved hone ke baad invoice confirm + email bhejta hai.

---

## Steps (Claude ka kaam jab /whatsapp-odoo-connector chalao)

### Phase 1 — Scan & Detect
1. `Needs_Action/` folder mein saare `WHATSAPP_*.md` files dhundo
2. Sirf woh files lo jisme:
   - `keywords_found:` mein `invoice` ho
   - `status: pending` ho
3. Agar koi file nahi mili → user ko batao "No pending invoice requests found"

### Phase 2 — Extract Info
Har matching file se yeh info nikalo:
- **Customer name**: `from:` field se (e.g., "Ali Hassan")
- **Message text**: `## Message Content` section se
- **Amount**: message mein number dhundo (e.g., "5000", "Rs 10,000", "$500")
- **Description**: message ka context (e.g., "web design", "monthly retainer")
- **Original filename**: (e.g., `WHATSAPP_20260301_120000.md`)

### Phase 3 — Odoo Customer Lookup / Create
1. `list_customers` call karo
2. Customer name se match dhundo (case-insensitive partial match)
3. Agar mila → us ka `id` use karo
4. Agar nahi mila → `create_customer` call karo (name field se)
5. Customer ID save karo

### Phase 4 — Create Draft Invoice
1. `create_invoice` call karo:
   - `customer_id`: Phase 3 se mila ID
   - `description`: message se extracted description
   - `amount`: message se extracted amount (number only, no currency symbol)
2. Returned `invoice_id` save karo

### Phase 5 — Create Approval File
`Plans/INVOICE_APPROVAL_YYYYMMDD_HHMMSS.md` banao (current timestamp use karo):

```markdown
---
type: invoice_approval
invoice_id: {invoice_id}
customer: {customer_name}
customer_id: {customer_id}
amount: {amount}
status: pending_approval
whatsapp_file: {original_filename}
customer_email: {email_if_known}
---

# Invoice Approval Required

**Customer:** {customer_name}
**Amount:** {amount}
**Description:** {description}
**Odoo Invoice ID:** {invoice_id}
**Source:** WhatsApp message from {customer_name}

## Original Message
> {original_message_text}

## Actions Required
- [ ] Review invoice details above
- [ ] Move this file to `Approved/` to confirm invoice + send email
- [ ] Or delete this file to reject

**Odoo Link:** http://localhost:8069/web#id={invoice_id}&model=account.move
```

### Phase 6 — Mark Source File as Processed
Original `WHATSAPP_*.md` file mein `status: pending` ko `status: processed` se replace karo
(file ko move mat karo — connector.py automatically Done/ mein move karega)

### Phase 7 — Wait for Human Approval (HITL)
User ko batao:
```
✅ Invoice draft created in Odoo (ID: {invoice_id})
📋 Customer: {customer_name} | Amount: {amount}
📄 Approval file: Plans/INVOICE_APPROVAL_{timestamp}.md
⏳ Next: Move the approval file to Approved/ to post invoice + send email
```

### Phase 8 — When Approved (Approval file moved to Approved/)
Yeh step connector.py automatically handle karta hai (loop mein).
Manual trigger ke liye user `/whatsapp-odoo-connector` dobara chalaye.

1. `Approved/INVOICE_APPROVAL_*.md` files scan karo
2. `status: pending_approval` wali files lo
3. Front matter se `invoice_id` nikalo
4. `confirm_invoice` call karo us `invoice_id` se
5. Agar `customer_email` available hai → email bhejo:
   - Subject: "Invoice #{invoice_id} - Payment Details"
   - Body: professional invoice notification
6. Approval file ko `Done/` mein move karo (rename: `DONE_INVOICE_...`)
7. Original `WHATSAPP_*.md` ko bhi `Done/` mein move karo

---

## Rules
- Kabhi bhi invoice automatically confirm mat karo — hamesha `Approved/` ka wait karo
- Agar amount message mein nahi mila → approval file mein `amount: UNKNOWN` likho aur user se puchho
- Agar customer email nahi pata → email step skip karo, log mein note karo
- Har action `Logs/YYYY-MM-DD.md` mein record karo
- Sensitive financial amounts (>50,000) pe extra note likho approval file mein

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Amount not found in message | `amount: UNKNOWN` likho, user se puchho |
| Customer create fails | Log karo, user ko notify karo |
| Invoice create fails | Log karo, original file status reset karo |
| Email not available | Skip email, log note karo |
| Odoo not running | `docker start odoo-db odoo-ai-employee` suggest karo |

---

## Log Format
Har action ke baad `Logs/YYYY-MM-DD.md` mein append karo:
```
[HH:MM] whatsapp-odoo-connector: {action} | file={filename} | customer={name} | invoice_id={id}
```
