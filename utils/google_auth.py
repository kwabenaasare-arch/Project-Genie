from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly"
]

def get_credentials():
    creds = Credentials.from_authorized_user_file("credentials/token.json", SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds
