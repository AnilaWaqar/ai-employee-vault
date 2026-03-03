---
name: gmail-watcher
description: Gmail se unread important emails detect karo
  aur /Needs_Action folder mein .md files banao.
  Use karo jab Gmail monitoring chahiye ho.
---

# Gmail Watcher

## Overview
Yeh skill Gmail API use karke unread emails detect
karti hai aur unhe Obsidian vault mein
actionable files mein convert karti hai.

## Steps
1. Gmail API se unread+important emails fetch karo
2. Har email ke liye /Needs_Action/EMAIL_id.md banao
3. Email content, sender, subject save karo
4. Processed IDs track karo (duplicates se bachne ke liye)
5. Har 120 seconds mein repeat karo

## Rules
- Sirf unread+important emails process karo
- Already processed emails skip karo
- Error pe crash mat karo, log karo aur continue karo
