import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
]

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

auth_url, _ = flow.authorization_url(prompt='consent')
print("Visit this URL to authorize:\n")
print(auth_url)

code = input("\nEnter the authorization code: ").strip()
flow.fetch_token(code=code)
creds = flow.credentials

with open('token.json', 'w') as f:
    json.dump(json.loads(creds.to_json()), f, indent=2)

print("token.json created successfully!")

