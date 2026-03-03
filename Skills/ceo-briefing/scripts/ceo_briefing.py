"""
CEO Briefing — Gold Tier Feature 5
Comprehensive weekly/daily briefing with:
- System status (all folders)
- Odoo revenue data
- Social media activity (FB, IG, Twitter)
- Google Calendar upcoming events
- Proactive suggestions
"""

import os
import re
import json
import logging
import xmlrpc.client
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────
VAULT = Path("E:/HC/AI_Employee_Vault")
load_dotenv(VAULT / ".env")

ODOO_URL      = os.getenv("ODOO_URL", "http://localhost")
ODOO_PORT     = os.getenv("ODOO_PORT", "8069")
ODOO_DB       = os.getenv("ODOO_DB", "odoo_ai_employee")
ODOO_USER     = os.getenv("ODOO_USER", "")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "")

BRIEFINGS_DIR = VAULT / "Briefings"
LOGS_DIR      = VAULT / "Logs"
DONE_DIR      = VAULT / "Done"
PLANS_DIR     = VAULT / "Plans"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CEO-BRIEFING] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "ceo_briefing.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("ceo-briefing")


# ── Folder Counts ─────────────────────────────────────────────────────────────
def get_folder_counts() -> dict:
    folders = {
        "Needs_Action":     VAULT / "Needs_Action",
        "Drafts":           VAULT / "Drafts",
        "Pending_Approval": VAULT / "Pending_Approval",
        "Approved":         VAULT / "Approved",
        "Done":             VAULT / "Done",
        "Rejected":         VAULT / "Rejected",
        "Plans":            VAULT / "Plans",
        "Briefings":        BRIEFINGS_DIR,
    }
    return {name: len(list(path.glob("*.md"))) for name, path in folders.items() if path.exists()}


# ── Odoo Revenue ──────────────────────────────────────────────────────────────
def get_odoo_revenue() -> dict:
    result = {"total_invoiced": 0, "invoice_count": 0, "paid": 0, "unpaid": 0, "error": None}
    try:
        base_url = f"{ODOO_URL}:{ODOO_PORT}"
        common = xmlrpc.client.ServerProxy(f"{base_url}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            result["error"] = "Odoo login failed"
            return result

        models = xmlrpc.client.ServerProxy(f"{base_url}/xmlrpc/2/object")

        # This month invoices
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")

        invoices = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "account.move", "search_read",
            [[["move_type", "=", "out_invoice"], ["invoice_date", ">=", month_start]]],
            {"fields": ["name", "amount_total", "payment_state", "state"], "limit": 100}
        )

        for inv in invoices:
            if inv["state"] in ("posted", "paid"):
                result["invoice_count"] += 1
                result["total_invoiced"] += inv["amount_total"]
                if inv["payment_state"] == "paid":
                    result["paid"] += inv["amount_total"]
                else:
                    result["unpaid"] += inv["amount_total"]

    except Exception as e:
        result["error"] = str(e)
        log.warning(f"Odoo data fetch failed: {e}")

    return result


# ── Social Media Stats ────────────────────────────────────────────────────────
def get_social_stats() -> dict:
    stats = {"facebook": 0, "instagram": 0, "twitter": 0, "linkedin": 0, "total": 0}
    cutoff = datetime.now() - timedelta(days=7)

    try:
        for f in DONE_DIR.glob("SENT_*.md"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                continue
            name = f.name.upper()
            if "FACEBOOK" in name:
                stats["facebook"] += 1
            elif "INSTAGRAM" in name:
                stats["instagram"] += 1
            elif "TWITTER" in name:
                stats["twitter"] += 1
            elif "LINKEDIN" in name:
                stats["linkedin"] += 1
        stats["total"] = sum(v for k, v in stats.items() if k != "total")
    except Exception as e:
        log.warning(f"Social stats error: {e}")

    return stats


# ── Calendar Events ───────────────────────────────────────────────────────────
def get_upcoming_events() -> list:
    events = []
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        token_path = VAULT / "Skills/gmail-watcher/assets/token.json"
        if not token_path.exists():
            return events

        token = json.loads(token_path.read_text(encoding="utf-8"))
        creds = Credentials.from_authorized_user_info(token)
        service = build("calendar", "v3", credentials=creds)

        now = datetime.utcnow().isoformat() + "Z"
        future = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

        result = service.events().list(
            calendarId="primary",
            timeMin=now,
            timeMax=future,
            maxResults=5,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        for e in result.get("items", []):
            start = e["start"].get("dateTime", e["start"].get("date", ""))
            events.append({"title": e.get("summary", "No title"), "start": start})

    except Exception as e:
        log.warning(f"Calendar fetch failed: {e}")

    return events


# ── Weekly Activity from Logs ─────────────────────────────────────────────────
def get_week_activity() -> dict:
    stats = {"emails_sent": 0, "drafts": 0, "whatsapp": 0, "total_actions": 0, "active_days": 0}
    for i in range(7):
        day = datetime.now() - timedelta(days=i)
        log_file = LOGS_DIR / f"{day.strftime('%Y-%m-%d')}.md"
        if not log_file.exists():
            continue
        stats["active_days"] += 1
        try:
            text = log_file.read_text(encoding="utf-8").lower()
            stats["emails_sent"] += len(re.findall(r"email sent|send_email.*sent", text))
            stats["drafts"]      += len(re.findall(r"draft created", text))
            stats["whatsapp"]    += len(re.findall(r"whatsapp.*created", text))
            actions = re.findall(r"^###\s+\d{2}:\d{2}:\d{2}", log_file.read_text(encoding="utf-8"), re.MULTILINE)
            stats["total_actions"] += len(actions)
        except Exception:
            pass
    return stats


# ── Proactive Suggestions ─────────────────────────────────────────────────────
def generate_suggestions(counts: dict, odoo: dict, social: dict, activity: dict) -> list:
    suggestions = []

    if counts.get("Needs_Action", 0) > 3:
        suggestions.append(f"📧 {counts['Needs_Action']} emails unprocessed — run /inbox-processor")
    if counts.get("Pending_Approval", 0) > 2:
        suggestions.append(f"🔔 {counts['Pending_Approval']} items need your review in Pending_Approval/")
    if odoo.get("unpaid", 0) > 0:
        suggestions.append(f"💰 PKR {odoo['unpaid']:,.0f} unpaid invoices — follow up with clients")
    if social.get("total", 0) == 0:
        suggestions.append("📱 No social media posts this week — consider posting content")
    if social.get("total", 0) > 0 and social.get("linkedin", 0) == 0:
        suggestions.append("💼 No LinkedIn posts this week — good time to share business updates")
    if activity.get("active_days", 0) < 4:
        suggestions.append("⚠️ System was inactive some days — check PM2 processes")
    if not suggestions:
        suggestions.append("✅ Everything looks good! System running smoothly.")

    return suggestions


# ── Build Briefing ────────────────────────────────────────────────────────────
def create_ceo_briefing() -> Path:
    now = datetime.now()
    log.info("Collecting data for CEO briefing...")

    counts   = get_folder_counts()
    odoo     = get_odoo_revenue()
    social   = get_social_stats()
    calendar = get_upcoming_events()
    activity = get_week_activity()
    suggestions = generate_suggestions(counts, odoo, social, activity)

    # Calendar section
    if calendar:
        cal_lines = "\n".join(f"- **{e['title']}** — {e['start'][:16].replace('T', ' ')}" for e in calendar)
    else:
        cal_lines = "- No upcoming events in next 7 days"

    # Odoo section
    if odoo.get("error"):
        odoo_section = f"- Odoo connection failed: {odoo['error']}"
    else:
        odoo_section = f"""- Invoices this month: **{odoo['invoice_count']}**
- Total invoiced: **PKR {odoo['total_invoiced']:,.0f}**
- Paid: **PKR {odoo['paid']:,.0f}**
- Unpaid: **PKR {odoo['unpaid']:,.0f}**"""

    suggestions_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(suggestions))

    content = f"""---
type: ceo_briefing
created: {now.isoformat()}
date: {now.strftime("%Y-%m-%d")}
week: {(now - timedelta(days=6)).strftime("%Y-%m-%d")} to {now.strftime("%Y-%m-%d")}
---

# CEO Briefing — {now.strftime("%A, %B %d %Y")}

*Generated at {now.strftime("%I:%M %p")} by AI Employee — Gold Tier*

---

## System Status

| Folder | Files |
|--------|-------|
| Needs_Action | {counts.get("Needs_Action", 0)} |
| Drafts | {counts.get("Drafts", 0)} |
| Pending_Approval | {counts.get("Pending_Approval", 0)} |
| Approved (queued) | {counts.get("Approved", 0)} |
| Done (total) | {counts.get("Done", 0)} |
| Rejected | {counts.get("Rejected", 0)} |

---

## Revenue (This Month)

{odoo_section}

---

## Social Media (Last 7 Days)

| Platform | Posts |
|----------|-------|
| Facebook | {social.get("facebook", 0)} |
| Instagram | {social.get("instagram", 0)} |
| Twitter/X | {social.get("twitter", 0)} |
| LinkedIn | {social.get("linkedin", 0)} |
| **Total** | **{social.get("total", 0)}** |

---

## Email Activity (Last 7 Days)

- Active days: **{activity.get("active_days", 0)}/7**
- Emails sent: **{activity.get("emails_sent", 0)}**
- Drafts created: **{activity.get("drafts", 0)}**
- WhatsApp alerts: **{activity.get("whatsapp", 0)}**
- Total AI actions: **{activity.get("total_actions", 0)}**

---

## Upcoming Calendar Events

{cal_lines}

---

## Proactive Suggestions

{suggestions_str}

---

*Next briefing: Sunday 10PM | AI Employee Gold Tier*
"""

    filename = f"CEO_BRIEFING_{now.strftime('%Y%m%d_%H%M')}.md"
    filepath = BRIEFINGS_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    log.info(f"CEO Briefing saved: {filename}")
    return filepath


if __name__ == "__main__":
    briefing = create_ceo_briefing()
    print(f"Briefing created: {briefing}")
    print(briefing.read_text(encoding="utf-8"))
