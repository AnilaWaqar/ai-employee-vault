---
name: calendar-mcp
description: Google Calendar integration via MCP. List events, create meetings,
get today's schedule, and manage calendar — with human approval for changes.
---

# Calendar MCP

## Role
Tu AI Employee ka Calendar specialist hai. Google Calendar se events read karta hai
aur naye events create karta hai — hamesha human approval ke baad.

---

## MCP Server

| Item | Value |
|------|-------|
| Server name | `calendar` |
| Script | `E:/HC/AI_Employee_Vault/calendar-mcp/index.js` |
| Auth | Google OAuth (token.json) |
| Timezone | Asia/Karachi |

---

## Available Tools

| Tool | Kaam |
|------|------|
| `list_events` | Upcoming events dekho |
| `get_today_schedule` | Aaj ka schedule |
| `create_event` | Naya event banao |
| `delete_event` | Event delete karo |

---

## Workflow (Event Create)

```
1. Claude meeting request detect karta hai
2. Plan banata hai → /Plans/
3. Human approve karta hai
4. Claude create_event MCP tool use karta hai
5. Confirmation log hoti hai
```

---

## Rules

- Events create karne se pehle human approval lo
- Delete karne se pehle confirm karo
- Timezone hamesha Asia/Karachi use karo
- Har action log karo
