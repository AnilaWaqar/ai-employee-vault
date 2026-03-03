# Personal AI Employee — Silver Tier
## Spec-Kit Specification Document

**Version:** 1.0.0
**Platform:** Windows
**Vault:** `E:/HC/AI_Employee_Vault`
**Builds On:** Bronze Tier (Completed)
**Purpose:** spec-kit / specify-cli input file

---

## How To Use This File

Feed this file directly into spec-kit:

```bash
# Option 1: specify-cli
specify-cli generate --spec SILVER_TIER.md

# Option 2: Claude Code
# Open vault in terminal then say:
# "Read SILVER_TIER.md and implement Feature 1"

# Option 3: One feature at a time
# "Implement the WhatsApp Watcher from SILVER_TIER.md"
```

---

## Project Context

### What Is Already Built (Bronze — Complete)

The Bronze foundation is complete and working. Do not
rebuild or modify these. Only extend them.

- Obsidian Vault at `E:/HC/AI_Employee_Vault`
- `Dashboard.md` — live status file
- `Company_Handbook.md` — AI rules file
- `Gmail Watcher` — running via Python, monitors unread emails
- Folder structure: `/Needs_Action`, `/Plans`, `/Done`, `/Logs`
- Agent Skills: `gmail-watcher`, `inbox-processor`, `dashboard-updater`

### What Silver Tier Must Add

Six new features on top of Bronze. Each feature is
self-contained. Build them in order: 1 → 2 → 3 → 4 → 5 → 6.

---

## Feature 1 — WhatsApp Watcher

### Goal
Monitor WhatsApp Web continuously. When a message
containing a business keyword arrives, create a
structured Markdown file in `/Needs_Action/` so
Claude can process it.

### File To Create
`Skills/whatsapp-watcher/scripts/whatsapp_watcher.py`

### Behavior
- Use Playwright with a persistent Chromium context
- Save browser session to `whatsapp_session/` so QR
  code only needs scanning once
- Check for new unread messages every 60 seconds
- Match messages against this keyword list:
  `urgent, asap, emergency, invoice, payment, quote,
  meeting, deadline, schedule, help, issue, problem,
  project, task, delivery`
- For each keyword match, create one action file
- Skip messages already processed (track by sender+text ID)
- Never send any message automatically
- Run continuously in a while True loop
- Log every action to `/Logs/whatsapp_watcher.log`

### Output File Format
Create at: `/Needs_Action/WHATSAPP_YYYYMMDD_HHMMSS.md`

```
---
type: whatsapp_message
from: SENDER_NAME
received: ISO_TIMESTAMP
keywords_found: urgent, invoice
priority: high
status: pending
requires_approval: true
---

## Message Content
FULL_MESSAGE_TEXT

## Detected Keywords
`urgent`, `invoice`

## Priority
HIGH PRIORITY

## Suggested Actions
- [ ] Read and respond to message
- [ ] Generate invoice if requested
- [ ] Mark as priority if urgent
```

### Priority Logic
If keywords include `urgent`, `asap`, or `emergency`
then priority is `high`. Otherwise priority is `normal`.

### Rate Limiting
Maximum 20 action files per hour. If limit reached,
log a warning and skip until next hour.

### Environment Variables Needed
Read from `.env` file in vault root:

```
VAULT_PATH=E:/HC/AI_Employee_Vault
CHECK_INTERVAL=60
DRY_RUN=false
MAX_ACTIONS_PER_HOUR=20
```

If `DRY_RUN=true`, log what would happen but create
no files and send nothing.

### SKILL.md To Create
Create at: `Skills/whatsapp-watcher/SKILL.md`

```
---
name: whatsapp-watcher
description: Monitor WhatsApp Web for business-critical
messages containing keywords like urgent, invoice,
payment, help, deadline. Creates action files in
/Needs_Action automatically. Always use this skill
when WhatsApp monitoring, client message detection,
or business alert automation is needed.
---
```

### Install Commands
```bash
pip install playwright python-dotenv
playwright install chromium
```

### Success Criteria
- Script runs without crashing
- QR scan works on first run, auto-login after that
- Send test WhatsApp "urgent invoice needed"
- File appears in `/Needs_Action/WHATSAPP_*.md`
- File contains correct sender, keywords, priority
- Log entry written to `/Logs/whatsapp_watcher.log`

---

## Feature 2 — Email MCP Server

### Goal
Give Claude Code the ability to send emails via Gmail
after human approval. Expose email tools through the
Model Context Protocol so Claude can call them directly.

### Files To Create

```
email-mcp/
├── index.js        ← MCP server entry point
├── package.json    ← Node.js dependencies
└── .env            ← Gmail credentials (never commit)
```

### MCP Tools To Expose

**Tool 1: send_email**
- Inputs: `to`, `subject`, `body`, `attachment` (optional)
- Behavior: Send email via Gmail SMTP
- Requires: Approved file must exist before calling
- Dry run: If `DRY_RUN=true`, log and return success
  without sending

**Tool 2: draft_email**
- Inputs: `to`, `subject`, `body`
- Behavior: Save draft to `/Plans/DRAFT_*.md`
- No approval needed for drafts

**Tool 3: search_emails**
- Inputs: `query`, `max_results` (default 10)
- Behavior: Search Gmail and return results
- No approval needed for reading

### package.json Dependencies
```
@modelcontextprotocol/sdk — latest
nodemailer — ^6.9.0
dotenv — ^16.0.0
```

### Claude Code Config
Create or update `~/.config/claude-code/mcp.json`:

```
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["E:/HC/AI_Employee_Vault/email-mcp/index.js"],
      "env": {
        "GMAIL_USER": "your@gmail.com",
        "GMAIL_APP_PASSWORD": "your-app-password",
        "DRY_RUN": "false"
      }
    }
  ]
}
```

### How To Get Gmail App Password
1. Go to Google Account Settings
2. Security → 2-Step Verification → App Passwords
3. Generate password for "Mail"
4. Paste into `GMAIL_APP_PASSWORD`

### SKILL.md To Create
Create at: `Skills/email-mcp/SKILL.md`

```
---
name: email-mcp
description: Send, draft, and search emails via Gmail
using the Email MCP server. Use this skill whenever
Claude needs to send an email, create an email draft,
or search inbox. Always requires human approval before
sending. Never sends without /Approved/ file present.
---
```

### Success Criteria
- `node email-mcp/index.js` starts without errors
- Claude Code connects to MCP server
- `DRY_RUN=true` test logs email without sending
- `DRY_RUN=false` test delivers real email
- Audit log entry written after each action

---

## Feature 3 — LinkedIn Auto-Poster

### Goal
Allow Claude to draft LinkedIn posts and post them
after human approval. Never post without explicit
human approval via file movement.

### Files To Create

```
Skills/linkedin-poster/
├── SKILL.md
└── scripts/
    └── linkedin_poster.py
```

### Behavior
- Use Playwright with persistent Chromium context
- Save session to `linkedin_session/`
- Claude writes post content and creates approval file
- After human moves file to `/Approved/`, script posts
- Never auto-post under any circumstance
- Log every post attempt to audit log
- Support `DRY_RUN=true` mode

### Approval File Format
Claude creates at:
`/Pending_Approval/LINKEDIN_YYYYMMDD_HHMMSS.md`

```
---
type: approval_request
action: linkedin_post
content_preview: FIRST_100_CHARS
created: ISO_TIMESTAMP
expires: ISO_TIMESTAMP_PLUS_24H
status: pending
---

## Post Content
FULL_POST_CONTENT_HERE

## To APPROVE
Move this file to /Approved/ folder

## To REJECT
Move this file to /Rejected/ folder
```

### Post Steps (After Approval)
1. Open `linkedin.com/feed` via Playwright
2. Click the post creation button
3. Type the approved content
4. If `DRY_RUN=false` click post button
5. Log result to audit log
6. Move task to `/Done/`

### SKILL.md To Create
Create at: `Skills/linkedin-poster/SKILL.md`

```
---
name: linkedin-poster
description: Draft and post business content to LinkedIn
with human approval. Use this skill for LinkedIn
automation, business posting, content scheduling,
and social media management. Always creates approval
request first. Never posts without human confirmation.
---
```

### Success Criteria
- LinkedIn session saves on first login
- Claude creates approval file correctly
- Moving to `/Approved/` triggers post
- Moving to `/Rejected/` cancels post
- Post appears on LinkedIn profile
- Audit log entry created

---

## Feature 4 — HITL Approval Workflow

### Goal
Build the complete Human-in-the-Loop system. Claude
writes approval requests. Human moves files to act.
Orchestrator watches folders and executes actions.

### New Folders To Create

```
/Pending_Approval/    ← Claude writes here
/Approved/            ← Human moves here to approve
/Rejected/            ← Human moves here to reject
```

### File To Create
`orchestrator.py` in vault root

### Orchestrator Behavior
- Watch `/Approved/` folder every 30 seconds
- When a file appears in `/Approved/`:
  - Read the file type (email / linkedin / whatsapp_reply)
  - Call the correct MCP or script to execute action
  - Move original files to `/Done/`
  - Write audit log entry
  - Update `Dashboard.md`
- Watch `/Rejected/` folder every 30 seconds
- When a file appears in `/Rejected/`:
  - Log the rejection
  - Move to `/Done/` with rejected status
  - Update `Dashboard.md`

### Approval File Types To Handle

**Email Send:**
```
type: approval_request
action: send_email
to: EMAIL_ADDRESS
subject: SUBJECT_LINE
body: EMAIL_BODY
```

**LinkedIn Post:**
```
type: approval_request
action: linkedin_post
content: POST_CONTENT
```

**WhatsApp Reply:**
```
type: approval_request
action: whatsapp_reply
to: SENDER_NAME
message: REPLY_TEXT
```

### Expiry Rule
If file stays in `/Pending_Approval/` for more than
24 hours without being moved, mark it as expired,
log it, and move to `/Done/` with status `expired`.

### SKILL.md To Create
Create at: `Skills/hitl-workflow/SKILL.md`

```
---
name: hitl-workflow
description: Human-in-the-loop approval system for
sensitive actions. Creates approval request files
for email sends, LinkedIn posts, and WhatsApp replies.
Use whenever an action requires human confirmation
before execution. Move file to /Approved/ to proceed
or /Rejected/ to cancel.
---
```

### Success Criteria
- Orchestrator starts without errors
- Email approval file → move to `/Approved/` → email sent
- LinkedIn approval file → move to `/Approved/` → post created
- Move to `/Rejected/` → action cancelled, logged
- Files older than 24 hours → auto-expired
- Dashboard updated after every action

---

## Feature 5 — Plan Creator (Claude Reasoning Loop)

### Goal
When Claude reads a file in `/Needs_Action/`, it must
automatically create a structured `Plan.md` file in
`/Plans/` with step-by-step checkboxes and determine
if human approval is needed.

### SKILL.md To Create
Create at: `Skills/plan-creator/SKILL.md`

```
---
name: plan-creator
description: Read files in /Needs_Action/ and create
structured Plan.md files in /Plans/ with checkboxes.
Always reads Company_Handbook.md for rules. Creates
approval requests for sensitive actions. Use whenever
inbox processing, task planning, or reasoning about
a new action file is needed.
---

# Plan Creator

## Steps
1. Read all unprocessed files in /Needs_Action/
2. Read Company_Handbook.md for rules
3. Identify task type: email / whatsapp / file_drop
4. Create /Plans/PLAN_TIMESTAMP.md with this format:
   ---
   created: ISO_TIMESTAMP
   status: in_progress
   triggered_by: FILENAME
   ---
   ## Objective
   ONE SENTENCE GOAL
   ## Steps
   - [x] Identified task type
   - [x] Read handbook rules
   - [ ] Draft response or action
   - [ ] Create approval request if needed
   - [ ] Move to /Done/ when complete
   ## Approval Required
   yes / no — reason here
5. If action is sensitive → create /Pending_Approval/ file
6. Update Dashboard.md
7. Mark task as processed

## Rules
- Always follow Company_Handbook.md
- Never send anything without /Approved/ file
- Always create Plan.md before taking any action
- Log every step to /Logs/
```

### Success Criteria
- Claude reads `/Needs_Action/` file
- `Plan.md` created in `/Plans/` automatically
- Approval file created when action is sensitive
- Dashboard updated after processing

---

## Feature 6 — PM2 + Task Scheduler Setup

### Goal
Keep all watcher scripts running 24/7 on Windows.
Auto-restart on crash. Auto-start on PC reboot.
Add scheduled tasks for daily briefing.

### PM2 Setup (Process Management)

Install and configure PM2 for always-on watchers:

```bash
npm install -g pm2

pm2 start Skills/gmail-watcher/scripts/gmail_watcher.py \
  --interpreter python3 \
  --name gmail-watcher \
  --cwd E:/HC/AI_Employee_Vault

pm2 start Skills/whatsapp-watcher/scripts/whatsapp_watcher.py \
  --interpreter python3 \
  --name whatsapp-watcher \
  --cwd E:/HC/AI_Employee_Vault

pm2 start orchestrator.py \
  --interpreter python3 \
  --name hitl-orchestrator \
  --cwd E:/HC/AI_Employee_Vault

pm2 save
pm2 startup
```

### Windows Task Scheduler (Scheduled Tasks)

Create these two scheduled tasks:

**Task 1 — Daily Briefing**
- Name: `AI-Employee-Daily-Briefing`
- Trigger: Every day at 8:00 AM
- Action: Run `claude --skill dashboard-updater`
- Working Directory: `E:/HC/AI_Employee_Vault`

**Task 2 — Weekly Audit**
- Name: `AI-Employee-Weekly-Audit`
- Trigger: Every Sunday at 10:00 PM
- Action: Run `claude --skill weekly-auditor`
- Working Directory: `E:/HC/AI_Employee_Vault`

Create via PowerShell:

```powershell
# Daily Briefing Task
$action = New-ScheduledTaskAction `
  -Execute "claude" `
  -Argument "--skill dashboard-updater" `
  -WorkingDirectory "E:\HC\AI_Employee_Vault"

$trigger = New-ScheduledTaskTrigger `
  -Daily -At "08:00AM"

Register-ScheduledTask `
  -TaskName "AI-Employee-Daily-Briefing" `
  -Action $action `
  -Trigger $trigger `
  -RunLevel Highest
```

### SKILL.md To Create
Create at: `Skills/orchestrator/SKILL.md`

```
---
name: orchestrator
description: Manage all running processes for the
AI Employee system. Start, stop, restart watchers
via PM2. Setup Windows Task Scheduler for timed
tasks. Use when process management, scheduling,
or system health monitoring is needed.
---
```

### Success Criteria
- `pm2 list` shows all 3 processes as `online`
- Kill a watcher manually → PM2 restarts it in 5 seconds
- Restart PC → all watchers start automatically
- Task Scheduler shows both tasks as active
- Daily briefing runs at 8AM

---

## Complete Folder Structure After Silver

```
E:/HC/AI_Employee_Vault/
│
├── .env                          ← secrets (never commit)
├── .gitignore                    ← excludes .env, sessions
├── Dashboard.md                  ← live status (Bronze)
├── Company_Handbook.md           ← AI rules (Bronze)
├── Business_Goals.md             ← targets
├── orchestrator.py               ← NEW Feature 4
├── SILVER_TIER.md                ← this file
│
├── Needs_Action/                 ← watchers write here
├── Plans/                        ← Claude writes plans
├── Pending_Approval/             ← awaiting review
├── Approved/                     ← human approved
├── Rejected/                     ← human rejected
├── Done/                         ← completed tasks
├── Logs/                         ← audit trail
│
├── whatsapp_session/             ← NEW Playwright session
├── linkedin_session/             ← NEW Playwright session
│
├── email-mcp/                    ← NEW MCP server
│   ├── index.js
│   ├── package.json
│   └── .env
│
└── Skills/
    ├── gmail-watcher/            ← Bronze
    ├── inbox-processor/          ← Bronze
    ├── dashboard-updater/        ← Bronze
    ├── whatsapp-watcher/         ← NEW Feature 1
    ├── email-mcp/                ← NEW Feature 2
    ├── linkedin-poster/          ← NEW Feature 3
    ├── hitl-workflow/            ← NEW Feature 4
    ├── plan-creator/             ← NEW Feature 5
    └── orchestrator/             ← NEW Feature 6
```

---

## Security Rules

Apply these rules to every file generated from this spec.

- Never store credentials in vault markdown files
- Never commit `.env` files to git
- Always read credentials from environment variables
- Always support `DRY_RUN=true` mode in every script
- Never auto-execute any external action without
  a corresponding file in `/Approved/`
- Log every action to `/Logs/YYYY-MM-DD.json` with:
  `timestamp, action_type, actor, target, result, dry_run`
- Rate limit all watchers to max 20 actions per hour
- Expire approval requests after 24 hours

---

## .gitignore File Content

Create `.gitignore` in vault root with:

```
.env
email-mcp/.env
whatsapp_session/
linkedin_session/
Logs/
*.log
__pycache__/
node_modules/
*.pyc
.DS_Store
```

---

## .env Template

Create `.env` in vault root with:

```
VAULT_PATH=E:/HC/AI_Employee_Vault
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=your-app-password
DRY_RUN=false
CHECK_INTERVAL=60
MAX_ACTIONS_PER_HOUR=20
```

---

## Hackathon Requirements Coverage

This spec covers all 8 official Silver tier requirements:

- Two or more Watchers → Gmail (Bronze) + WhatsApp (Feature 1)
- LinkedIn posting → Feature 3
- Claude reasoning loop + Plan.md → Feature 5
- One working MCP server → Feature 2 (Email MCP)
- Human-in-the-loop workflow → Feature 4
- Basic scheduling → Feature 6 (Task Scheduler)
- All Bronze requirements → Already complete
- All AI as Agent Skills → Every feature
