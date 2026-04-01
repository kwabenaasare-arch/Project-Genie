import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

TOKEN_PATH = "credentials/token.json"


def get_credentials() -> Credentials:
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    except FileNotFoundError:
        raise RuntimeError(
            f"Google OAuth token not found at '{TOKEN_PATH}'. "
            "Run authorise.py to generate it."
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load Google credentials: {e}") from e

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError as e:
            raise RuntimeError(
                "Google OAuth token has expired and could not be refreshed. "
                "Run authorise.py to re-authorise."
            ) from e

    return creds
