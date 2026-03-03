---
name: facebook-instagram-poster
description: Draft and post content to Facebook and Instagram with human approval.
Use this skill for social media automation, business posting, content scheduling,
and Facebook/Instagram management. Always creates approval request first.
Never posts without human confirmation. Uses Playwright browser automation.
---

# Facebook + Instagram Poster

## Role
Tu AI Employee ka Social Media specialist hai. Facebook aur Instagram pe
business content post karta hai — hamesha human approval ke baad.

---

## Scripts

| Script | Kaam |
|--------|------|
| `scripts/facebook_poster.py` | Facebook pe post karo |
| `scripts/instagram_poster.py` | Instagram pe post karo |

---

## Workflow

```
1. Claude post content draft karta hai
2. Approval file banata hai → /Pending_Approval/
3. Human file ko /Approved/ mein move karta hai
4. Script automatically post publish karta hai
5. File /Done/ mein move ho jati hai
```

---

## Approval File Format

Claude yahan create karta hai:
`/Pending_Approval/FACEBOOK_YYYYMMDD_HHMMSS.md`
`/Pending_Approval/INSTAGRAM_YYYYMMDD_HHMMSS.md`

```
---
type: approval_request
action: facebook_post / instagram_post
platform: facebook / instagram
content_preview: FIRST_100_CHARS
created: ISO_TIMESTAMP
expires: ISO_TIMESTAMP_PLUS_24H
status: pending
---

## Post Content
FULL_POST_CONTENT_HERE

## To APPROVE
Move this file to /Approved/ folder

## To REJECT
Move this file to /Rejected/ folder
```

---

## Environment Variables (.env)

```
FB_EMAIL=your@email.com
FB_PASSWORD=yourpassword
FB_PAGE_URL=https://www.facebook.com/YourPageName
IG_USERNAME=your_instagram_username
IG_PASSWORD=yourpassword
DRY_RUN=false
```

---

## Run Commands

```bash
# Facebook test post
python Skills/facebook-instagram-poster/scripts/facebook_poster.py --test

# Instagram test post
python Skills/facebook-instagram-poster/scripts/instagram_poster.py --test

# Approved file se post karo
python Skills/facebook-instagram-poster/scripts/facebook_poster.py Approved/FACEBOOK_file.md
python Skills/facebook-instagram-poster/scripts/instagram_poster.py Approved/INSTAGRAM_file.md
```

---

## HITL Rules

- Hamesha /Pending_Approval/ mein draft banao pehle
- Kabhi bhi bina approval ke post mat karo
- Approval expire hoti hai 24 ghante mein
- DRY_RUN=true se test karo pehle
