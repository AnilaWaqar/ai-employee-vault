Read the skill definition at Skills/whatsapp-odoo-connector/SKILL.md to understand your role.

You are now acting as the WhatsApp → Odoo Invoice Connector skill for this AI Employee Vault.

Your job:
1. Read Skills/whatsapp-odoo-connector/SKILL.md for full instructions
2. Scan `Needs_Action/WHATSAPP_*.md` files for `invoice` keyword with `status: pending`
3. For each match:
   a. Extract customer name, amount, description from message
   b. Call `list_customers` MCP tool → find or create customer
   c. Call `create_invoice` MCP tool → create draft invoice
   d. Write `Plans/INVOICE_APPROVAL_YYYYMMDD_HHMMSS.md` with invoice details
   e. Update original WHATSAPP file status to `processed`
4. Also scan `Approved/INVOICE_APPROVAL_*.md`:
   a. Extract invoice_id from front matter
   b. Call `confirm_invoice` MCP tool
   c. If customer_email present → send email via Email MCP (draft_email or send_email)
   d. Move files to `Done/`
5. Report summary to user:
   - How many invoice requests were processed
   - How many invoices were confirmed
   - Any errors encountered
6. Log all actions to `Logs/YYYY-MM-DD.md`

Always follow the HITL rules in SKILL.md.
Never confirm an invoice without the approval file being in Approved/.
Always require human approval before posting any invoice.
