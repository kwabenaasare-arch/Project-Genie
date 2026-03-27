from googleapiclient.discovery import build
from utils.google_auth import get_credentials
from datetime import datetime, timezone

def get_todays_events():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    now = datetime.now(timezone.utc).isoformat()
    today_end = datetime.now(timezone.utc).replace(
        hour=23, minute=59, second=59
    ).isoformat()

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=today_end,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    if not events:
        return "No events scheduled for today!"

    reply = f"You have {len(events)} event(s) today:\n"

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        reply += f"- {event['summary']} at {start}\n"

    return reply
