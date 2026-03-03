---
type: audit_dashboard
generated: 2026-03-03T07:36:36.738030
period: Last 30 days
---

# Audit Dashboard

*Auto-generated: 2026-03-03 07:36 | AI Employee Gold Tier*

---

## Overview

| Metric | Value |
|--------|-------|
| Total Actions | 30 |
| Successful | 12 |
| Failed | 18 |
| Dry Run (skipped) | 0 |
| **Success Rate** | **40%** |

---

## By Actor (Last 30 Days)

| Actor | Success | Failed | Rate |
|-------|---------|--------|------|
| claude | 5 | 0 | 100% |
| facebook-poster | 5 | 6 | 45% |
| instagram-poster | 1 | 6 | 14% |
| twitter-poster | 1 | 6 | 14% |

---

## By Action Type

| Action | Success | Failed |
|--------|---------|--------|
| draft_email | 2 | 0 |
| facebook_post | 5 | 6 |
| instagram_post | 1 | 6 |
| search_emails | 1 | 0 |
| send_email | 2 | 0 |
| tweet_post | 1 | 6 |

---

## Daily Activity (Last 7 Days)

| Date | Actions | Chart |
|------|---------|-------|
| 2026-02-25 | 0 | · |
| 2026-02-26 | 0 | · |
| 2026-02-27 | 0 | · |
| 2026-02-28 | 0 | · |
| 2026-03-01 | 2 | ██ |
| 2026-03-02 | 18 | ██████████████████ |
| 2026-03-03 | 7 | ███████ |

---

## Recent Errors (Last 10)

| Time | Actor | Error |
|------|-------|-------|
| 2026-03-02 09:39 | facebook-poster | timeout: Page.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator |
| 2026-03-02 09:40 | facebook-poster | timeout: Page.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator |
| 2026-03-02 09:41 | facebook-poster | error: EOF when reading a line |
| 2026-03-02 09:43 | facebook-poster | failed_no_postbtn |
| 2026-03-02 09:58 | facebook-poster | failed_no_postbtn |
| 2026-03-02 10:03 | facebook-poster | failed_no_postbtn |
| 2026-03-02 10:07 | instagram-poster | failed_no_newpost |
| 2026-03-02 10:08 | instagram-poster | failed_no_newpost |
| 2026-03-02 10:13 | instagram-poster | failed_no_newpost |
| 2026-03-02 10:14 | instagram-poster | failed_no_newpost |

---

## Recent Activity (Last 5)

| Time | Actor | Action | Result |
|------|-------|--------|--------|
| 2026-03-02 09:39 | facebook-poster | facebook_post | timeout: Page.click: Timeout 30000ms exceeded.
Cal |
| 2026-03-02 09:40 | facebook-poster | facebook_post | timeout: Page.click: Timeout 30000ms exceeded.
Cal |
| 2026-03-02 09:41 | facebook-poster | facebook_post | error: EOF when reading a line |
| 2026-03-02 09:43 | facebook-poster | facebook_post | failed_no_postbtn |
| 2026-03-02 09:45 | facebook-poster | facebook_post | success |

---

*Next update: Run `python Skills/audit-logger/scripts/audit_dashboard.py`*
