# ui.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import config
from db import fetchall

async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("View Plans", callback_data="view_plans")],
        [InlineKeyboardButton("Buy Plan", callback_data="buy_plan")],
        [InlineKeyboardButton("My Mappings", callback_data="my_mappings")]
    ]
    await update.message.reply_text("Choose:", reply_markup=InlineKeyboardMarkup(kb))

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data == "view_plans":
        msg = "Available plans:\n"
        for key, p in config.PLANS.items():
            msg += f"{key}: {p['name']} - {p['price']} {p['currency']} / {p['duration_days']}d\nFeatures: {p['features']}\n\n"
        await q.edit_message_text(msg)
    elif data == "buy_plan":
        await q.edit_message_text("Use /buy <plan_key> to purchase in private chat.")
    elif data == "my_mappings":
        await q.edit_message_text("Use /list_mappings to see your mappings.")