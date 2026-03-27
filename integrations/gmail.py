from googleapiclient.discovery import build
from utils.google_auth import get_credentials

def get_unread_emails():
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me", labelIds=["UNREAD"], maxResults=5
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        return "No unread emails!"

    reply = f"You have {len(messages)} unread emails:\n"

    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata"
        ).execute()
        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        reply += f"- {headers.get('Subject', 'No Subject')} from {headers.get('From', 'Unknown')}\n"

    return reply
