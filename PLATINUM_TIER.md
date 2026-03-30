# Personal AI Employee — Platinum Tier
# Spec-Kit Specification Document
# Format: Pure Markdown for spec-kit / specify-cli

---

## How To Use This File

```bash
# One phase at a time — recommended approach
# Open vault in terminal, then say:
"Read platinum-tier-speckit.md and implement Phase 1"

# After testing Phase 1:
"Read platinum-tier-speckit.md and implement Phase 2"

# To create a new Agent Skill:
"Read platinum-tier-speckit.md and create the Skill for Phase 5"

# To use Skill Creator pattern:
"Read platinum-tier-speckit.md, use skill-creator pattern
to build and test the cloud-agent-skill"
```

---

## Project Context

### Already Complete — Do Not Rebuild

```
Bronze Tier:
  Obsidian Vault — E:/HC/AI_Employee_Vault
  Gmail Watcher (gmail_watcher.py)
  Dashboard.md + Company_Handbook.md
  inbox-processor skill
  dashboard-updater skill
  Folder: /Needs_Action, /Plans, /Done, /Logs

Silver Tier:
  WhatsApp Watcher (whatsapp_watcher.py)
  Email MCP Server
  LinkedIn Auto-Poster
  HITL Approval Workflow
  Folders: /Pending_Approval, /Approved, /Rejected
  Plan Creator Skill
  PM2 + Windows Task Scheduler
  orchestrator.py

Gold Tier:
  Odoo Community (Docker, localhost:8069)
  Odoo MCP Server
  Facebook + Instagram Playwright poster
  Twitter/X Watcher
  CEO Briefing Skill (weekly audit)
  Ralph Wiggum Loop (Stop hook)
  Watchdog + Error Recovery
  Enhanced Audit Logging (/Logs/YYYY-MM-DD.json)
  Full Gold documentation
```

### What Platinum Tier Must Add

Eight phases on top of Gold. Build in order: 1 to 8.
Each phase depends on the previous being complete and tested.

---

## Skill Creator Pattern — Use For Every Feature

Every Platinum feature must follow this pattern when
creating Agent Skills. Based on official skill-creator
methodology from /mnt/skills/examples/skill-creator/SKILL.md

### How To Create Every New Skill

```
Step 1 — Write SKILL.md draft:
  - YAML frontmatter (name + description)
  - Trigger phrases in description (be "pushy")
  - Step by step instructions (imperative form)
  - Output format definition
  - Rules and constraints
  - Keep under 500 lines

Step 2 — Write test cases in evals/evals.json:
  {
    "skill_name": "skill-name",
    "evals": [
      {
        "id": 1,
        "prompt": "realistic user prompt",
        "assertions": [
          {
            "type": "contains",
            "value": "expected output keyword"
          }
        ]
      }
    ]
  }

Step 3 — Run 2-3 test prompts, evaluate results

Step 4 — Improve SKILL.md based on test results

Step 5 — Save final SKILL.md to:
  E:/HC/AI_Employee_Vault/Skills/skill-name/SKILL.md
```

### SKILL.md Template (Use For Every New Skill)

```markdown
---
name: skill-name
description: >
  WHAT it does AND WHEN to use it.
  Include trigger phrases explicitly.
  Be "pushy" — list all contexts where this should trigger.
  Example: "Use this skill whenever user mentions cloud,
  VM, deployment, AWS, EC2, or dual agent setup."
---

# Skill Name

## Purpose
One line — what this skill does.

## When To Use
- Trigger phrase 1
- Trigger phrase 2
- Context where this applies

## Steps
1. First action (imperative)
2. Second action
3. Third action

## Output Format
Describe exact output structure.

## Rules
- Rule 1
- Rule 2

## Error Handling
What to do when something fails.
```

---

## Platinum Vault — New Folder Structure

Add these folders on top of existing Gold structure:

```
E:/HC/AI_Employee_Vault/
│
├── [All Bronze + Silver + Gold folders — keep as is]
│
├── Needs_Action/
│   ├── email/          ← Cloud Agent likhta hai
│   ├── whatsapp/       ← Local Agent likhta hai
│   └── social/         ← Cloud Agent likhta hai
│
├── In_Progress/
│   ├── cloud/          ← Cloud ne claim kiya (NEW)
│   └── local/          ← Local ne claim kiya (NEW)
│
├── Updates/            ← Cloud writes here (NEW)
├── Signals/            ← Agent-to-agent comms (NEW)
│
└── Skills/             ← All Agent Skills folder
    ├── cloud-agent/
    ├── local-agent/
    ├── git-sync/
    ├── claim-by-move/
    ├── dual-dashboard/
    └── platinum-demo/
```

---

## Phase 1 — Cloud VM Setup (AWS Free Tier)

### Goal
Provision a free Ubuntu VM on AWS EC2 that stays
online 24/7. This VM will run the Cloud Agent.

### Note
AWS Free Tier = 750 hours/month EC2 t2.micro — FREE for 12 months.
After 12 months: ~$8-10/month.

### Estimated Time
3–4 hours

### Steps

```
1. AWS Console mein login karo
   URL: console.aws.amazon.com

2. EC2 Dashboard kholo
   Services → EC2 → Launch Instance

3. Instance configure karo:
   Name:             ai-employee-cloud
   AMI:              Ubuntu Server 22.04 LTS (64-bit x86)
   Instance Type:    t2.micro  ← Free Tier eligible
   Storage:          20 GB gp2 (free tier mein)

4. Key Pair banao (SSH ke liye):
   "Create new key pair" click karo
   Name:   aws_ai_employee
   Type:   ED25519
   Format: .pem (Linux/Mac) ya .ppk (PuTTY)
   Download hoga — sambhal ke rakho, dobara nahi milegi!
   Save karo: C:/Users/<you>/.ssh/aws_ai_employee.pem

5. Security Group configure karo (Firewall):
   Inbound Rules mein yeh add karo:
   ┌─────────┬──────────┬───────────────────────┐
   │ Type    │ Port     │ Source                │
   ├─────────┼──────────┼───────────────────────┤
   │ SSH     │ 22       │ My IP (sirf apna IP)  │
   │ Custom  │ 8069     │ My IP (Odoo)          │
   │ HTTPS   │ 443      │ 0.0.0.0/0             │
   └─────────┴──────────┴───────────────────────┘

6. Launch Instance karo
   "Launch Instance" button dabao
   EC2 Dashboard pe instance Running dikhega

7. Public IP copy karo
   Instance select karo → "Public IPv4 address" copy karo

8. SSH test karo (Windows Terminal ya Git Bash se):
   chmod 400 ~/.ssh/aws_ai_employee.pem
   ssh -i ~/.ssh/aws_ai_employee.pem ubuntu@<YOUR_EC2_IP>

9. .env mein save karo (local PC pe):
   CLOUD_VM_IP=<your EC2 public IP>
   CLOUD_VM_USER=ubuntu
   CLOUD_VM_KEY_PATH=~/.ssh/aws_ai_employee.pem
```

### Success Check

```bash
# Windows Git Bash se:
ssh -i ~/.ssh/aws_ai_employee.pem ubuntu@$CLOUD_VM_IP "echo VM_CONNECTED"
# Should print: VM_CONNECTED
```

### Elastic IP (Optional but Recommended)

```
EC2 Public IP har restart pe change ho jaata hai.
Fix karne ke liye Elastic IP assign karo (free jab attached ho):

EC2 Dashboard → Elastic IPs → Allocate Elastic IP
→ Associate with your instance
→ Ab IP kabhi nahi badlega
```

### Security Rules

```
Never put VM credentials in vault markdown files
Never commit .pem key to git
Store VM IP in local .env only
.pem file sirf local PC pe rakho
```

---

## Phase 2 — Cloud VM Configuration

### Goal
Install all required software on the AWS EC2 VM so the
Cloud Agent can run Python scripts and connect to Git.

### Estimated Time
2–3 hours

### Steps

```bash
# SSH into VM first:
ssh -i ~/.ssh/aws_ai_employee.pem ubuntu@$CLOUD_VM_IP

# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.13
sudo apt install -y python3.13 python3.13-pip python3-venv

# 3. Install Git
sudo apt install -y git

# 4. Install PM2 (process manager)
sudo apt install -y nodejs npm
sudo npm install -g pm2

# 5. Install Python packages
pip3 install google-auth google-auth-oauthlib google-api-python-client
pip3 install playwright python-dotenv watchdog requests

# 6. Clone vault repo (see Phase 3 for Git setup first)
git clone <your-vault-git-repo-url> ~/AI_Employee_Vault

# 7. Create Cloud .env
nano ~/AI_Employee_Vault/.env
# Add: GMAIL_CREDENTIALS_PATH, CLAUDE_API_KEY, etc.
# This .env NEVER syncs to git (add to .gitignore)
```

### PM2 Process Config

```javascript
// ecosystem.config.js — on Cloud VM
module.exports = {
  apps: [
    {
      name: 'cloud-gmail-watcher',
      script: 'gmail_watcher.py',
      interpreter: 'python3',
      cwd: '/home/ubuntu/AI_Employee_Vault',
      watch: false,
      restart_delay: 5000,
      env: { DRY_RUN: 'false' }
    },
    {
      name: 'cloud-orchestrator',
      script: 'cloud_orchestrator.py',
      interpreter: 'python3',
      cwd: '/home/ubuntu/AI_Employee_Vault',
      watch: ['Needs_Action/email', 'Approved'],
      restart_delay: 5000
    },
    {
      name: 'cloud-watchdog',
      script: 'watchdog.py',
      interpreter: 'python3',
      cwd: '/home/ubuntu/AI_Employee_Vault',
      restart_delay: 10000
    }
  ]
}
```

### Success Check

```bash
pm2 list
# Should show all 3 processes as "online"

pm2 logs cloud-gmail-watcher --lines 20
# Should show: "Starting GmailWatcher..."
```

---

## Phase 3 — Git Vault Sync

### Goal
Both Cloud VM and Local PC share the same Obsidian vault
via Git. Changes auto-sync every 5 minutes.

### Estimated Time
3–4 hours

### Steps

```
1. Create private GitHub repo:
   Name: ai-employee-vault-sync
   Visibility: Private
   Initialize: Yes (with README)

2. Add .gitignore to vault root:
```

```gitignore
# .gitignore — CRITICAL — never remove these
.env
*.env
.env.*
credentials.json
token.json
*.session
*.key
*.pem
whatsapp-session/
__pycache__/
*.pyc
.DS_Store
node_modules/
```

```
3. Push vault to GitHub (Local PC):
   cd E:/HC/AI_Employee_Vault
   git init
   git remote add origin https://github.com/<you>/ai-employee-vault-sync.git
   git add .
   git commit -m "Initial vault sync"
   git push -u origin main

4. Pull vault on Cloud VM:
   cd ~
   git clone https://github.com/<you>/ai-employee-vault-sync.git AI_Employee_Vault

5. Auto-sync script (runs every 5 minutes):
```

```python
# git_sync.py — runs on BOTH Cloud VM and Local PC
import subprocess
import time
import logging
from pathlib import Path

VAULT_PATH = Path("E:/HC/AI_Employee_Vault")  # Windows local
# VAULT_PATH = Path("/home/ubuntu/AI_Employee_Vault")  # Cloud VM

logger = logging.getLogger("git_sync")

def sync_vault():
    try:
        # Pull latest changes
        result = subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=VAULT_PATH,
            capture_output=True, text=True
        )
        if result.returncode != 0:
            logger.error(f"Pull failed: {result.stderr}")
            return

        # Check for local changes
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=VAULT_PATH,
            capture_output=True, text=True
        )

        if status.stdout.strip():
            # Local changes exist — commit and push
            subprocess.run(["git", "add", "."], cwd=VAULT_PATH)
            subprocess.run(
                ["git", "commit", "-m", f"Auto-sync {time.strftime('%Y-%m-%d %H:%M')}"],
                cwd=VAULT_PATH
            )
            subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=VAULT_PATH
            )
            logger.info("Vault synced to GitHub")

    except Exception as e:
        logger.error(f"Sync error: {e}")

if __name__ == "__main__":
    logger.info("Git sync started — every 5 minutes")
    while True:
        sync_vault()
        time.sleep(300)  # 5 minutes
```

### Sync Rules

```
SYNCS (markdown + state only):    NEVER SYNCS:
✅ /Needs_Action/*.md             ❌ .env
✅ /Plans/*.md                    ❌ credentials.json
✅ /Pending_Approval/*.md         ❌ token.json
✅ /Approved/*.md                 ❌ whatsapp-session/
✅ /Updates/*.md                  ❌ *.key / *.pem
✅ /Signals/*.md                  ❌ __pycache__/
✅ Dashboard.md                   ❌ Banking tokens
✅ /Done/*.md                     ❌ Payment credentials
✅ /Logs/*.md
```

### Success Check

```
1. Create test file on Local PC:
   E:/HC/AI_Employee_Vault/Updates/test-sync.md

2. Wait 5 minutes

3. SSH to Cloud VM:
   cat ~/AI_Employee_Vault/Updates/test-sync.md
   # File should be present

4. Delete test file and re-sync
```

### Agent Skill To Create

```
Skill: git-sync-skill
Purpose: Monitor sync status, detect conflicts, alert human
Trigger: "check sync status", "git sync failed", "vault not syncing"

SKILL.md steps:
  1. Run git status in vault
  2. Check last sync timestamp
  3. If conflict detected → write to /Signals/CONFLICT.md
  4. Alert human via Dashboard.md
  5. Never auto-resolve conflicts — always ask human
```

---

## Phase 4 — Cloud Agent (cloud_orchestrator.py)

### Goal
Cloud Agent runs 24/7 on Oracle VM. It watches for emails,
drafts replies, creates approval files — but NEVER sends
directly. All sends require Local Agent approval.

### Estimated Time
5–6 hours

### cloud_orchestrator.py Structure

```python
# cloud_orchestrator.py
import time
import logging
import shutil
from pathlib import Path
from datetime import datetime

VAULT = Path("/home/ubuntu/AI_Employee_Vault")
NEEDS_ACTION = VAULT / "Needs_Action" / "email"
IN_PROGRESS_CLOUD = VAULT / "In_Progress" / "cloud"
PENDING_APPROVAL = VAULT / "Pending_Approval"
UPDATES = VAULT / "Updates"
DONE = VAULT / "Done"

logger = logging.getLogger("cloud_orchestrator")

def claim_task(task_file: Path) -> bool:
    """Claim-by-move: first agent to move wins."""
    try:
        dest = IN_PROGRESS_CLOUD / task_file.name
        task_file.rename(dest)
        logger.info(f"Cloud claimed: {task_file.name}")
        return True
    except FileNotFoundError:
        logger.info(f"Already claimed by another agent: {task_file.name}")
        return False

def draft_reply(task_file: Path) -> str:
    """Call Claude API to draft email reply."""
    content = task_file.read_text()
    # Claude API call here — returns draft text
    # Use Anthropic Python SDK
    draft = f"[Cloud Draft] Reply to: {task_file.name}"
    return draft

def create_approval_file(task_file: Path, draft: str):
    """Write approval request for Local Agent."""
    approval_content = f"""---
type: approval_request
agent: cloud
action: email_send
task_ref: {task_file.name}
created: {datetime.now().isoformat()}
expires: 24h
status: pending
---

## Cloud Agent Draft Reply

{draft}

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
"""
    approval_file = PENDING_APPROVAL / f"CLOUD_{task_file.stem}_approval.md"
    approval_file.write_text(approval_content)

    # Write update for Dashboard
    update = f"[{datetime.now().strftime('%H:%M')}] Cloud drafted reply for {task_file.name}\n"
    (UPDATES / "cloud_activity.md").open("a").write(update)

def process_tasks():
    """Main loop — check for new email tasks."""
    for task_file in NEEDS_ACTION.glob("EMAIL_*.md"):
        if claim_task(task_file):
            claimed = IN_PROGRESS_CLOUD / task_file.name
            draft = draft_reply(claimed)
            create_approval_file(claimed, draft)

def run():
    logger.info("Cloud Orchestrator started — 24/7 mode")
    while True:
        try:
            process_tasks()
        except Exception as e:
            logger.error(f"Error: {e}")
        time.sleep(120)  # Check every 2 minutes

if __name__ == "__main__":
    run()
```

### Cloud Agent Rules

```
Cloud OWNS:                       Cloud NEVER does:
✅ Email triage                   ❌ Send emails directly
✅ Draft replies                  ❌ Post on social media
✅ Social post drafting           ❌ Access WhatsApp
✅ Write to /Updates/             ❌ Make payments
✅ Write to /Pending_Approval/    ❌ Access banking
✅ Write to /Signals/             ❌ Update Dashboard.md
✅ Claim tasks via claim-by-move  ❌ Sync secrets
```

### Claim-By-Move Rule (Critical)

```
Rule: First agent to move file from
      /Needs_Action/<domain>/ to /In_Progress/<agent>/
      becomes the owner. Other agents MUST ignore.

Python implementation:
  try:
      task_file.rename(IN_PROGRESS_CLOUD / task_file.name)
      # Success = we own it
  except FileNotFoundError:
      # Already moved by other agent = ignore
      pass
```

### Agent Skill To Create

```
Skill: cloud-agent-skill
Purpose: Monitor cloud agent health, check drafts, manage claims
Trigger: "cloud agent", "cloud drafts", "check cloud status",
         "what did cloud draft", "cloud offline", "cloud agent down"

SKILL.md steps:
  1. Check pm2 status on Cloud VM via SSH
  2. List files in /In_Progress/cloud/
  3. List files in /Pending_Approval/ with CLOUD_ prefix
  4. Report health status
  5. If unhealthy — write to /Signals/CLOUD_DOWN.md
  6. Alert human via Dashboard.md update
```

---

## Phase 5 — Odoo Cloud Deployment

### Goal
Move Odoo Community from localhost to Cloud VM with
HTTPS, daily backups, and health monitoring.
Cloud Agent drafts invoices. Local Agent posts them.

### Estimated Time
4–5 hours

### Steps

```bash
# SSH into Cloud VM
ssh -i ~/.ssh/oracle_vm ubuntu@$CLOUD_VM_IP

# 1. Install Docker on VM
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
newgrp docker

# 2. Create Odoo docker-compose on VM
mkdir -p ~/odoo && cd ~/odoo
```

```yaml
# docker-compose.yml — Cloud VM
version: '3.8'
services:
  odoo:
    image: odoo:17
    restart: always
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=${ODOO_DB_PASSWORD}
    volumes:
      - odoo-data:/var/lib/odoo
    depends_on:
      - db

  db:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=${ODOO_DB_PASSWORD}
      - POSTGRES_DB=postgres
    volumes:
      - pg-data:/var/lib/postgresql/data

volumes:
  odoo-data:
  pg-data:
```

```bash
# 3. Start Odoo on Cloud VM
cd ~/odoo
docker-compose up -d

# 4. Verify Odoo running
curl http://localhost:8069/web/health
# Should return: {"status": "pass"}

# 5. Setup HTTPS with Certbot (free SSL)
sudo apt install -y certbot nginx
sudo certbot --nginx -d yourdomain.com
# OR use self-signed for demo:
sudo openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout /etc/ssl/odoo.key \
  -out /etc/ssl/odoo.crt

# 6. Setup daily backup
crontab -e
# Add: 0 2 * * * docker exec odoo_db_1 pg_dump -U odoo postgres > ~/backups/odoo_$(date +%Y%m%d).sql
```

### Odoo MCP Rules (Platinum)

```
Cloud Agent via Odoo MCP:    Local Agent via Odoo MCP:
✅ Draft invoices             ✅ Post/confirm invoices
✅ Read customer list         ✅ Register payments
✅ Read product catalog       ✅ Send invoices to clients
✅ Create draft estimates     ✅ Cancel/credit notes
❌ Post invoices              ❌ N/A (Local owns posting)
❌ Register payments
```

### Success Check

```
From Local PC browser:
https://<VM_IP>:8069
Login with admin credentials
Create test draft invoice
Confirm Cloud Agent can see it via Odoo MCP
```

---

## Phase 6 — Local Agent (local_orchestrator.py)

### Goal
Local Agent runs on your PC. It watches for approved files
from Cloud Agent and executes final actions — send emails,
post social, update Dashboard.md.

### Estimated Time
4–5 hours

### local_orchestrator.py Structure

```python
# local_orchestrator.py — runs on your Windows PC
import time
import logging
import shutil
from pathlib import Path
from datetime import datetime

VAULT = Path("E:/HC/AI_Employee_Vault")
APPROVED = VAULT / "Approved"
IN_PROGRESS_LOCAL = VAULT / "In_Progress" / "local"
DONE = VAULT / "Done"
UPDATES = VAULT / "Updates"

logger = logging.getLogger("local_orchestrator")

def process_approved_files():
    """Watch /Approved/ for Cloud Agent approvals."""
    for approval_file in APPROVED.glob("CLOUD_*.md"):
        content = approval_file.read_text()

        # Move to in-progress
        dest = IN_PROGRESS_LOCAL / approval_file.name
        approval_file.rename(dest)

        # Parse action type from frontmatter
        if "action: email_send" in content:
            execute_email_send(dest, content)
        elif "action: social_post" in content:
            execute_social_post(dest, content)

        # Move to done
        done_dest = DONE / dest.name
        dest.rename(done_dest)

        # Update Dashboard
        update_dashboard(f"Local executed: {approval_file.name}")

def execute_email_send(task_file: Path, content: str):
    """Send email via Gmail MCP after Cloud drafted it."""
    logger.info(f"Sending email for: {task_file.name}")
    # Call Gmail MCP here
    # Log to /Logs/YYYY-MM-DD.json

def update_dashboard(message: str):
    """Local Agent is the only one who writes Dashboard.md"""
    dashboard = VAULT / "Dashboard.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Read existing, prepend new entry, write back

def run():
    logger.info("Local Orchestrator started")
    while True:
        try:
            process_approved_files()
        except Exception as e:
            logger.error(f"Error: {e}")
        time.sleep(60)  # Check every 1 minute

if __name__ == "__main__":
    run()
```

### Local Agent Rules

```
Local OWNS:                       Local NEVER does:
✅ Execute email sends             ❌ Email triage (Cloud owns)
✅ WhatsApp session + sends        ❌ Social drafting (Cloud owns)
✅ Execute social posts            ❌ Overwrite /Updates/ (Cloud's)
✅ Banking + payments              ❌ Claim Cloud's tasks
✅ Update Dashboard.md
✅ Merge /Updates/ into Dashboard
✅ Approve/Reject Cloud drafts
✅ Post Odoo invoices
```

### Agent Skill To Create

```
Skill: local-agent-skill
Purpose: Manage approvals, check pending items, execute actions
Trigger: "pending approvals", "local agent", "approve this",
         "what needs approval", "execute send", "process approved"

SKILL.md steps:
  1. List all files in /Pending_Approval/
  2. Show summary to human (from, subject, action)
  3. Wait for human to move file to /Approved or /Rejected
  4. On /Approved — trigger local_orchestrator.py
  5. Log result to /Logs/YYYY-MM-DD.json
  6. Update Dashboard.md
  7. Move task to /Done
```

---

## Phase 7 — Dual Dashboard System

### Goal
Cloud writes activity to /Updates/. Local reads and merges
into Dashboard.md. Only Local Agent writes Dashboard.md
(single-writer rule).

### Estimated Time
2–3 hours

### Dashboard Flow

```
Cloud VM:                          Local PC:
─────────────────                  ─────────────────
Cloud drafts email                 Git pull (every 5min)
Writes to:                              ↓
/Updates/cloud_activity.md         Reads /Updates/
       ↓                           Merges into Dashboard.md
Git auto-push                      Writes Dashboard.md
       ↓                           Git push
─────────────────────────────────────────────────────
Result: Dashboard always shows what Cloud is doing,
        even when Local PC was offline
```

### Dashboard Template

```markdown
# Dashboard.md
---
last_updated: <timestamp>
updated_by: local_agent
---

## System Status
| Agent | Status | Last Seen |
|-------|--------|-----------|
| Cloud | 🟢 Online | 2026-01-07 10:45 |
| Local | 🟢 Online | 2026-01-07 10:50 |
| Odoo  | 🟢 Running | 2026-01-07 10:00 |
| Git Sync | 🟢 Active | 5 min ago |

## Pending Approvals
- CLOUD_email_client_a_approval.md (from: client@email.com)

## Recent Activity
- [10:45] Cloud drafted reply for EMAIL_abc123.md
- [10:30] Local sent invoice to Client A
- [10:00] Git sync successful

## Bank Balance
$4,500 (updated daily)

## Active Tasks
- Project Alpha — Due Jan 15
```

---

## Phase 7.5 — /Signals/ Agent Communication

### Goal
/Signals/ folder agent-to-agent communication ke liye hai.
Cloud VM koi problem detect kare ya Local ko alert karna ho
toh /Signals/ mein file likhta hai. Local Agent yeh signals
padhta hai aur respond karta hai.

### Estimated Time
2–3 hours

### Signal Types

```
Signal File Name              Kaun Likhta    Kaun Padh ta   Matlab
──────────────────────────────────────────────────────────────────
CLOUD_DOWN.md                 Watchdog       Local          Cloud VM offline hai
LOCAL_OFFLINE.md              Cloud          Local          Local se koi response nahi
SYNC_CONFLICT.md              git_sync.py    Both           Git conflict hai
APPROVAL_EXPIRED.md           Cloud          Local          24hr se approval nahi mila
TASK_FAILED.md                Either         Both           Task process nahi hua
HEALTH_CHECK.md               Cloud          Local          Regular ping signal
```

### signals_writer.py (Cloud VM pe)

```python
# signals_writer.py — Cloud VM pe run hoga
from pathlib import Path
from datetime import datetime
import json

VAULT = Path("/home/ubuntu/AI_Employee_Vault")
SIGNALS = VAULT / "Signals"

def write_signal(signal_type: str, message: str, data: dict = None):
    """Cloud Agent signal likhta hai /Signals/ mein."""
    SIGNALS.mkdir(exist_ok=True)

    signal_content = f"""---
signal_type: {signal_type}
written_by: cloud_agent
timestamp: {datetime.now().isoformat()}
status: unread
---

## Signal: {signal_type}

{message}

## Data
{json.dumps(data or {}, indent=2)}

## To Acknowledge
Move this file to /Signals/Acknowledged/
"""
    signal_file = SIGNALS / f"{signal_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    signal_file.write_text(signal_content)
    return signal_file

# Usage examples:
# write_signal("APPROVAL_EXPIRED", "No approval received in 24hrs", {"task": "EMAIL_abc.md"})
# write_signal("HEALTH_CHECK", "Cloud Agent is alive", {"uptime": "24h", "tasks_processed": 5})
# write_signal("TASK_FAILED", "Could not draft reply", {"error": "Gmail API timeout"})
```

### signals_reader.py (Local PC pe)

```python
# signals_reader.py — Local PC pe run hoga
from pathlib import Path
from datetime import datetime
import logging

VAULT = Path("E:/HC/AI_Employee_Vault")
SIGNALS = VAULT / "Signals"
SIGNALS_ACK = SIGNALS / "Acknowledged"
DASHBOARD = VAULT / "Dashboard.md"

logger = logging.getLogger("signals_reader")

SIGNAL_HANDLERS = {
    "CLOUD_DOWN":        "alert_cloud_down",
    "APPROVAL_EXPIRED":  "handle_expired_approval",
    "SYNC_CONFLICT":     "handle_sync_conflict",
    "TASK_FAILED":       "handle_task_failed",
    "HEALTH_CHECK":      "log_health_check",
}

def read_signals():
    """Local Agent /Signals/ check karta hai har minute."""
    SIGNALS_ACK.mkdir(exist_ok=True)

    for signal_file in SIGNALS.glob("*.md"):
        content = signal_file.read_text()

        # Signal type detect karo
        for signal_type, handler in SIGNAL_HANDLERS.items():
            if signal_type in signal_file.name:
                handle_signal(signal_type, content, signal_file)
                break

def handle_signal(signal_type: str, content: str, signal_file: Path):
    """Signal ke type ke hisaab se action lo."""
    logger.info(f"Signal received: {signal_type}")

    if signal_type == "CLOUD_DOWN":
        update_dashboard("⚠️ ALERT: Cloud Agent offline detected")

    elif signal_type == "APPROVAL_EXPIRED":
        update_dashboard(f"⚠️ Approval expired: {signal_file.name}")

    elif signal_type == "SYNC_CONFLICT":
        update_dashboard("⚠️ Git sync conflict — manual resolution needed")

    elif signal_type == "TASK_FAILED":
        update_dashboard(f"❌ Task failed: see {signal_file.name}")

    elif signal_type == "HEALTH_CHECK":
        update_dashboard(f"🟢 Cloud Agent alive: {datetime.now().strftime('%H:%M')}")

    # Signal acknowledge karo — /Acknowledged/ mein move karo
    ack_dest = SIGNALS_ACK / signal_file.name
    signal_file.rename(ack_dest)

def update_dashboard(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [{timestamp}] {message}\n"
    # Prepend to Recent Activity in Dashboard.md

def run():
    logger.info("Signals Reader started")
    while True:
        try:
            read_signals()
        except Exception as e:
            logger.error(f"Signal read error: {e}")
        import time
        time.sleep(60)

if __name__ == "__main__":
    run()
```

### /Signals/ Folder Structure

```
Signals/
├── HEALTH_CHECK_20260107_1000.md     ← Cloud ne likha (unread)
├── APPROVAL_EXPIRED_20260107_0900.md ← Cloud ne likha (unread)
└── Acknowledged/                     ← Local ne read kar liya
    ├── HEALTH_CHECK_20260106_1000.md
    └── TASK_FAILED_20260106_0800.md
```

### Signal Rules

```
Cloud likhta hai:              Local karta hai:
✅ HEALTH_CHECK (har ghanta)   ✅ Signals padhta hai (har minute)
✅ APPROVAL_EXPIRED            ✅ Dashboard update karta hai
✅ TASK_FAILED                 ✅ /Acknowledged/ mein move karta hai
✅ SYNC_CONFLICT detect        ❌ /Signals/ mein nahi likhta
                               ❌ Signal files delete nahi karta
```

### Agent Skill To Create

```
Skill: signals-monitor-skill
Purpose: Read and respond to agent signals, alert human
Trigger: "check signals", "any alerts", "agent signals",
         "cloud sent signal", "signal folder", "agent alert"

SKILL.md steps:
  1. List all unread files in /Signals/
  2. Show summary to human (type, timestamp, message)
  3. For CLOUD_DOWN → immediate Dashboard alert
  4. For APPROVAL_EXPIRED → list expired tasks
  5. For SYNC_CONFLICT → show conflict details
  6. Move read signals to /Signals/Acknowledged/
  7. Update Dashboard.md with signal summary
```

---

## Phase 8 — Platinum Demo Preparation

### Goal
Record the minimum passing demo as specified in hackathon
document. Show offline → online → approval → send flow.

### Estimated Time
3–4 hours

### Minimum Demo Script (Exact From Document)

```
Record exactly this scenario:

0:00 — Show Cloud VM terminal
       pm2 list → all processes online

0:30 — Show Local PC vault in Obsidian
       Dashboard.md → both agents online

1:00 — Turn Local PC offline
       Enable airplane mode / disconnect internet

1:30 — Send test email to your Gmail
       Subject: "Test Platinum Demo — Invoice Request"

2:00 — Show Cloud VM terminal
       Cloud Agent detecting email in real time
       pm2 logs cloud-gmail-watcher

2:30 — Show /Pending_Approval/ on GitHub
       CLOUD_EMAIL_xxx_approval.md appears

3:00 — Turn Local PC back online
       Git sync pulls the approval file

3:30 — Show approval file in Obsidian
       Move file to /Approved/

4:00 — Show Local Agent executing
       pm2 logs local-orchestrator (or Task Scheduler)

4:30 — Show email sent in Gmail Sent folder

5:00 — Show /Done/ folder updated
       Show /Logs/ entry with full audit

5:30 — Show Dashboard.md updated
       Both agents show activity
```

### Agent Skill To Create

```
Skill: platinum-demo-skill
Purpose: Run demo scenario, verify all components work
Trigger: "platinum demo", "run demo", "test dual agent",
         "demo check", "hackathon demo", "offline scenario"

SKILL.md steps:
  1. Check Cloud VM status via SSH
  2. Check Git sync is working
  3. Check Odoo health on Cloud VM
  4. Verify /Pending_Approval/ is accessible
  5. Run test email send
  6. Confirm Cloud Agent creates approval file
  7. Confirm Local Agent executes after approval
  8. Generate demo checklist report
```

---

## All Platinum Skills Summary

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `git-sync-skill` | "sync status", "git sync" | Monitor vault sync |
| `cloud-agent-skill` | "cloud agent", "cloud status" | Cloud VM health |
| `local-agent-skill` | "pending approvals", "approve" | Manage approvals |
| `dual-dashboard-skill` | "dashboard update", "agent status" | Merge Updates |
| `signals-monitor-skill` | "check signals", "any alerts", "agent alert" | Agent signals |
| `platinum-demo-skill` | "platinum demo", "run demo" | Demo verification |

---

## Security Rules — All Phases

```
VAULT SYNC:
  Only .md and state files sync
  .env files NEVER sync (add to .gitignore)
  Secrets NEVER in markdown files

CLOUD VM:
  WhatsApp session NEVER on Cloud VM
  Banking credentials NEVER on Cloud VM
  Payment tokens NEVER on Cloud VM
  Cloud only drafts — never executes sends

LOCAL PC:
  WhatsApp session LOCAL ONLY
  Banking credentials LOCAL ONLY
  Payment tokens LOCAL ONLY
  Final sends LOCAL ONLY

AUDIT:
  Every action logged to /Logs/YYYY-MM-DD.json
  Log format: timestamp, agent, action, result
  Retain logs minimum 90 days
  DRY_RUN=true during testing
  Rate limit: max 20 actions/hour per agent
```

---

## Judging Criteria Coverage

```
Functionality 30%:
  ✅ Cloud Agent running 24/7 on Oracle VM
  ✅ Local Agent executing approved actions
  ✅ Offline demo scenario works
  ✅ Git sync working
  ✅ Odoo on cloud with HTTPS

Innovation 25%:
  ✅ Dual Agent Architecture (novel for hackathon)
  ✅ Claim-by-Move pattern (prevents double work)
  ✅ File-based A2A communication via vault
  ✅ Git as agent communication bus

Practicality 20%:
  ✅ Oracle Free VM (zero cost, forever)
  ✅ Real email workflow demonstrated
  ✅ Works even when PC is offline
  ✅ Human always in control

Security 15%:
  ✅ Secrets never sync via Git
  ✅ HTTPS on Odoo cloud
  ✅ Audit logs on both agents
  ✅ Banking credentials local only
  ✅ Claim-by-move prevents race conditions

Documentation 10%:
  ✅ Architecture diagram in README.md
  ✅ Demo video (5-10 minutes)
  ✅ Setup instructions for both agents
  ✅ Security disclosure document
```

---

## Phase Timeline

```
Phase 1: Cloud VM Setup          3–4 hrs
Phase 2: Cloud VM Configure      2–3 hrs
Phase 3: Git Vault Sync          3–4 hrs
Phase 4: Cloud Agent Code        5–6 hrs
Phase 5: Odoo Cloud Deploy       4–5 hrs
Phase 6: Local Agent Code        4–5 hrs
Phase 7: Dual Dashboard          2–3 hrs
Phase 7.5: Signals System        2–3 hrs
Phase 8: Demo Preparation        3–4 hrs
────────────────────────────────────────
Total:                          28–37 hrs
```

---

## Claude Code Prompts (Use In Order)

```bash
"Read PLATINUM_TIER.md and implement Phase 1 — Cloud VM Setup"

"Read PLATINUM_TIER.md and implement Phase 2 — Cloud VM Configuration"

"Read PLATINUM_TIER.md and implement Phase 3 — Git Vault Sync"

"Read PLATINUM_TIER.md and implement Phase 4 — Cloud Agent"

"Read PLATINUM_TIER.md and implement Phase 5 — Odoo Cloud"

"Read PLATINUM_TIER.md and implement Phase 6 — Local Agent"

"Read PLATINUM_TIER.md and implement Phase 7 — Dual Dashboard"

"Read PLATINUM_TIER.md, use skill-creator pattern
to build and test the platinum-demo-skill"

"Read PLATINUM_TIER.md and implement Phase 8 — Demo Prep"
```

---

*Personal AI Employee — Platinum Tier*
