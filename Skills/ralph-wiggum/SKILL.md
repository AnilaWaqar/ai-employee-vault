---
name: ralph-wiggum
description: Autonomous self-prompting loop. Claude keeps working on a task
until completion, re-injecting itself via Stop Hook. Use for long multi-step tasks.
---

# Ralph Wiggum Loop

## Role
Tu AI Employee ka Autonomous Agent hai. Ek baar task start ho toh
khud hi loop karta rehta hai jab tak task complete nahi hota.

---

## How It Works

```
1. start_task.py se task shuru karo
2. Claude task pe kaam karta hai
3. Claude rukta hai → Stop Hook chalti hai
4. Hook check karta hai: Done/ mein done_marker hai?
   - YES → Claude band ho jaata hai (task complete)
   - NO  → Hook Claude ko re-inject karta hai → loop continue
5. Max loops (default 10) ke baad automatically stop
```

---

## Scripts

| Script | Kaam |
|--------|------|
| `scripts/ralph_hook.py` | Stop Hook — Claude Code se register |
| `scripts/start_task.py` | Naya autonomous task shuru karo |

---

## Task File Format (`.current_task`)

```json
{
  "task_id": "TASK_EMAIL_001",
  "task": "Process all emails in Needs_Action/",
  "done_marker": "TASK_EMAIL_001_complete",
  "started": "2026-03-03T10:00:00",
  "max_loops": 10,
  "loop_count": 0
}
```

---

## Usage

```bash
# Task shuru karo
python Skills/ralph-wiggum/scripts/start_task.py "Process emails" TASK_001

# Claude automatically loop karega
# Task complete hone par Done/ mein file banao:
# Done/TASK_001_complete.md
```

---

## Hook Registration

`~/.claude/settings.json` mein:
```json
"hooks": {
  "Stop": [{
    "matcher": "",
    "hooks": [{"type": "command",
    "command": "python E:/HC/AI_Employee_Vault/Skills/ralph-wiggum/scripts/ralph_hook.py"}]
  }]
}
```

---

## Rules

- Max 10 loops (configurable) — infinite loop se bachao
- Task complete hone par HAMESHA done marker file banao
- `.current_task` delete ho jaata hai automatically jab task done ho
