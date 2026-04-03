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

# To create a new Skill:
"Read platinum-tier-speckit.md and create the Skill for Phase 4"

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
  Folders: /Needs_Action, /Plans, /Done, /Logs
  Skills: inbox-processor, dashboard-updater, gmail-watcher

Silver Tier:
  WhatsApp Watcher (whatsapp_watcher.py)
  Email MCP Server
  LinkedIn Auto-Poster
  HITL Approval Workflow
  Folders: /Pending_Approval, /Approved, /Rejected
  Skills: plan-creator, whatsapp-handler, approval-processor
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
  Skills: odoo-invoice-skill, social-poster-skill,
          ceo-briefing-skill, watchdog-skill
```

### What Platinum Tier Must Add

Eight phases on top of Gold. Build in order: 1 to 8.
Each phase depends on the previous being complete and tested.

```
Phase 1  →  Cloud VM Setup (AWS EC2)
Phase 2  →  VM Environment Configure
Phase 3  →  Git Vault Sync (Cloud ↔ Local)
Phase 4  →  Cloud Agent Deploy
Phase 5  →  Odoo Cloud Migration
Phase 6  →  Work Zone Specialization
Phase 7  →  Dashboard Sync via /Updates/
Phase 8  →  Testing + Demo Video
```

Total estimated time: 34–44 hours

---

## Skill Creator Pattern — Use For Every New Skill

Every Platinum feature that needs a Skill must follow
this pattern. This is based on the official skill-creator
methodology.

### How To Create Every New Skill

```
Step 1 — Write SKILL.md with:
  - YAML frontmatter (name + description)
  - Trigger phrases listed clearly in description
  - Step by step instructions
  - Output format definition
  - Rules and constraints

Step 2 — Write 2-3 test cases in evals/evals.json:
  {
    "skill_name": "skill-name",
    "evals": [
      {
        "id": 1,
        "prompt": "realistic user prompt",
        "expected_output": "what Claude should do"
      }
    ]
  }

Step 3 — Run test cases. Evaluate results qualitatively.

Step 4 — Improve SKILL.md based on test results.

Step 5 — Save final SKILL.md to:
  E:/HC/AI_Employee_Vault/Skills/skill-name/SKILL.md
```

### SKILL.md Template (Use For Every Skill)

```markdown
---
name: skill-name
description: >
  WHAT it does AND WHEN Claude should use it.
  Mention all trigger phrases explicitly.
  Make description slightly "pushy" so Claude
  does not undertrigger the skill.
---

# Skill Name

## Purpose
One line: What does this skill do?

## Trigger Phrases
Use this skill when user says:
- "..."
- "..."

## Input
What input does this skill receive?

## Steps
1. Step one
2. Step two
3. Step three

## Output Format
What file/result does this skill produce?

## Rules
- Rule 1
- Rule 2
- DRY_RUN=true must be supported
```

---

## Vault Folder Structure — Platinum Additions

Add these new folders inside existing vault:

```
E:/HC/AI_Employee_Vault/
├── (All Bronze + Silver + Gold folders remain)
│
├── In_Progress/
│   ├── cloud/        ← Cloud Agent working files
│   └── local/        ← Local Agent working files
│
├── Updates/          ← Cloud writes status here
│                       Local reads + merges into Dashboard.md
│
└── Signals/          ← Agent-to-agent communication
                        Cloud writes → Local reads
```

### Claim-by-Move Rule

```
When a task file arrives in /Needs_Action/:

  Cloud Agent:                 Local Agent:
  ────────────                 ────────────
  Tries to move file           Tries to move file
  to /In_Progress/cloud/       to /In_Progress/local/

  Whoever moves it first → owns the task.
  Other agent detects it is gone → skips it.
  No double work. No conflict.
```

---

## Security Rules — Apply To All Phases

```
Git Sync — ALLOWED:          Git Sync — NEVER:
✅ .md task files             ❌ .env files
✅ Dashboard.md               ❌ API keys / tokens
✅ Plans + Logs               ❌ WhatsApp session files
✅ Signals files              ❌ Banking credentials
✅ Updates files              ❌ Odoo admin password
                              ❌ OAuth tokens

Cloud Agent — CAN:           Cloud Agent — CANNOT:
✅ Read emails                ❌ Send emails directly
✅ Draft replies              ❌ Post to social directly
✅ Write to /Pending_Approval ❌ Access payment systems
✅ Write Odoo drafts          ❌ Post Odoo invoices
✅ Write to /Signals/         ❌ Access WhatsApp session
```

---

## Phase 1 — Cloud VM Setup (AWS EC2)

### Goal
Launch a 24/7 cloud server that will run the Cloud Agent.
Oracle Cloud signup is difficult from Pakistan — use AWS EC2
Free Tier instead.

### Prerequisites
- AWS account (free tier)
- Local PC: Git installed, SSH client (Windows built-in is fine)
- Vault already working locally (Gold complete)

### Step-by-Step Instructions

```
1. Go to: https://aws.amazon.com/free
   Sign up for AWS Free Tier account

2. AWS Console → EC2 → Launch Instance:
   Name:          ai-employee-cloud
   OS:            Ubuntu 22.04 LTS
   Instance type: t2.micro (free tier)
   Key pair:      Create new → download ai-employee-key.pem
   Storage:       20 GB gp2

3. Security Group — open these ports:
   Port 22   → SSH (Your IP only — not 0.0.0.0)
   Port 80   → HTTP
   Port 443  → HTTPS
   Port 8069 → Odoo (restrict to your IP only)

4. Launch instance. Wait for "Running" status.

5. Note down:
   Public IPv4 address   → copy this
   Public DNS name       → copy this
```

### Test Criteria

```
PASS: Can SSH into VM with this command:
  ssh -i ai-employee-key.pem ubuntu@YOUR_PUBLIC_IP

PASS: See Ubuntu terminal prompt
PASS: Internet works on VM:
  ping google.com → gets replies
```

### Files Created This Phase

```
Local PC:
  ~/Downloads/ai-employee-key.pem    ← Keep safe, never share
```

---

## Phase 2 — VM Environment Configure

### Goal
Install all required software on the cloud VM so it can
run Python scripts, Node.js tools, and PM2 process manager.

### Prerequisites
- Phase 1 complete
- SSH access working

### Step-by-Step Instructions

```bash
# SSH into VM first:
ssh -i ai-employee-key.pem ubuntu@YOUR_PUBLIC_IP

# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.11 + pip
sudo apt install python3.11 python3-pip python3.11-venv -y

# 3. Install Node.js v20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# 4. Install PM2 (process manager)
sudo npm install -g pm2

# 5. Install Git
sudo apt install git -y

# 6. Install Docker (for Odoo — Phase 5)
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu
newgrp docker

# 7. Create vault folder on VM
mkdir -p ~/AI_Employee_Vault

# 8. Create Python virtual environment
cd ~/AI_Employee_Vault
python3.11 -m venv venv
source venv/bin/activate
pip install anthropic python-dotenv watchdog requests
```

### Watchdog Config (PM2 — Auto Restart on Crash)

```bash
# Create PM2 ecosystem file:
cat > ~/AI_Employee_Vault/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: "cloud-orchestrator",
      script: "orchestrator_cloud.py",
      interpreter: "./venv/bin/python",
      cwd: "/home/ubuntu/AI_Employee_Vault",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        DRY_RUN: "false"
      }
    },
    {
      name: "cloud-gmail-watcher",
      script: "gmail_watcher.py",
      interpreter: "./venv/bin/python",
      cwd: "/home/ubuntu/AI_Employee_Vault",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000
    }
  ]
}
EOF

# Start PM2:
pm2 start ecosystem.config.js
pm2 save
pm2 startup    # follow the printed command to enable on reboot
```

### Test Criteria

```
PASS: python3.11 --version → shows 3.11.x
PASS: node --version       → shows v20.x
PASS: pm2 --version        → shows version
PASS: docker --version     → shows version
PASS: pm2 list             → shows app list (even if empty)
```

---

## Phase 3 — Git Vault Sync

### Goal
Both Cloud VM and Local PC use the same Obsidian vault,
synchronized via a private Git repository. Secrets never
go into Git.

### Prerequisites
- Phase 2 complete
- GitHub account (free)

### Step A — Create Private Git Repo

```
1. GitHub → New Repository
   Name:    ai-employee-vault-sync
   Private: YES (very important)
   README:  No

2. Copy the repo URL:
   https://github.com/YOUR_USERNAME/ai-employee-vault-sync.git
```

### Step B — Setup on Local PC (Windows)

```powershell
# Open PowerShell in vault folder:
cd E:\HC\AI_Employee_Vault

# Initialize git:
git init
git remote add origin https://github.com/YOUR_USERNAME/ai-employee-vault-sync.git

# Create .gitignore — VERY IMPORTANT:
```

```
# .gitignore content — copy exactly:
.env
*.env
venv/
__pycache__/
*.pyc
*.pem
*.key
WhatsApp_Session/
node_modules/
.obsidian/workspace.json
Logs/sensitive/
```

```powershell
# First commit:
git add .
git commit -m "Initial vault sync"
git push -u origin main
```

### Step C — Setup on Cloud VM

```bash
# SSH into VM, then:
cd ~
git clone https://github.com/YOUR_USERNAME/ai-employee-vault-sync.git AI_Employee_Vault
cd AI_Employee_Vault

# Create cloud .env (different from local .env):
cat > .env << 'EOF'
ANTHROPIC_API_KEY=your_key_here
GMAIL_CREDENTIALS=cloud_credentials.json
AGENT_ROLE=cloud
VAULT_PATH=/home/ubuntu/AI_Employee_Vault
DRY_RUN=false
EOF
```

### Step D — Auto Sync Script (Both Sides)

Create this file on BOTH Local PC and Cloud VM:

```python
# File: vault_sync.py
import subprocess
import time
import logging
from pathlib import Path
import os

VAULT_PATH = os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault")
SYNC_INTERVAL = 60  # seconds

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [SYNC] %(message)s")

def sync_vault():
    try:
        # Pull latest from remote
        result = subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=VAULT_PATH,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logging.info(f"Pull OK: {result.stdout.strip()}")
        else:
            logging.error(f"Pull failed: {result.stderr.strip()}")

        # Push local changes
        subprocess.run(["git", "add", "."], cwd=VAULT_PATH)
        diff = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=VAULT_PATH, capture_output=True, text=True
        )
        if diff.stdout.strip():
            subprocess.run(
                ["git", "commit", "-m",
                 f"Auto sync {time.strftime('%Y-%m-%d %H:%M')}"],
                cwd=VAULT_PATH
            )
            subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=VAULT_PATH
            )
            logging.info("Pushed local changes")

    except Exception as e:
        logging.error(f"Sync error: {e}")

if __name__ == "__main__":
    logging.info("Vault sync started")
    while True:
        sync_vault()
        time.sleep(SYNC_INTERVAL)
```

### Test Criteria

```
PASS: Create test.md on Local PC → appears on Cloud VM
      within 2 minutes
PASS: Create test2.md on Cloud VM → appears on Local PC
      within 2 minutes
PASS: .env file is NOT pushed to GitHub
PASS: git log on both sides shows same commit hash
```

---

## Phase 4 — Cloud Agent Deploy

### Goal
Deploy orchestrator_cloud.py on VM. This agent handles
email triage, draft replies, and social post drafts.
It never sends anything — only prepares files for
Local Agent approval.

### Prerequisites
- Phase 3 complete and syncing correctly

### Cloud Agent Rules (Hard-Coded)

```python
# Cloud Agent responsibilities:
CLOUD_CAN_DO = [
    "read_new_emails",
    "write_draft_replies_to_pending_approval",
    "categorize_emails",
    "write_social_post_drafts",
    "write_to_signals_folder",
    "write_to_updates_folder",
    "move_files_to_in_progress_cloud",
    "write_odoo_invoice_drafts",
]

CLOUD_CANNOT_DO = [
    "send_emails",           # Local only
    "post_to_social_media",  # Local only
    "access_whatsapp",       # Local only
    "make_payments",         # Local only
    "post_odoo_invoices",    # Local only
    "read_local_env_file",   # Security
]
```

### orchestrator_cloud.py

```python
# File: orchestrator_cloud.py
import os
import time
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()

VAULT = Path(os.getenv("VAULT_PATH", "/home/ubuntu/AI_Employee_Vault"))
AGENT_ROLE = os.getenv("AGENT_ROLE", "cloud")
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
client = anthropic.Anthropic()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CLOUD] %(message)s",
    handlers=[
        logging.FileHandler(VAULT / "Logs" / f"{datetime.now().date()}.log"),
        logging.StreamHandler()
    ]
)

def claim_task(task_file: Path) -> bool:
    """Claim-by-Move: move file to /In_Progress/cloud/ to own it."""
    target = VAULT / "In_Progress" / "cloud" / task_file.name
    try:
        shutil.move(str(task_file), str(target))
        logging.info(f"Claimed task: {task_file.name}")
        return True
    except Exception:
        logging.info(f"Task already claimed by another agent: {task_file.name}")
        return False

def process_email_task(task_file: Path):
    """Read email task, draft reply, write to /Pending_Approval/."""
    content = task_file.read_text(encoding="utf-8")

    prompt = f"""You are a Cloud AI Employee.
Read this email task and draft a professional reply.

TASK FILE:
{content}

Rules:
- Draft reply only, do NOT send
- Be professional and concise
- If unsure, mark as NEEDS_HUMAN_REVIEW

Return JSON:
{{
  "draft_reply": "...",
  "priority": "high|medium|low",
  "category": "inquiry|complaint|follow_up|spam",
  "needs_human_review": true/false,
  "reason": "why this needs review (if applicable)"
}}
"""

    if DRY_RUN:
        logging.info(f"DRY_RUN: Would process {task_file.name}")
        return

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    result = json.loads(response.content[0].text)

    # Write to /Pending_Approval/
    approval_file = VAULT / "Pending_Approval" / f"email_reply_{task_file.stem}.md"
    approval_file.write_text(f"""---
type: email_reply_draft
source_task: {task_file.name}
priority: {result['priority']}
category: {result['category']}
needs_review: {result['needs_human_review']}
created_by: cloud_agent
created_at: {datetime.now().isoformat()}
---

# Draft Reply

{result['draft_reply']}

---
Reason for review: {result.get('reason', 'N/A')}
""", encoding="utf-8")

    logging.info(f"Draft written: {approval_file.name}")

def write_signal(signal_type: str, data: dict):
    """Write a signal for Local Agent to read."""
    signal_file = VAULT / "Signals" / f"{signal_type}_{int(time.time())}.json"
    signal_file.write_text(json.dumps({
        "type": signal_type,
        "from": "cloud_agent",
        "timestamp": datetime.now().isoformat(),
        "data": data
    }, indent=2))

def write_update(message: str):
    """Write status update for Dashboard merge."""
    update_file = VAULT / "Updates" / f"cloud_{int(time.time())}.md"
    update_file.write_text(f"""---
from: cloud_agent
at: {datetime.now().isoformat()}
---
{message}
""")

def main_loop():
    logging.info("Cloud Agent started")
    write_update("Cloud Agent online and monitoring")

    while True:
        try:
            needs_action = VAULT / "Needs_Action"
            for task_file in needs_action.glob("*.md"):
                if claim_task(task_file):
                    claimed = VAULT / "In_Progress" / "cloud" / task_file.name
                    content = claimed.read_text()
                    if "email" in content.lower() or "gmail" in content.lower():
                        process_email_task(claimed)

            time.sleep(30)

        except Exception as e:
            logging.error(f"Loop error: {e}")
            write_signal("error", {"message": str(e)})
            time.sleep(60)

if __name__ == "__main__":
    main_loop()
```

### Skill — cloud-agent-skill

```
Skills/cloud-agent-skill/SKILL.md
```

```yaml
---
name: cloud-agent-skill
description: >
  Processes email tasks on the Cloud VM. Drafts replies,
  categorizes emails, writes to /Pending_Approval/.
  Use this skill when cloud agent needs to handle new
  email tasks, draft social posts, or write signals.
  Trigger on: "process email", "draft reply", "cloud agent
  task", "triage inbox", "queue for approval".
---

# Cloud Agent Skill

## Purpose
Read email tasks from /In_Progress/cloud/, draft replies
using Claude, write drafts to /Pending_Approval/.

## Steps
1. Read task file from /In_Progress/cloud/
2. Extract: sender, subject, body, priority
3. Call Claude to draft professional reply
4. Write draft to /Pending_Approval/email_reply_TASKNAME.md
5. Write signal to /Signals/ (task_drafted)
6. Write update to /Updates/ (status message)
7. Log to /Logs/YYYY-MM-DD.log

## Output Format
/Pending_Approval/email_reply_*.md with YAML frontmatter

## Rules
- NEVER send email directly
- NEVER access WhatsApp
- NEVER make payments
- Always support DRY_RUN=true
- Max 20 tasks per hour (rate limit)
```

### Test Criteria

```
PASS: Create a test file in /Needs_Action/ on Local PC
PASS: Git sync pushes it to Cloud VM
PASS: Cloud Agent claims it (moves to /In_Progress/cloud/)
PASS: Draft appears in /Pending_Approval/
PASS: Signal file appears in /Signals/
PASS: Update file appears in /Updates/
PASS: Git sync brings files back to Local PC
```

---

## Phase 5 — Odoo Cloud Migration

### Goal
Move Odoo from Local PC (localhost:8069) to Cloud VM
with HTTPS and daily backups. Cloud Agent can only create
Odoo drafts. Local Agent approves and posts.

### Prerequisites
- Phase 4 complete
- Domain name (optional — can use IP with self-signed cert)

### Step A — Install Odoo on Cloud VM

```bash
# SSH into VM, then:
mkdir -p ~/odoo-cloud
cd ~/odoo-cloud

cat > docker-compose.yml << 'EOF'
version: '3.1'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: CHANGE_THIS_STRONG_PASSWORD
    volumes:
      - odoo_db:/var/lib/postgresql/data
    restart: always

  odoo:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      HOST: db
      USER: odoo
      PASSWORD: CHANGE_THIS_STRONG_PASSWORD
    volumes:
      - odoo_data:/var/lib/odoo
    restart: always

volumes:
  odoo_db:
  odoo_data:
EOF

docker-compose up -d
```

### Step B — HTTPS with Nginx + SSL

```bash
# Install nginx + certbot:
sudo apt install nginx certbot python3-certbot-nginx -y

# Configure nginx proxy:
sudo cat > /etc/nginx/sites-available/odoo << 'EOF'
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;

    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Note: For full HTTPS you need a domain name.
# With IP only: use self-signed cert for testing.
```

### Step C — Daily Backup

```bash
# Create backup script:
cat > ~/backup_odoo.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y-%m-%d)
BACKUP_DIR=~/odoo_backups
mkdir -p $BACKUP_DIR

# Backup database
docker exec odoo-cloud_db_1 pg_dump -U odoo odoo > \
  $BACKUP_DIR/odoo_db_$DATE.sql

# Backup filestore
docker run --rm \
  -v odoo-cloud_odoo_data:/data \
  -v $BACKUP_DIR:/backup \
  ubuntu tar czf /backup/odoo_files_$DATE.tar.gz /data

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup done: $DATE"
EOF

chmod +x ~/backup_odoo.sh

# Schedule daily backup at 2 AM:
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup_odoo.sh") | crontab -
```

### Odoo MCP Rules — Cloud vs Local

```
Cloud Agent CAN:
  ✅ Create invoice draft
  ✅ Create customer record
  ✅ Read invoice list
  ✅ Write draft to /Pending_Approval/

Cloud Agent CANNOT:
  ❌ Post/confirm invoice
  ❌ Register payment
  ❌ Delete records
  ❌ Change account settings

Local Agent CAN (after human approval):
  ✅ Post/confirm invoices
  ✅ Register payments
  ✅ Send invoices to customers
```

### Test Criteria

```
PASS: Odoo accessible at http://YOUR_PUBLIC_IP:8069
PASS: Can login with admin credentials
PASS: Cloud Agent creates draft invoice via MCP
PASS: Draft appears in /Pending_Approval/ vault folder
PASS: Backup script runs and creates .sql file
PASS: docker-compose ps → both containers "Up"
```

---

## Phase 6 — Work Zone Specialization

### Goal
Clearly separate what Cloud Agent does vs Local Agent.
Update Local orchestrator to read Signals from Cloud.
Add Local-only functions for approvals and WhatsApp.

### Local Agent New Functions

```python
# Add to existing orchestrator.py on Local PC:

def read_signals():
    """Read and process signals from Cloud Agent."""
    signals_dir = VAULT / "Signals"
    processed_dir = VAULT / "Signals" / "processed"
    processed_dir.mkdir(exist_ok=True)

    for signal_file in signals_dir.glob("*.json"):
        try:
            signal = json.loads(signal_file.read_text())
            handle_signal(signal)
            # Move to processed so we don't re-read
            shutil.move(str(signal_file),
                        str(processed_dir / signal_file.name))
        except Exception as e:
            logging.error(f"Signal read error: {e}")

def handle_signal(signal: dict):
    """Route signal to correct handler."""
    signal_type = signal.get("type", "")
    data = signal.get("data", {})

    if signal_type == "task_drafted":
        logging.info(f"Cloud drafted task: {data.get('task')}")
    elif signal_type == "error":
        logging.warning(f"Cloud agent error: {data.get('message')}")
    elif signal_type == "health_check":
        write_local_update("Received health check from cloud")

def handle_approved_file(approved_file: Path):
    """Process an approved file from /Approved/ folder."""
    content = approved_file.read_text(encoding="utf-8")

    if "email_reply" in approved_file.name:
        send_approved_email(content, approved_file)
    elif "social_post" in approved_file.name:
        post_approved_social(content, approved_file)
    elif "odoo_invoice" in approved_file.name:
        post_approved_odoo_invoice(content, approved_file)

def process_approvals():
    """Watch /Approved/ folder and execute approved tasks."""
    approved_dir = VAULT / "Approved"
    for f in approved_dir.glob("*.md"):
        handle_approved_file(f)
        # Move to /Done/ after execution
        shutil.move(str(f), str(VAULT / "Done" / f.name))
        logging.info(f"Executed and moved to Done: {f.name}")
```

### Work Zone Summary

```
CLOUD VM (24/7):
  ┌─────────────────────────────────┐
  │  gmail_watcher.py               │
  │  orchestrator_cloud.py          │
  │  vault_sync.py                  │
  │                                 │
  │  Writes to:                     │
  │    /Needs_Action/ (new tasks)   │
  │    /Pending_Approval/ (drafts)  │
  │    /Signals/ (messages)         │
  │    /Updates/ (status)           │
  │    /In_Progress/cloud/ (owned)  │
  └─────────────────────────────────┘

LOCAL PC:
  ┌─────────────────────────────────┐
  │  orchestrator.py (updated)      │
  │  whatsapp_watcher.py            │
  │  vault_sync.py                  │
  │                                 │
  │  Reads from:                    │
  │    /Pending_Approval/ (review)  │
  │    /Signals/ (from cloud)       │
  │    /Updates/ (merge into dash)  │
  │                                 │
  │  Writes to:                     │
  │    /Approved/ or /Rejected/     │
  │    /Done/ (completed)           │
  │    /In_Progress/local/ (owned)  │
  └─────────────────────────────────┘
```

### Test Criteria

```
PASS: Cloud writes signal → Local reads it within 2 minutes
PASS: Approve a draft on Local → email/post executed
PASS: WhatsApp messages only processed on Local
PASS: Cloud never attempts to send email directly
PASS: Logs show which agent handled each task
```

---

## Phase 7 — Dashboard Sync via /Updates/

### Goal
Cloud Agent cannot directly write to Dashboard.md
(conflict risk). Instead it writes status to /Updates/.
Local Agent merges Updates into Dashboard.md once per hour.

### Update Writer (Cloud Side)

```python
# Add to orchestrator_cloud.py:

def write_update(message: str, category: str = "status"):
    """Write a cloud update for Local to merge."""
    update_file = VAULT / "Updates" / \
        f"cloud_{category}_{int(time.time())}.md"
    update_file.write_text(f"""---
from: cloud_agent
category: {category}
at: {datetime.now().isoformat()}
---
{message}
""", encoding="utf-8")
```

### Dashboard Merger (Local Side)

```python
# File: dashboard_merger.py (run hourly via PM2/Task Scheduler)
import os
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT = Path(os.getenv("VAULT_PATH", "E:/HC/AI_Employee_Vault"))

def merge_updates():
    updates_dir = VAULT / "Updates"
    processed_dir = updates_dir / "processed"
    processed_dir.mkdir(exist_ok=True)

    dashboard = VAULT / "Dashboard.md"
    current = dashboard.read_text(encoding="utf-8")

    new_entries = []
    for update_file in sorted(updates_dir.glob("cloud_*.md")):
        content = update_file.read_text(encoding="utf-8")
        # Strip YAML frontmatter
        lines = content.split("\n")
        body_lines = []
        in_front = False
        for line in lines:
            if line.strip() == "---":
                in_front = not in_front
                continue
            if not in_front:
                body_lines.append(line)
        body = "\n".join(body_lines).strip()
        if body:
            new_entries.append(
                f"- [{datetime.now().strftime('%H:%M')}] ☁️ Cloud: {body}"
            )
        shutil.move(str(update_file),
                    str(processed_dir / update_file.name))

    if new_entries:
        update_section = "\n".join(new_entries)
        marker = "## Cloud Agent Updates"
        if marker in current:
            updated = current.replace(
                marker,
                f"{marker}\n{update_section}"
            )
        else:
            updated = current + f"\n\n{marker}\n{update_section}"
        dashboard.write_text(updated, encoding="utf-8")
        print(f"Merged {len(new_entries)} updates into Dashboard.md")

if __name__ == "__main__":
    merge_updates()
```

### Schedule Dashboard Merger

```bash
# Add to PM2 on Local PC (ecosystem.config.js):
{
  name: "dashboard-merger",
  script: "dashboard_merger.py",
  interpreter: "python",
  cwd: "E:/HC/AI_Employee_Vault",
  cron_restart: "0 * * * *",   # Every hour
  autorestart: false
}
```

### Test Criteria

```
PASS: Cloud writes 3 updates → all appear in Dashboard.md
      within 1 hour
PASS: Dashboard.md has no merge conflicts
PASS: Processed updates moved to /Updates/processed/
PASS: Multiple cloud updates do not overwrite each other
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

## Phase 8 — Testing + Demo Video

### Offline Resilience Test (Required for Demo)

This exact scenario must work for minimum passing demo:

```
STEP 1:  Send a test email to monitored Gmail account
STEP 2:  Turn OFF your Local PC (or disconnect from internet)
         ↓ Local PC is now OFFLINE
STEP 3:  Wait 2–3 minutes
STEP 4:  Cloud Agent detects new email (still running 24/7)
STEP 5:  Cloud Agent drafts reply
STEP 6:  Cloud Agent writes to /Pending_Approval/
STEP 7:  Cloud Agent syncs to Git automatically
         ↓ Now turn Local PC back ON
STEP 8:  vault_sync.py pulls latest from Git
STEP 9:  Approval file appears in Local PC vault
STEP 10: You move file to /Approved/ (or approve via HITL)
STEP 11: Local orchestrator detects approval
STEP 12: Local Agent sends email via MCP
STEP 13: Task moved to /Done/
STEP 14: Logs updated on both sides

RESULT: Email was handled even while PC was offline ✅
```

### Full Test Checklist

```
Infrastructure:
  □ AWS EC2 VM running 24/7
  □ SSH access works from Local PC
  □ PM2 keeps processes alive after reboot

Git Vault Sync:
  □ Local → Cloud sync works (< 2 min)
  □ Cloud → Local sync works (< 2 min)
  □ .env files NOT in GitHub repo
  □ Conflict resolution works

Cloud Agent:
  □ Detects new emails automatically
  □ Drafts replies to /Pending_Approval/
  □ Claim-by-Move prevents double work
  □ Writes signals to /Signals/
  □ Writes updates to /Updates/

Local Agent:
  □ Reads signals from Cloud
  □ Processes approvals correctly
  □ Sends approved emails via MCP
  □ Never processes WhatsApp on Cloud

Odoo Cloud:
  □ Accessible at Cloud VM IP
  □ Daily backup runs at 2 AM
  □ Cloud can create Odoo drafts
  □ Only Local can post invoices

Dashboard:
  □ Cloud updates appear in Dashboard.md
  □ No merge conflicts
  □ Single writer rule respected

Security:
  □ .env never in Git
  □ Cloud cannot make payments
  □ HTTPS configured on Odoo
  □ SSH restricted to Your IP only

Offline Scenario:
  □ Full offline test passes (see above)
```

### Demo Video Script (5–10 minutes)

```
Minute 0:00 — Architecture diagram
  Show: Cloud VM ↔ Git ↔ Local PC diagram
  Say:  "Two agents, one vault, synced via Git"

Minute 1:00 — Live dashboard
  Show: Dashboard.md open in Obsidian
  Show: PM2 list on Cloud VM in one terminal
  Show: PM2 list on Local PC in another terminal

Minute 2:00 — Normal flow demo
  Send a test email
  Show Cloud Agent detecting it (tail logs)
  Show draft appearing in /Pending_Approval/
  Approve it
  Show email sent (email client)

Minute 5:00 — Offline resilience demo
  Turn off Local PC internet
  Send another test email
  Show Cloud handling it (VM logs)
  Turn Local back on
  Show vault sync pulling the draft
  Approve and send

Minute 8:00 — Security proof
  Show .gitignore file
  Show GitHub repo — no .env files
  Show Cloud agent cannot see payment code

Minute 9:00 — Summary
  Bronze → Silver → Gold → Platinum progression
  Show /Done/ folder with completed tasks
```

---

## Skill — platinum-demo-skill

```
Skills/platinum-demo-skill/SKILL.md
```

```yaml
---
name: platinum-demo-skill
description: >
  Runs through the full Platinum tier demo scenario.
  Use when preparing for hackathon demo, testing the
  offline resilience scenario, or verifying all phases
  are working correctly. Trigger on: "run demo",
  "test platinum", "offline test", "prepare demo",
  "demo video", "check platinum status".
---

# Platinum Demo Skill

## Purpose
Execute and verify the complete Platinum tier demo
scenario including the offline resilience test.

## Steps
1. Check PM2 status on Cloud VM (SSH)
2. Check vault_sync.py running on both sides
3. Send test email to monitored account
4. Verify Cloud Agent detects it (check /In_Progress/cloud/)
5. Verify draft appears in /Pending_Approval/
6. Simulate offline (or just proceed to approval)
7. Move file to /Approved/
8. Verify Local Agent sends email
9. Verify task in /Done/
10. Check Dashboard.md has cloud updates
11. Print PASS/FAIL for each step

## Output
Demo checklist printed to terminal with PASS/FAIL per step

## Rules
- DRY_RUN=true shows steps without executing
- Log all results to /Logs/demo_YYYY-MM-DD.log
```

---

## Security Rules — Final Summary

```
Secrets:
  ❌ Never commit .env to Git
  ❌ Never log API keys
  ❌ Never print credentials
  ✅ Always use environment variables
  ✅ Rotate keys monthly

Cloud Agent:
  ❌ Never send emails directly
  ❌ Never post to social media
  ❌ Never access WhatsApp
  ❌ Never make payments
  ✅ Only draft + write to /Pending_Approval/

Local Agent:
  ✅ Only executes after human approval
  ✅ Reads /Approved/ before acting
  ✅ Logs every action

Rate Limits:
  ✅ Max 20 tasks per hour per agent
  ✅ Approval files expire after 24 hours
  ✅ Max 10 PM2 restarts before alert
```

---

## Judging Criteria — How Platinum Is Scored

```
Functionality       30%
  → Cloud + Local dono working
  → Offline scenario demo passes
  → All 8 phases complete

Innovation          25%
  → Dual agent architecture
  → Claim-by-Move pattern (novel)
  → File-based A2A via /Signals/
  → Git as sync layer (not a traditional DB)

Practicality        20%
  → AWS Free Tier (near-zero cost)
  → Real email workflow
  → Works on Windows + Ubuntu

Security            15%
  → Secrets never in Git
  → HTTPS on Odoo
  → Cloud cannot touch payments
  → Full audit logs

Documentation       10%
  → Architecture diagram
  → Demo video (5-10 min)
  → This spec file as proof of planning
```

---

*Personal AI Employee — Platinum Tier Specification*
*Format: Pure Markdown for spec-kit / specify-cli*
*Includes: Skill Creator Pattern for all new skills*
*Vault: E:/HC/AI_Employee_Vault | Platform: Windows + Ubuntu*
*Builds on: Bronze + Silver + Gold (all complete)*
*Cloud: AWS EC2 Free Tier (t2.micro, Ubuntu 22.04)*
