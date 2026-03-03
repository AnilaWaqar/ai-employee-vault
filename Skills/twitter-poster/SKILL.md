---
name: twitter-poster
description: Draft and post tweets to Twitter/X with human approval.
Use this skill for Twitter automation, business tweets, announcements,
and X platform management. Always creates approval request first.
Never posts without human confirmation. Uses Twitter API v2 (Tweepy).
---

# Twitter/X Poster

## Role
Tu AI Employee ka Twitter/X specialist hai. Twitter pe business content
post karta hai — hamesha human approval ke baad. 280 characters ka limit yaad rakh.

---

## Scripts

| Script | Kaam |
|--------|------|
| `scripts/twitter_poster.py` | Tweet post karo via API |

---

## Workflow

```
1. Claude tweet content draft karta hai (max 280 chars)
2. Approval file banata hai → /Pending_Approval/
3. Human file ko /Approved/ mein move karta hai
4. Script automatically tweet publish karta hai
5. File /Done/ mein move ho jati hai
```

---

## Approval File Format

Claude yahan create karta hai:
`/Pending_Approval/TWITTER_YYYYMMDD_HHMMSS.md`

```
---
type: approval_request
action: tweet_post
platform: twitter
char_count: TWEET_LENGTH
created: ISO_TIMESTAMP
expires: ISO_TIMESTAMP_PLUS_24H
status: pending
---

## Tweet Content
FULL_TWEET_TEXT_HERE (max 280 chars)

## To APPROVE
Move this file to /Approved/ folder

## To REJECT
Move this file to /Rejected/ folder
```

---

## Environment Variables (.env)

```
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token
DRY_RUN=false
```

---

## Twitter Developer Setup

1. developer.twitter.com pe jao
2. Project + App banao
3. App settings mein **Read and Write** permissions set karo
4. Keys and Tokens tab se sabhi keys copy karo
5. .env mein paste karo

---

## Run Commands

```bash
# Test tweet (credentials check)
python Skills/twitter-poster/scripts/twitter_poster.py --test

# Approved file se tweet karo
python Skills/twitter-poster/scripts/twitter_poster.py Approved/TWITTER_file.md
```

---

## HITL Rules

- Hamesha /Pending_Approval/ mein draft banao pehle
- Kabhi bhi bina approval ke tweet mat karo
- Tweet 280 chars se zyada nahi hona chahiye
- Approval expire hoti hai 24 ghante mein
- DRY_RUN=true se test karo pehle

---

## Tweet Writing Rules

- Max 280 characters — count karo pehle
- Relevant hashtags lagao (2-3 max)
- Business tone — professional aur engaging
- Emojis allowed but professional rakho
- URL lagani ho toh 23 chars count hoti hai Twitter mein
