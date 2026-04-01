import os
import sys
import logging
import threading
import sentry_sdk
from flask import Flask
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from apscheduler.schedulers.background import BackgroundScheduler
from ai_helper import get_ai_response
from integrations.gmail import get_unread_emails
from integrations.calendar import get_todays_events
from integrations.linear import get_pending_issues
from briefing import get_briefing

# --- Logging -----------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# --- Environment -------------------------------------------------------------

load_dotenv()

REQUIRED_ENV_VARS = [
    "SLACK_BOT_TOKEN",
    "SLACK_APP_TOKEN",
    "SLACK_USER_ID",
    "GROQ_API_KEY",
    "LINEAR_API_KEY",
    "SENTRY_DSN",
]

missing = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
if missing:
    logger.critical("Missing required environment variables: %s", ", ".join(missing))
    sys.exit(1)

# --- Sentry ------------------------------------------------------------------

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    send_default_pii=False,
    enable_logs=True,
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
)

# --- Flask health endpoint ---------------------------------------------------

health_app = Flask(__name__)

@health_app.route("/health")
def health():
    return "", 200

# --- Slack bot ---------------------------------------------------------------

app = App(token=os.environ["SLACK_BOT_TOKEN"])
SLACK_USER_ID = os.environ["SLACK_USER_ID"]

HELP_TEXT = (
    "Hello! I am Genie, your personal assistant. "
    "Here is what I can do for you:\n\n"
    "📧  *emails* — I will pull up your latest unread emails\n"
    "📅  *calendar* — I will show you what is on your schedule today\n"
    "🌅  *briefing* — I will give you a full morning summary\n"
    "📋  *linear* — I will show you your pending Linear issues\n"
    "💬  *anything else* — Just ask and I will do my best to help\n\n"
    "I am here to make your day a little easier. What do you need?"
)

THINKING_TEXT = "I'm pondering over this I'll be with you shortly boss."

ERROR_TEXT = (
    "I ran into a small issue retrieving that for you. "
    "Please try again in a moment."
)


def send_briefing():
    logger.info("Sending morning briefing...")
    try:
        briefing = get_briefing()
        app.client.chat_postMessage(channel=SLACK_USER_ID, text=briefing)
        logger.info("Briefing sent successfully.")
    except Exception as e:
        logger.error("Briefing failed: %s", e)
        sentry_sdk.capture_exception(e)


def route(text, say):
    say(THINKING_TEXT)
    try:
        if "email" in text:
            result = get_unread_emails()
            say("📧 *Here are your latest unread emails:*\n\n" + result)
        elif "calendar" in text:
            result = get_todays_events()
            say("📅 *Here is your schedule for today:*\n\n" + result)
        elif "linear" in text:
            result = get_pending_issues()
            say("📋 *Here are your pending Linear issues:*\n\n" + result)
        elif "briefing" in text:
            result = get_briefing()
            say(result)
        elif "help" in text:
            say(HELP_TEXT)
        else:
            result = get_ai_response(text)
            say(result)
    except Exception as e:
        logger.error("Route error: %s", e)
        sentry_sdk.capture_exception(e)
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
    threading.Thread(
        target=lambda: health_app.run(host="0.0.0.0", port=8080),
        daemon=True,
    ).start()

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_briefing, "cron", hour=7, minute=30, timezone="GMT")
    scheduler.start()

    logger.info("----------------------------------------")
    logger.info("  Genie Personal Assistant")
    logger.info("  Status   : Running")
    logger.info("  Briefing : 7:30 AM GMT daily")
    logger.info("----------------------------------------")

    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
