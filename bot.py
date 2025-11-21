
# bot.py
import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    PreCheckoutQueryHandler,
)

import config
import db
import ui
import mappings
import forwarder
import admin_cmds
import subscriptions

from payments_telegram import (
    cmd_buy,
    payment_callback_handler,
    precheckout_handler,
    successful_payment_handler,
    handle_payment_proof,
)

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user or user.id != config.ADMIN_ID:
            if update.message:
                await update.message.reply_text("Admin only.")
            return
        return await func(update, context)
    return wrapper


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /menu to view options.")


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ui.cmd_menu(update, context)


async def list_plans_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Available Plans:\n"
    for key, p in config.PLANS.items():
        msg += f"{key}: {p['name']} — {p['price']} {p['currency']} / {p['duration_days']} days\n"
    await update.message.reply_text(msg)


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if subscriptions.is_user_allowed(uid):
        sub = subscriptions.get_user_active_subscription(uid)
        if sub:
            await update.message.reply_text(f"Active Plan: {sub['plan_key']} — expires {sub['expiry_ts']}")
        else:
            await update.message.reply_text("You have free access.")
    else:
        await update.message.reply_text("No active subscription. Use /buy.")


def main():
    db.init_db()

    app = Application.builder().token(config.BOT_TOKEN).build()

    # User Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("list_plans", list_plans_cmd))
    app.add_handler(CommandHandler("status", status_cmd))

    # Payments
    app.add_handler(CommandHandler("buy", cmd_buy))
    app.add_handler(CallbackQueryHandler(payment_callback_handler))
    app.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))
    app.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, handle_payment_proof))

    # Mappings
    app.add_handler(CommandHandler("add_mapping", mappings.cmd_add_mapping))
    app.add_handler(CommandHandler("list_mappings", mappings.cmd_list_mappings))
    app.add_handler(CommandHandler("remove_mapping", mappings.cmd_remove_mapping))

    # Forwarding
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL & (~filters.COMMAND), forwarder.handle_channel_post))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & (~filters.COMMAND), forwarder.handle_private_message))

    # Admin commands
    app.add_handler(CommandHandler("grant_free", admin_only(admin_cmds.cmd_grant_free)))
    app.add_handler(CommandHandler("revoke_free", admin_only(admin_cmds.cmd_revoke_free)))
    app.add_handler(CommandHandler("manual_activate", admin_only(admin_cmds.cmd_manual_activate)))
    app.add_handler(CommandHandler("list_subscribers", admin_only(admin_cmds.cmd_list_subscribers)))
    app.add_handler(CommandHandler("list_users", admin_only(admin_cmds.cmd_list_users)))
    app.add_handler(CommandHandler("export_payments", admin_only(admin_cmds.cmd_export_payments)))
    app.add_handler(CommandHandler("broadcast", admin_only(admin_cmds.cmd_broadcast)))

    # UI callback
    app.add_handler(CallbackQueryHandler(ui.admin_callback_handler))


    # Set Bot Commands (synchronous)
    commands = [
        BotCommand("start", "Start bot"),
        BotCommand("menu", "Open menu"),
        BotCommand("buy", "Buy a plan"),
        BotCommand("list_plans", "List plans"),
        BotCommand("add_mapping", "Add mapping"),
        BotCommand("list_mappings", "List mappings"),
        BotCommand("remove_mapping", "Remove mapping"),
    ]
    try:
        # synchronous method
        app.bot.set_my_commands(commands)
    except Exception:
        logger.exception("Failed to set bot commands")

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()