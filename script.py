from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json')
gmail = build('gmail', 'v1', credentials=creds)
calendar = build('calendar', 'v3', credentials=creds)
