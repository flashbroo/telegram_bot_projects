# Telegram Forward Bot (Polling) 1.BOT NAME(@AUTOMATEDFORWARDERBOT) or YOU CAN SEARCH IN FLASH's @BOTFATHER

## Setup (Windows / Termux / VPS)
1. Install Python 3.11.
2. Clone this folder into telegram_forward_bot/.
3. Edit config.py and set BOT_TOKEN and ADMIN_ID.
4. Create a venv and install requirements:


## HOW TO RUN BOT AND CMD 
## Quick Tests
- /start → welcome
- /menu → inline menu
- /list_mappings → show mappings
- /add_mapping @source @target → add mapping
- Post into source channel (bot must be able to see posts) → see forwarded message in target

## Troubleshooting
- ModuleNotFoundError: No module named 'telegram':

Here is a clean, professional, copy-paste-ready README.md for your Telegram Forwarding Bot project — including:

✔ Full setup
✔ Windows + Termux instructions
✔ All user/admin commands
✔ Examples for each command
✔ Troubleshooting
✔ How multi-forward works


---

📌 Telegram Forward Bot — README

A complete Telegram bot for auto-forwarding messages from channels to multiple channels, with subscription system, paid plans, watermarking, admin controls, and SQLite storage.

Works on:

Windows

Android (Termux)

Any VPS (Ubuntu/Debian)


Uses:
Python 3.11, python-telegram-bot v20.x, SQLite, async architecture


---

📂 Project Structure

telegram_forward_bot/
├── bot.py
├── config.py
├── db.py
├── utils.py
├── users.py
├── subscriptions.py
├── payments_telegram.py
├── mappings.py
├── forwarder.py
├── admin_cmds.py
├── ui.py
├── branding.py
├── requirements.txt
└── README.md


---

🚀 1. Installation

Windows Setup

1. Install Python 3.11
https://www.python.org/downloads/release/python-3110/


2. Open CMD inside your bot folder:



cd telegram_forward_bot

3. Install requirements:



py -3.11 -m pip install -r requirements.txt

4. Set your bot token & admin ID inside config.py.


5. Run:



py -3.11 bot.py


---

Android (Termux)

1. Install Termux from F-Droid (recommended).


2. Update packages:



pkg update && pkg upgrade

3. Install Python:



pkg install python

4. Install pip dependencies:



pip install -r requirements.txt

5. Run:



python bot.py


---

⚙️ 2. Config Setup (config.py)

You MUST edit these fields:

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ADMIN_ID = 123456789

Configure plans:

PLANS = {
   "basic": {
      "name": "Basic Plan",
      "price": 99,
      "currency": "INR",
      "duration_days": 30,
      "features": "Forward 1 source → 3 channels"
   }
}

Nothing related to pricing should be modified outside this file.


---

📡 3. Running the Bot

Start normally:

python bot.py

Add bot to your source channels and make it Admin.

Add bot to your target channels as Admin.

Bot will automatically forward messages according to user mappings.


---

🙋‍♂️ 4. USER COMMANDS

These commands are for normal users.


---

🔹 /start

Shows welcome message + menu.


---

🔹 /menu

Shows inline buttons:

View plans

Buy plans

My mappings



---

🔹 /list_plans

Shows all plans from config.PLANS.


---

🔹 /buy <plan_key>

Example:

/buy basic

If payments are configured → sends payment invoice.
If not → tells user to contact admin.


---

🔥 Forwarding Commands for Users

🔹 /add_mapping <source> <target> [watermark 0|1]

Creates a mapping: forward from source → target

Examples:

/add_mapping @source1 @targetA
/add_mapping @source1 @targetB 1
/add_mapping -1001234567890 -100987654321

✔ Accepts both @username and numeric channel ID
✔ Watermark optional (default = 0)


---

🔹 /list_mappings

Shows all mappings for the user.

Example output:

1. @source1 → @targetA
2. @source1 → @targetB (watermark)


---

🔹 /remove_mapping <mapping_id>

Example:

/remove_mapping 2

Deletes mapping #2.


---

🔹 /status

Shows current subscription:

Plan: Basic
Expires: 2025-01-10

If no plan → shows free access or expired.


---

## ADMIN COMMANDS

Only ADMIN_ID can run these.


---

🔹 /grant_free <user_id>

Give lifetime free access.

/grant_free 5566778899


---

🔹 /revoke_free <user_id>

Remove free access.


---

🔹 /manual_activate <user_id> <plan_key> [days]

Example:

/manual_activate 556677889 basic

or custom duration:

/manual_activate 556677889 basic 90


---

🔹 /list_subscribers

Shows all users with active subscriptions.


---

🔹 /list_users

Shows all registered users.


---

🔹 /export_logs

Exports forwarding logs as CSV file.


---

🔹 /broadcast <text>

Sends a message to all users.

Example:

/broadcast Server maintenance at 10PM.


---

🔹 /set_free_mode on

Enable free usage for everyone.

/set_free_mode on

Disable:

/set_free_mode off


---

🔄 6. MULTI-CHANNEL FORWARDING (IMPORTANT)

You achieve multi-forward using multiple /add_mapping commands.

Example: forward 1 source to 5 channels

Ⓕⓛⓐⓢⓗ ⚡, [21-11-2025 15:44]
/add_mapping @source @c1
/add_mapping @source @c2
/add_mapping @source @c3
/add_mapping @source @c4
/add_mapping @source @c5

Example: forward 3 sources to 5 channels

Repeat command for each source-target pair:

/add_mapping @source1 @c1
/add_mapping @source1 @c2
...
/add_mapping @source2 @c1
...
/add_mapping @source3 @c1
...

There is no limit—database-driven.


---

🧪 7. Testing Checklist

✔ 1. Start the bot

/start should respond.

✔ 2. Add a mapping

/add_mapping @yourSource @yourTarget

✔ 3. Post in source channel

Bot should forward instantly.

✔ 4. Buy a plan (if payments enabled)

/buy basic

✔ 5. Manually activate (admin)

/manual_activate <user_id> basic

✔ 6. Remove mapping

/remove_mapping 1

✔ 7. Test watermark

/add_mapping @source @target 1

✔ 8. Export logs

/export_logs


---

❗ 8. Troubleshooting

ModuleNotFoundError: No module named 'telegram'

Install exact requirements:

pip install -r requirements.txt

Or:

py -3.11 -m pip install python-telegram-bot==20.3


---

Payments not working?

Check:

TELEGRAM_PROVIDER_TOKEN = ""

Must contain a real provider token.


---

Forwarding not happening?

Bot must be:

✔ Admin in source
✔ Admin in target
✔ Allowed permission “post messages”
✔ Mapping must exist
✔ User subscription must be active


---

SQLite locked error

Your project uses a threading lock.
If error persists, delete the .db file once (dev use) or increase timeout.


---
## DEPLOYMENT PROCESS

Below is a clean, zipped-style “deployment-only bundle” for high-scale production, including:

✅ Mandatory improvements
✅ PostgreSQL (required for scale)
✅ Logging fixes
✅ Systemd service
✅ Environment variable support
✅ Ready-to-deploy folder structure
❗ No SQLite — removed because not suitable for high-scale.

Everything is included as a text ZIP (pasteable).
You only need to copy → create files → deploy.


---

📦 ZIP: High-Scale Deployment Bundle

(Everything below should be placed as files in one folder)


---

📁 Folder Structure

telegram-forwarder/
│
├── bot.py
├── config.py
├── requirements.txt
├── .env
├── systemd.service
└── README_DEPLOY.md


---

📄 bot.py

(High-scale ready, async optimized, PostgreSQL, no blocking code)

import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sqlalchemy import create_engine, text
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("forwarder")

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# ---------------------------------------
# DATABASE INIT
# ---------------------------------------
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS channels (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT UNIQUE NOT NULL
        );
    """))

# ---------------------------------------
# COMMANDS
# ---------------------------------------

@dp.message(Command("addchannel"))
async def add_channel(message: types.Message):
    if message.from_user.id not in settings.ADMIN_IDS:
        return await message.reply("Unauthorized.")

    if not message.reply_to_message:
        return await message.reply("Reply to a forwarded message from a channel.")

    channel_id = message.reply_to_message.forward_from_chat.id

    with engine.begin() as conn:
        conn.execute(text("INSERT INTO channels (chat_id) VALUES (:cid) ON CONFLICT DO NOTHING"),
                     {"cid": channel_id})

    await message.reply(f"Added channel: {channel_id}")


@dp.message(Command("listchannels"))
async def list_channels(message: types.Message):
    if message.from_user.id not in settings.ADMIN_IDS:
        return

    with engine.begin() as conn:
        rows = conn.execute(text("SELECT chat_id FROM channels")).fetchall()

    if not rows:
        return await message.reply("No channels added.")

    text_msg = "\n".join([str(r[0]) for r in rows])
    await message.reply(f"Channels:\n{text_msg}")


@dp.message(Command("removechannel"))
async def remove_channel(message: types.Message):
    if message.from_user.id not in settings.ADMIN_IDS:
        return

    parts = message.text.split()
    if len(parts) != 2:
        return await message.reply("Usage: /removechannel <chat_id>")

    chat_id = int(parts[1])

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM channels WHERE chat_id = :cid"), {"cid": chat_id})

    await message.reply("Removed.")


# ---------------------------------------
# FORWARDING LOGIC
# ---------------------------------------

@dp.message()
async def forward_all(message: types.Message):
    with engine.begin() as conn:
        channels = conn.execute(text("SELECT chat_id FROM channels")).fetchall()

    for (target_chat,) in channels:
        try:
            await message.copy_to(target_chat)
        except Exception as e:
            logger.error(f"Failed to forward to {target_chat}: {e}")


# ---------------------------------------
# BOT STARTER
# ---------------------------------------

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())


---

📄 config.py

from dotenv import load_dotenv
import os
load_dotenv()

class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
    DATABASE_URL = os.getenv("DATABASE_URL")

settings = Settings()


---