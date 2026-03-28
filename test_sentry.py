import sentry_sdk
import logging

# --- INIT ---
sentry_sdk.init(
    dsn="https://6c1535fc3d0469fcda972bdfba7cd748@o4511108342022145.ingest.us.sentry.io/4511123823525888",
    send_default_pii=True,
    enable_logs=True,
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
)

# --- PERFORMANCE PROFILING ---
def slow_function():
    import time
    time.sleep(0.1)
    return "done"

def fast_function():
    import time
    time.sleep(0.05)
    return "done"

sentry_sdk.profiler.start_profiler()
for i in range(0, 10):
    slow_function()
    fast_function()
sentry_sdk.profiler.stop_profiler()

# --- LOGS ---
sentry_sdk.logger.info("This is an info log message")
sentry_sdk.logger.warning("This is a warning message")
sentry_sdk.logger.error("This is an error message")

# --- PYTHON LOGGING ---
logger = logging.getLogger(__name__)
logger.info("This will be sent to Sentry")
logger.warning("User login failed")
logger.error("Something went wrong")

# --- METRICS ---
from sentry_sdk import metrics
metrics.count("checkout.failed", 1)
metrics.gauge("queue.depth", 42)
metrics.distribution("cart.amount_usd", 187.5)

# --- TRIGGER A REAL ERROR ---
try:
    division_by_zero = 1 / 0
except ZeroDivisionError as e:
    sentry_sdk.capture_exception(e)
    print("✅ Error captured and sent to Sentry")

# --- FLUSH BEFORE EXIT ---
sentry_sdk.flush(timeout=5)
print("✅ All done — check your Sentry dashboard!")
