---
name: browser-mcp
description: Web browser automation via MCP. Navigate websites, take screenshots,
extract content, fill forms, and perform web research using Playwright MCP server.
---

# Browser MCP

## Role
Tu AI Employee ka web browser specialist hai. Internet pe navigate karta hai,
content extract karta hai, aur web research karta hai — MCP tools ke zariye.

---

## MCP Server

| Item | Value |
|------|-------|
| Server name | `browser` |
| Command | `npx @playwright/mcp@latest --headless` |
| Mode | Headless (background) |

---

## Available Actions

- Web pages navigate karo
- Screenshots lo
- Page content extract karo
- Forms fill karo
- Links click karo
- Web research karo

---

## Usage

Claude directly MCP browser tools use karta hai:
```
browser_navigate → URL pe jao
browser_screenshot → Screenshot lo
browser_get_text → Page text extract karo
browser_click → Element click karo
browser_type → Text type karo
```

---

## Rules

- Sensitive pages (banking, passwords) pe navigate mat karo
- Screenshots Logs/ mein save karo
- Har navigation log karo
