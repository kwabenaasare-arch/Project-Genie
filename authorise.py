import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

TOKEN_PATH = "credentials/token.json"

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)

auth_url, _ = flow.authorization_url(prompt="consent")
print("Visit this URL to authorize:\n")
print(auth_url)

code = input("\nEnter the authorization code: ").strip()
flow.fetch_token(code=code)
creds = flow.credentials

os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
with open(TOKEN_PATH, "w") as f:
    json.dump(json.loads(creds.to_json()), f, indent=2)

print(f"\nToken saved to {TOKEN_PATH}")
