# --- Edit these values ---
BOT_TOKEN = "8439266642:AAFzBEKL5pt_L6NFMyTvQQQaXfh0BcDumBc"

ADMIN_ID = 717813316  # your Telegram user id (int)

DB_PATH = "bot.db"    # sqlite DB file

DEFAULT_CURRENCY = "INR"  # used in invoices

# Forward logs file path
FORWARD_LOG_FILE = "logs/forward.log"

#UPI and PayPal Settings
UPI_ID = "flashbro@ybl"
UPI_NAME = "Flash Bro"
PAYPAL_LINK = ""
ADMIN_USERNAME = "flash_bro"


#Enable Upi for Payment
ENABLE_UPI= True

# PLANS (canonical)
PLANS = {
    "basic": {
        "name": "Basic",
        "price": 60,
        "currency": "INR",
        "paypal_price_usd": 10,            # NEW
        "duration_days": 30,
        "features": "Text only",
    },
    "premium": {
        "name": "Premium",
        "price": 120,
        "currency": "INR",
        "paypal_price_usd": 20,            # NEW
        "duration_days": 30,
        "features": "All Media",
    },
    "premium_yearly": {
        "name": "Premium Yearly",
        "price": 999,
        "currency": "INR",
        "paypal_price_usd": 150,           # NEW
        "duration_days": 365,
        "features": "All Media + Yearly",
    }
}

#DEFAULT_TARGETS = ["@your_target_channel"]
FREE_MODE = False  # if True, everyone can use the bot (runtime toggle via admin)

REQUIRED_CHANNELS = ["@flashbro_bot_updates"] 

# Payment provider payload - for Telegram Payments set provider token here (from BotFather instructions)
#TELEGRAM_PROVIDER_TOKEN = ""  # leave empty if not using telegram payments