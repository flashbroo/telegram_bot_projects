import os
from dotenv import load_dotenv

load_dotenv()

# -------------------- BASIC CONFIG --------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))      # MUST be integer
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")

# -------------------- PAYMENT CONFIG --------------------
UPI_ID = os.getenv("UPI_ID", "")                  # e.g. flashbro@ybl
PAYPAL_LINK = os.getenv("PAYPAL_LINK", "")        # PayPal.me/xyz
TELEGRAM_PROVIDER_TOKEN = os.getenv("TELEGRAM_PROVIDER_TOKEN", "")

# -------------------- DATABASE --------------------
DB_PATH = os.getenv("DB_PATH", "bot.db")

# FREE MODE (1 = everyone allowed)
FREE_MODE = int(os.getenv("FREE_MODE", "0"))

# Logs (optional)
FORWARD_LOG_FILE = "forward_logs.txt"


# -------------------- PLANS (ONLY EDIT HERE!) --------------------
PLANS = {
    "basic": {
        "name": "Basic Subscription",
        "prices": {"INR": 60, "USD": 1},
        "currency": "INR",
        "duration_days": 30,
        "features": "Basic forwarding (text+media)"
    },
    "premium": {
        "name": "Premium Monthly",
        "prices": {"INR": 120, "USD": 3},
        "currency": "INR",
        "duration_days": 30,
        "features": "Full forwarding + filters"
    },
    "premium_yearly": {
        "name": "Premium Yearly",
        "prices": {"INR": 1200, "USD": 30},
        "currency": "INR",
        "duration_days": 365,
        "features": "All premium features for 1 year"
    }
}
