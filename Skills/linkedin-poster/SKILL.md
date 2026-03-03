---
name: linkedin-poster
description: Draft and post business content to LinkedIn
  with human approval. Use this skill for LinkedIn
  automation, business posting, content scheduling,
  and social media management. Always creates approval
  request first. Never posts without human confirmation.
---

# LinkedIn Auto-Poster

## Overview
Yeh skill Claude ko LinkedIn pe posts karne ki ability deti hai.
Claude pehle draft banata hai, human approve karta hai, phir
Playwright automatically LinkedIn pe post karta hai.

## Steps
1. Claude post content likhta hai
2. `Pending_Approval/LINKEDIN_YYYYMMDD_HHMMSS.md` file banata hai
3. Human file ko `Approved/` mein move karta hai
4. `linkedin_poster.py` watch karta hai `Approved/` folder
5. Approved file mile toh Playwright se LinkedIn pe post karta hai
6. Post ke baad file `Done/` mein move hoti hai
7. Har action `Logs/` mein log hota hai

## Run Command
```bash
python Skills/linkedin-poster/scripts/linkedin_poster.py
```

## Rules
- Kabhi bhi bina `/Approved/` file ke post mat karo
- Pehli baar LinkedIn login karke session `linkedin_session/` mein save karo
- `DRY_RUN=true` pe post mat karo, sirf log karo
- Har post attempt audit log mein record karo
- Max 20 posts per hour (rate limit)
- Post content 3000 characters se zyada nahi hona chahiye

## Approval File Format
`Pending_Approval/LINKEDIN_YYYYMMDD_HHMMSS.md`

## Environment Variables
```
VAULT_PATH=E:/HC/AI_Employee_Vault
DRY_RUN=false
MAX_ACTIONS_PER_HOUR=20
```
