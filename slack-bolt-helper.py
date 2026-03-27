from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("app_mention")
def handle_mention(event, say):
    say(f"Hello <@{event['user']}>! I'm your PA Bot 🤖")

handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
handler.start()
