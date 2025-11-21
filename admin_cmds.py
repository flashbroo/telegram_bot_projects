# admin_cmds.py

from telegram import Update
from telegram.ext import ContextTypes
import db
import subscriptions
from utils import now_iso

# Grant free access
async def cmd_grant_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        return await update.message.reply_text("Usage: /grant_free <user_id>")

    uid = int(context.args[0])
    db.execute(
        "INSERT OR REPLACE INTO users (user_id, free_access, created_at, updated_at) VALUES (?, 1, ?, ?)",
        (uid, now_iso(), now_iso())
    )
    await update.message.reply_text(f"✅ Free access granted to {uid}")

# Revoke free access
async def cmd_revoke_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        return await update.message.reply_text("Usage: /revoke_free <user_id>")

    uid = int(context.args[0])
    db.execute(
        "UPDATE users SET free_access=0, updated_at=? WHERE user_id=?",
        (now_iso(), uid)
    )
    await update.message.reply_text(f"❌ Free access revoked for {uid}")

# Manual subscription activation
async def cmd_manual_activate(update, context):
    # /manual_activate <user_id> <plan_key> [days]
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /manual_activate <user_id> <plan_key> [days]")
        return

    uid = int(context.args[0])
    plan_key = context.args[1]

    if plan_key not in config.PLANS:
        await update.message.reply_text("❌ Invalid plan key.")
        return

    # custom days (optional)
    custom_days = int(context.args[2]) if len(context.args) == 3 else None

    result = subscriptions.manual_activate(uid, plan_key, custom_days)

    if not result:
        await update.message.reply_text("❌ Activation failed. Check user or plan.")
        return

    # Notify admin
    await update.message.reply_text(
        f"✅ User {uid} manually activated for plan '{plan_key}'."
    )

    # Notify the user
    try:
        await context.bot.send_message(
            chat_id=uid,
            text=(
                f"🎉 *Subscription Activated!*\n\n"
                f"Plan: *{config.PLANS[plan_key]['name']}*\n"
                f"Duration: *{config.PLANS[plan_key]['duration_days']} days*\n"
                f"Thank you for using our service!"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        # If user blocked bot or cannot be messaged
        await update.message.reply_text(f"⚠️ User notification failed: {e}")

# List subscribers
async def cmd_list_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = db.fetchall("SELECT * FROM subscriptions WHERE status='active' ORDER BY expiry_ts DESC")
    if not rows:
        return await update.message.reply_text("No active subscriptions.")

    msg = "Active subscribers:\n\n"
    for r in rows:
        msg += f"User {r['user_id']} → {r['plan_key']} (expires {r['expiry_ts']})\n"

    await update.message.reply_text(msg)

# List all users
async def cmd_list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = db.fetchall("SELECT * FROM users")
    if not rows:
        return await update.message.reply_text("No users found.")

    msg = "Users:\n\n"
    for r in rows:
        msg += f"{r['user_id']} (free_access={r['free_access']})\n"

    await update.message.reply_text(msg)

# Export payments
async def cmd_export_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = db.fetchall("SELECT * FROM payments")
    if not rows:
        return await update.message.reply_text("No payments.")

    from io import BytesIO
    import csv

    buffer = BytesIO()
    writer = csv.writer(buffer)

    writer.writerow(["payment_id","user_id","provider","payload","status","ts"])
    for r in rows:
        writer.writerow([r["payment_id"], r["user_id"], r["provider"], r["payload"], r["status"], r["ts"]])

    buffer.seek(0)
    await update.message.reply_document(buffer, filename="payments.csv")

# Broadcast
async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /broadcast <message>")

    text = " ".join(context.args)
    users = db.fetchall("SELECT user_id FROM users")

    count = 0
    for u in users:
        try:
            await context.bot.send_message(u["user_id"], text)
            count += 1
        except:
            pass

    await update.message.reply_text(f"Broadcast sent to {count} users.")