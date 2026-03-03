# Security — AI Employee Vault

## Credential Storage

| Credential | Location | Notes |
|-----------|----------|-------|
| Gmail OAuth token | `Skills/gmail-watcher/assets/token.json` | Auto-refreshes |
| Google API creds | `Skills/gmail-watcher/assets/credentials.json` | Client ID/Secret |
| All passwords | `.env` | Never committed |
| Odoo credentials | `.env` | ODOO_USER, ODOO_PASSWORD |
| Social media | `.env` | FB, IG, Twitter, LinkedIn |

---

## What is NEVER Committed to Git

```
.env
Skills/gmail-watcher/assets/token.json
Skills/gmail-watcher/assets/credentials.json
twitter_session/
facebook_session/
instagram_session/
linkedin_session/
whatsapp_session/
```

---

## Human-in-the-Loop Safety

Every external action requires human approval:

| Action | Approval Method |
|--------|----------------|
| Send email | Move to `Approved/` folder |
| Post on social media | Move to `Approved/` folder |
| Create invoice | Claude asks before calling MCP |
| Create calendar event | Claude asks before calling MCP |

**Claude NEVER sends emails or posts without human approval.**

---

## Sensitive Email Handling

These email types go directly to `Pending_Approval/` — never auto-drafted:
- OTP / Verification codes
- Security alerts
- Financial transactions
- Legal documents
- HR / Personal information

---

## OAuth Scopes (Minimal)

Gmail token only requests what it needs:
```
gmail.modify    — read + label emails
gmail.send      — send emails
calendar        — read + write calendar events
```

---

## Rate Limiting

| System | Limit |
|--------|-------|
| Gmail API | 250 quota units/second |
| WhatsApp actions | 20 per hour (MAX_ACTIONS_PER_HOUR) |
| Watchdog restarts | 3 per process (MAX_RESTARTS) |
| Ralph Wiggum loops | 10 per task (max_loops) |

---

## Recommendations

1. **Regenerate tokens periodically** — every 6 months
2. **Review Approved/ before pipeline runs** — check what will be sent
3. **DRY_RUN=true for testing** — set in .env to test without real actions
4. **Monitor watchdog.log** — check for repeated crashes
5. **Review audit-dashboard.md weekly** — spot anomalies in success rates
