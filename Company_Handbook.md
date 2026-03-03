---
version: 1.0.0
last_updated: 2026-01-14
owner: AI Employee
type: configuration
---

# Company Handbook: Email Processing Rules

This document defines how the AI Employee categorizes emails and selects response templates.

## Email Categorization Rules

### Priority Levels

**HIGH Priority** - Requires immediate attention (same day):
- Keywords: urgent, asap, deadline, critical, emergency, important
- From: Known client domains
- Labels: urgent, important, clients
- Time-sensitive requests with explicit deadlines

**MEDIUM Priority** - Requires attention within 1-2 days:
- Keywords: project, proposal, meeting, schedule, invoice, payment
- From: Vendor domains, business contacts
- Labels: business, vendors, projects
- General business correspondence

**LOW Priority** - Can be handled within a week:
- Keywords: update, information, newsletter, announcement, fyi
- From: Newsletters, automated systems
- Labels: newsletters, updates, social
- Informational content, non-urgent updates

### Category Types

**client_request** - Client project or service requests:
- From known client domains or contacts
- Keywords: project, scope, requirements, deliverables, proposal
- Requires: Draft response with project acknowledgment

**vendor** - Vendor communications (invoices, quotes, services):
- From vendor domains
- Keywords: invoice, payment, quote, contract, service
- Requires: Draft acknowledgment or follow-up

**internal** - Internal team/organization communications:
- From company domain
- Keywords: meeting, update, team, review, status
- Requires: Quick acknowledgment or action

**urgent** - Time-critical communications:
- Contains deadline language
- Keywords: urgent, asap, critical, emergency, deadline today
- Requires: Immediate attention flag

**newsletter** - Newsletters and automated updates:
- From known newsletter senders (unsubscribe link present)
- Keywords: newsletter, unsubscribe, subscription, digest
- Requires: Low priority, archive after review

**other** - Uncategorized emails:
- Doesn't match above categories
- Requires: Manual review for categorization

## Auto-Categorization Rules (YAML Format)

```yaml
categorization_rules:
  high_priority_keywords:
    - urgent
    - asap
    - deadline
    - critical
    - emergency
    - important
    - help needed

  client_domains:
    - "@clientcompany.com"
    - "@startupname.io"
    # Add your client domains here

  vendor_domains:
    - "@stripe.com"
    - "@aws.amazon.com"
    - "@heroku.com"
    # Add your vendor domains here

  newsletter_indicators:
    - unsubscribe
    - "click here to unsubscribe"
    - newsletter
    - digest
    - subscription

  sensitive_keywords:
    - legal
    - lawsuit
    - complaint
    - violation
    - termination
    - confidential
    - password reset
    - security alert
```

## Response Templates

### Template 1: Client Project Request

**Use when**: Email requests project work, scope discussion, or proposal

**Template**:
```
Subject: Re: [Original Subject]

Hi [Client Name],

Thank you for reaching out regarding [Project Topic].

I've received your request and I'm excited to discuss this further. Based on your email, I understand you're looking for [FILL IN: brief project summary].

To provide you with an accurate scope and timeline, I'd like to clarify a few points:
- [FILL IN: clarification question 1]
- [FILL IN: clarification question 2]
- [FILL IN: timeline expectations]

I'm available for a call this week to discuss the details. What time works best for you?

Looking forward to working together on this.

Best regards,
[Your Name]
```

### Template 2: Invoice Request

**Use when**: Client requests invoice or payment information

**Template**:
```
Subject: Re: [Original Subject]

Hi [Client Name],

Thank you for your email regarding the invoice.

I'll prepare the invoice for [FILL IN: project/service description] and send it to you by [FILL IN: date, typically within 24 hours].

The invoice will include:
- [FILL IN: itemized services]
- Total amount: [FILL IN: amount]
- Payment terms: [FILL IN: terms, e.g., Net 30]

Please let me know if you need any additional information or if you have specific invoicing requirements.

Best regards,
[Your Name]
```

### Template 3: Meeting Confirmation

**Use when**: Scheduling or confirming a meeting

**Template**:
```
Subject: Re: [Original Subject]

Hi [Name],

Thank you for suggesting a meeting to discuss [FILL IN: meeting topic].

I'm available on:
- [FILL IN: date/time option 1]
- [FILL IN: date/time option 2]
- [FILL IN: date/time option 3]

Please let me know which time works best for you, or suggest an alternative if none of these fit your schedule.

I'll send a calendar invite once we confirm the time.

Looking forward to our conversation.

Best regards,
[Your Name]
```

### Template 4: Polite Decline

**Use when**: Need to decline a request or opportunity

**Template**:
```
Subject: Re: [Original Subject]

Hi [Name],

Thank you for thinking of me for [FILL IN: opportunity/request].

Unfortunately, I'm not able to [FILL IN: take on this project/attend/participate] at this time due to [FILL IN: reason - workload/schedule/priorities].

I appreciate you reaching out, and I hope we can connect on future opportunities.

Best regards,
[Your Name]
```

### Template 5: Acknowledgment (Generic)

**Use when**: Need to acknowledge receipt but require more time to respond

**Template**:
```
Subject: Re: [Original Subject]

Hi [Name],

Thank you for your email regarding [FILL IN: topic].

I've received your message and I'm reviewing the details. I'll get back to you with a full response by [FILL IN: specific date/timeframe].

If this is urgent, please let me know and I'll prioritize accordingly.

Best regards,
[Your Name]
```

## Never Auto-Draft For (Require Manual Handling)

The AI Employee will **NOT** generate drafts for emails containing these sensitive topics:

- Legal matters (lawsuit, legal notice, complaint, violation)
- HR issues (termination, disciplinary action, harassment)
- Security alerts (password reset, account compromise, breach)
- Financial disputes (refund disputes, payment issues, fraud)
- Personal matters (health, family, personal emergency)
- Confidential information requests

**Action**: Flag these emails as "Requires Manual Review" with HIGH priority.

## Logging Rules

Log the following to daily log files (Logs/YYYY-MM-DD.md):

**For each email processed**:
- Timestamp (HH:MM:SS)
- Email ID
- From (name and email)
- Subject
- Priority assigned (high/medium/low)
- Category assigned
- Action taken (task created, draft generated, flagged for review)
- Duration (seconds)

**Example log entry**:
```
### 14:30:25 - Email Detected
- **Email ID**: EMAIL_20260114T143025_a3f2
- **From**: John Client <john@clientcompany.com>
- **Subject**: Urgent: Project Timeline
- **Priority**: high
- **Category**: client_request
- **Action**: Task created in Needs_Action/
- **Duration**: 1.2s
```

---

## Customization Instructions

**To customize this handbook**:

1. **Update client domains**: Add your actual client email domains to the YAML block
2. **Update vendor domains**: Add your regular vendor domains
3. **Modify templates**: Adjust response templates to match your communication style
4. **Add categories**: Create new categories if your workflow needs them
5. **Adjust priorities**: Modify priority keywords based on your business needs

**After updating**:
- Save this file
- The AI Employee will automatically use the updated rules
- Test with sample emails to verify categorization works correctly

---

---

## WhatsApp Processing Rules

### WhatsApp Message Categorization

**HIGH Priority → Pending_Approval/** (human must respond manually):
- Keywords: urgent, asap, emergency
- Reason: Real-time chat — aadmi khud jawab de

**NORMAL Priority → Drafts/WHATSAPP_DRAFT_*.md** (suggested reply):
- Keywords: invoice, payment, meeting, schedule, deadline, quote, project, task, delivery
- Reply suggestion banao, human approve kare

**INFO Only → Done/** (archive, no reply needed):
- Group messages with no direct question
- Announcements, broadcasts, FYI messages
- Preview without clear ask

### WhatsApp Reply Templates

**WT-1: Urgent Acknowledgment** (HIGH priority, human-drafted):
```
Haan, abhi dekh raha/rahi hoon. 2 minute mein respond karti/karta hoon.
```
*(Sirf suggestion — human approve karke khud bheje)*

**WT-2: Meeting/Schedule Request**:
```
Haan bilkul. Meri availability:
- [FILL IN: din/time 1]
- [FILL IN: din/time 2]
Batao kya suit karta hai.
```

**WT-3: Invoice/Payment**:
```
Invoice ready kar raha/rahi hoon. Aaj kal mein bhej deta/deti hoon.
Details:
- [FILL IN: service description]
- Amount: [FILL IN]
```

**WT-4: Project/Task Update**:
```
Update: [FILL IN — kya hua, kya bacha hai]
Koi aur cheez chahiye? Batao.
```

**WT-5: Deadline Info**:
```
Theek hai, note kar liya. Deadline: [FILL IN].
[FILL IN: koi action needed?]
```

**WT-6: Generic Acknowledgment**:
```
Theek hai, samajh gaya/gayi. [FILL IN — specific response]
```

### WhatsApp Draft File Format

Save to `Drafts/WHATSAPP_DRAFT_{timestamp}_{sender_slug}.md`:

```markdown
---
type: whatsapp_draft
original_file: WHATSAPP_{timestamp}.md
from: {sender}
priority: {high/normal}
template_used: {WT-1 etc.}
status: ready_for_review
generated_at: {date}
---

# WhatsApp Reply Suggestion

**To:** {sender}
**Re:** {message preview}

---

{reply text here}

---
> Review Note: {any special note}
```

### WhatsApp Logging

Log har WhatsApp action:
```
### HH:MM:SS - WhatsApp Message
- From: {sender}
- Keywords: {keywords}
- Priority: {high/normal/info}
- Action: → Pending_Approval / Draft created / Archived
```

---

**Version History**:
- v1.0.0 (2026-01-14): Initial handbook template for Bronze Tier
- v1.1.0 (2026-02-27): WhatsApp processing rules added (Silver Tier)
