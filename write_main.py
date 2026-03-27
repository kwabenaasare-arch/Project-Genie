with open('/root/Project-Genie/main.py', 'w') as f:
    f.write("""import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from apscheduler.schedulers.background import BackgroundScheduler
from ai_helper import get_ai_response
from integrations.gmail import get_unread_emails
from integrations.calendar import get_todays_events
from briefing import get_briefing
from datetime import datetime

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])
SLACK_USER_ID = os.environ["SLACK_USER_ID"]

HELP_TEXT = (
    "Hello! I am Genie, your personal assistant. "
    "Here is what I can do for you:\\n\\n"
    "📧  *emails* — I will pull up your latest unread emails\\n"
    "📅  *calendar* — I will show you what is on your schedule today\\n"
    "🌅  *briefing* — I will give you a full morning summary\\n"
    "💬  *anything else* — Just ask and I will do my best to help\\n\\n"
    "I am here to make your day a little easier. What do you need?"
)

THINKING_TEXT = "Got it, give me just a moment."

ERROR_TEXT = (
    "I ran into a small issue retrieving that for you. "
    "Please try again in a moment."
)


def send_briefing():
    now = datetime.now().strftime("%H:%M")
    print("[" + now + "] Sending morning briefing...")
    try:
        briefing = get_briefing()
        app.client.chat_postMessage(channel=SLACK_USER_ID, text=briefing)
        print("Briefing sent successfully.")
    except Exception as e:
        print("Briefing failed: " + str(e))


def route(text, say):
    say(THINKING_TEXT)
    try:
        if "email" in text:
            result = get_unread_emails()
            say("📧 *Here are your latest unread emails:*\\n\\n" + result)
        elif "calendar" in text:
            result = get_todays_events()
            say("📅 *Here is your schedule for today:*\\n\\n" + result)
        elif "briefing" in text:
            result = get_briefing()
            say(result)
        elif "help" in text:
            say(HELP_TEXT)
        else:
            result = get_ai_response(text)
            say(result)
    except Exception as e:
        print("Error: " + str(e))
        say(ERROR_TEXT)


@app.event("app_mention")
def handle_mention(event, say):
    text = event["text"].lower()
    route(text, say)


@app.message()
def handle_message(message, say):
    text = message["text"].lower()
    route(text, say)


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_briefing, "cron", hour=7, minute=30)
    scheduler.start()
    print("----------------------------------------")
    print("  Genie Personal Assistant")
    print("  Status   : Running")
    print("  Briefing : 7:30 AM daily")
    print("----------------------------------------")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
""")
print("Done")
