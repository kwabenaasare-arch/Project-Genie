from googleapiclient.discovery import build
from utils.google_auth import get_credentials
from datetime import datetime, timezone

def get_todays_events():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).isoformat()
    today_end = datetime.now(timezone.utc).replace(
        hour=23, minute=59, second=59, microsecond=0
    ).isoformat()

    events_result = service.events().list(
        calendarId="primary",
        timeMin=today_start,
        timeMax=today_end,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    if not events:
        return "No events scheduled for today!"

    reply = f"You have {len(events)} event(s) today:\n"

    for event in events:
        start_raw = event["start"].get("dateTime", event["start"].get("date"))
        title = event.get("summary", "(No title)")
        try:
            dt = datetime.fromisoformat(start_raw)
            time_str = dt.strftime("%I:%M %p").lstrip("0")
        except ValueError:
            time_str = start_raw
        reply += f"- {title} at {time_str}\n"

    return reply
