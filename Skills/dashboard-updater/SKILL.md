---
name: dashboard-updater
description: Dashboard.md ko update karo latest
  task counts aur recent activity ke saath.
  Use karo jab vault mein koi change ho.
---

# Dashboard Updater

## Overview
Yeh skill Dashboard.md ko real-time
information ke saath update karti hai.

## Steps
1. /Needs_Action folder count karo
2. /Done folder count karo
3. /Logs/ se recent activity padhon
4. Dashboard.md update karo

## Template
```
# AI Employee Dashboard
Last Updated: {timestamp}

## Status
- Pending: {needs_action_count}
- Done Today: {done_count}

## Recent Activity
{recent_logs}
```

## Rules
- Har vault change ke baad update karo
- Timestamp hamesha include karo
- Recent activity ki last 5 entries dikhao
