# Lessons Learned — AI Employee Vault

## Bronze Tier

### What Worked
- Gmail OAuth2 token auto-refresh — stable aur reliable
- Markdown files as task queue — simple lekin powerful
- Human approval step (Approved/ folder) — practical aur safe
- Claude Code slash commands — clean workflow

### Problems & Solutions
| Problem | Solution |
|---------|----------|
| Gmail API rate limits | processed_ids.json se duplicates avoid |
| Sensitive email detection | Company_Handbook.md rules |
| Email encoding issues | `encoding="utf-8"` har jagah |

---

## Silver Tier

### What Worked
- WhatsApp Playwright automation — free aur reliable
- LinkedIn Playwright — no API needed
- HITL orchestrator pattern — Approved/ folder as trigger
- PM2-style background processes

### Problems & Solutions
| Problem | Solution |
|---------|----------|
| WhatsApp QR scan timeout | Persistent session directory |
| LinkedIn login 2FA | Manual session save once |
| Multiple processes crashing | Watchdog (Gold tier) |

---

## Gold Tier

### What Worked
- Odoo Docker setup — clean isolation
- Odoo MCP server — seamless Claude integration
- Playwright for Twitter — API too expensive ($100/mo)
- Google Calendar API — simple OAuth reuse from Gmail
- CEO Briefing — aggregates everything in one place
- Ralph Wiggum stop hook — elegant autonomous loop
- Watchdog with wmic — reliable on Windows

### Problems & Solutions
| Problem | Solution |
|---------|----------|
| Twitter API → 402 Payment Required | Playwright browser automation |
| Twitter Google OAuth → no password field | Detect home URL after email, skip password |
| Calendar API 403 → scope missing | Regenerate token with calendar scope |
| Calendar API disabled | Enable in Google Cloud Console |
| settings.json credentials exposed | Move all to .env |
| WhatsApp browser opening repeatedly | headless=True |
| Terminal emoji encoding errors | Windows cp1252 issue — cosmetic only |
| Odoo login from CEO briefing | Add ODOO_* vars to .env |

---

## Key Design Decisions

### 1. Markdown Files as Message Queue
Instead of a database or message broker, plain markdown files in folders act as the task queue. Simple, human-readable, and Claude can read/write them natively.

### 2. Human-in-the-Loop by Default
Every action that affects the outside world (send email, post on social media) requires human approval. The Approved/ folder is the "go" signal.

### 3. Playwright over APIs
For social media (Facebook, Instagram, Twitter), browser automation is more practical than APIs:
- Free (no API costs)
- Works with Google OAuth accounts
- Same code pattern across platforms

### 4. MCP for Structured Data
For Odoo and Calendar (structured CRUD operations), MCP servers are cleaner than scripts:
- Claude can call tools directly
- No file intermediary needed
- Real-time results

### 5. Single .env for All Credentials
All credentials in one `.env` file — never in settings.json, never hardcoded, never committed to git.

---

## What I Would Do Differently

1. **Start with headless=True** — saves confusion with visible browsers
2. **Add .env from day 1** — don't put credentials in any config files
3. **Token scopes upfront** — add all needed OAuth scopes before first token generation
4. **Process manager first** — set up watchdog before running multiple processes
5. **Test with DRY_RUN=true** — before any real posts/emails
