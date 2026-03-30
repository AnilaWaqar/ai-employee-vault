# AI Employee Vault — CLAUDE.md

## Project Overview
This is the **Platinum Tier** of the AI Employee system (Phase 3 — Git Vault Sync).
Claude acts as an AI Employee to read, process, draft, and send emails via Gmail automation,
with dual-agent (Cloud + Local) architecture synced via GitHub.

---

## Project Structure

```
AI_Employee_Vault/
├── CLAUDE.md                          # This file — auto-loaded by Claude
├── SPEC.md                            # Full system specification (all tiers)
├── Company_Handbook.md                # Email rules & response templates
├── Dashboard.md                       # Auto-updated system status
├── init_skill.py                      # Tool to scaffold new skills
├── Skills/
│   ├── gmail-watcher/                 # Fetches emails from Gmail API
│   ├── inbox-processor/               # Processes Needs_Action/ files
│   └── dashboard-updater/             # Updates Dashboard.md counts
├── .claude/
│   └── commands/                      # Slash commands (/gmail-watcher etc.)
├── Needs_Action/                      # New emails waiting to be processed
├── Approved/                          # Drafts approved by user → pipeline sends
├── Drafts/                            # Draft responses awaiting human review
├── Pending_Approval/                  # Sensitive emails requiring manual review
├── Done/                              # Completed / sent items
├── Rejected/                          # Rejected drafts
├── Plans/                             # Action plans created by inbox-processor
├── Logs/                              # Pipeline logs + Claude activity logs
│
│── [Platinum Tier additions]
├── Needs_Action/
│   ├── email/                         # Cloud Agent picks up email tasks
│   ├── whatsapp/                      # Local Agent picks up WhatsApp tasks
│   └── social/                        # Cloud Agent picks up social tasks
├── In_Progress/
│   ├── cloud/                         # Tasks claimed by Cloud Agent
│   └── local/                         # Tasks claimed by Local Agent
├── Updates/                           # Cloud Agent writes activity here
├── Signals/                           # Agent-to-agent comms (SYNC_ERROR etc.)
└── Skills/
    └── git-sync/                      # Git sync monitor skill + script
```

---

## Email Workflow

```
Gmail
  ↓ [master_pipeline.py — every 120s]
Needs_Action/   ← EMAIL_*.md files created here
  ↓ [/inbox-processor — Claude]
Drafts/         ← Draft responses + Plans/ created
  ↓ [Human reviews]
Approved/       ← Human moves draft here to approve
  ↓ [master_pipeline.py — every 120s]
Done/           ← Email sent, file archived as SENT_*
```

Sensitive emails skip drafting → go to `Pending_Approval/` for manual review.

---

## Skills & Commands

| Skill | Command | What it does |
|-------|---------|--------------|
| gmail-watcher | `/gmail-watcher` | Start/monitor pipeline, report status |
| inbox-processor | `/inbox-processor` | Process Needs_Action/, create drafts |
| dashboard-updater | `/dashboard-updater` | Update Dashboard.md with current counts |
| git-sync | `/git-sync` | Monitor vault sync status, detect conflicts |

---

## Pipeline

| Item | Path |
|------|------|
| Main script | `Skills/gmail-watcher/scripts/master_pipeline.py` |
| Start manually | `Skills/gmail-watcher/scripts/start_pipeline.bat` |
| Auto-start setup | `python Skills/gmail-watcher/scripts/setup_autostart.py` |
| Cycle interval | Every 120 seconds |
| Processed IDs | `Skills/gmail-watcher/assets/processed_ids.json` |

---

## Rules
- Always follow `Company_Handbook.md` for email categorization and templates
- Sensitive emails (security, OTP, financial, legal, HR) → `Pending_Approval/` only
- Never send emails without human approval — user must manually move to `Approved/`
- Log every Claude action to `Logs/YYYY-MM-DD.md`
- Never delete processed email IDs from `processed_ids.json`
- Claim-by-move rule: first agent to move file from Needs_Action/<domain>/ to In_Progress/<agent>/ owns it
- Never auto-resolve git conflicts — always escalate to human via Signals/SYNC_ERROR.md
- Git sync runs every 5 minutes via Skills/git-sync/git_sync.py

---

## Auth & Credentials
| File | Purpose |
|------|---------|
| `Skills/gmail-watcher/assets/token.json` | Gmail OAuth token (auto-refreshes) |
| `Skills/gmail-watcher/assets/credentials.json` | Google API credentials |

To regenerate token: `python Skills/gmail-watcher/scripts/generate_token.py`
