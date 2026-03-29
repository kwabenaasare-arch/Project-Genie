from integrations.gmail import get_unread_emails
from integrations.calendar import get_todays_events
from ai_helper import get_ai_response
from datetime import datetime


def get_briefing():
    emails = get_unread_emails()
    calendar = get_todays_events()
    day = datetime.now().strftime("%A, %B %d")

    prompt = (
        "You are Genie, a warm and professional personal assistant. "
        "Write a morning briefing for today " + day + ". "
        "Use the data below. Be friendly, clear and encouraging. "
        "List ALL calendar events — do not skip or summarize any of them. "
        "Start with Good Morning and end with a motivating closing line.\n\n"
        "EMAILS:\n" + emails + "\n\n"
        "CALENDAR:\n" + calendar
    )

    return get_ai_response(prompt)
