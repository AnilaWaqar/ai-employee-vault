---
name: inbox-processor
description: /Needs_Action folder scan karo,
  files process karo aur /Done mein move karo.
  Use karo jab Claude ko inbox process karwana ho.
---

# Inbox Processor

## Overview
Yeh skill /Needs_Action folder ki files padhti hai,
Claude se process karaati hai aur /Done mein move karti hai.

## Steps

### EMAIL files (EMAIL_*.md):
1. /Needs_Action folder scan karo
2. Har EMAIL_*.md file padhon
3. Company_Handbook.md ke email rules check karo
4. Sensitive → /Pending_Approval/APPROVAL_REQUIRED_{filename}
5. Safe → /Plans/ mein Plan.md + /Drafts/ mein DRAFT_*.md banao
6. Original → /Done/ mein move karo
7. Dashboard.md update karo
8. Har action /Logs/ mein record karo

### WHATSAPP files (WHATSAPP_*.md):
1. /Needs_Action folder scan karo
2. Har WHATSAPP_*.md file padhon
3. Priority check karo (header mein `priority:` field)
4. Company_Handbook.md ke WhatsApp rules check karo:
   - `priority: high` (urgent/asap/emergency) → /Pending_Approval/WHATSAPP_URGENT_{filename}
   - `priority: normal` with business keywords → /Drafts/WHATSAPP_DRAFT_{timestamp}_{sender}.md
   - Group info / no clear ask → directly /Done/ mein archive
5. Original WHATSAPP file → /Done/ mein move karo
6. Dashboard.md update karo
7. Har action /Logs/ mein record karo

## Rules
- Company_Handbook.md hamesha follow karo (email + WhatsApp dono sections)
- Sensitive/HIGH priority WhatsApp → /Pending_Approval/ (human khud respond kare)
- WhatsApp drafts WHATSAPP_DRAFT format mein hone chahiye (Company_Handbook.md dekho)
- Kabhi bhi WhatsApp pe auto-reply mat karo — sirf draft/suggestion banao
- Har action /Logs/ mein record karo
