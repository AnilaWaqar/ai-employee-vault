---
name: email-mcp
description: Send, draft, and search emails via Gmail
  using the Email MCP server. Use this skill whenever
  Claude needs to send an email, create an email draft,
  or search inbox. Always requires human approval before
  sending. Never sends without /Approved/ file present.
---

# Email MCP Server

## Overview
Gmail ke saath kaam karne ke liye MCP (Model Context Protocol) server.
Claude Code directly email send, draft, aur search kar sakta hai.

## Tools Available

| Tool | Description |
|------|-------------|
| `send_email` | Gmail se email bhejta hai — /Approved/ file zaroori |
| `draft_email` | Draft /Plans/ mein save karta hai |
| `search_emails` | Gmail inbox search karta hai |

## Rules
- `send_email` sirf tab kaam karta hai jab /Approved/ mein file ho
- Kabhi bhi human approval ke baghair email mat bhejo
- DRY_RUN=true pe sirf log hoga, kuch nahi bhejega
- Har action audit log mein save hoti hai

## Setup

### 1. Dependencies install karo
```bash
cd E:\HC\AI_Employee_Vault\email-mcp
npm install
```

### 2. .env fill karo
```
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

### 3. Claude Code mcp.json update karo
```json
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["E:/HC/AI_Employee_Vault/email-mcp/index.js"]
    }
  }
}
```

### 4. Test karo
```bash
node E:\HC\AI_Employee_Vault\email-mcp\index.js
```

## Gmail App Password Kaise Banayein
1. Google Account → Security
2. 2-Step Verification → App Passwords
3. "Mail" ke liye password generate karo
4. `email-mcp/.env` mein paste karo
