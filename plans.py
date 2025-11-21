# plans.py
from telegram import Update
from telegram.ext import ContextTypes
from db import execute, fetchall, fetchone
from utils import now_iso

ADMIN_ONLY = True

async def cmd_list_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = fetchall("SELECT * FROM plans")
    msg = "Plans:\n"
    for r in rows:
        msg += f"{r['plan_id']}: {r['name']} - {r['price']} {r['currency']} / {r['duration_days']}d - active={r['active']}\nFeatures: {r['features']}\n\n"
    await update.message.reply_text(msg)

async def cmd_create_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /create_plan <name> <price> <currency> <duration_days> <features>
    if len(context.args) < 5:
        await update.message.reply_text("Usage: /create_plan <name> <price> <currency> <duration_days> <features (no spaces? use quotes)>")
        return
    name = context.args[0]
    price = float(context.args[1])
    currency = context.args[2]
    duration = int(context.args[3])
    features = " ".join(context.args[4:])
    execute("INSERT INTO plans (name,price,currency,duration_days,features,active) VALUES (?,?,?,?,?,1)", (name,price,currency,duration,features))
    await update.message.reply_text(f"Created plan {name}")

async def cmd_set_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /set_price <plan_id> <new_price>
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /set_price <plan_id> <new_price>")
        return
    plan_id = int(context.args[0]); price = float(context.args[1])
    execute("UPDATE plans SET price=? WHERE plan_id=?", (price, plan_id))
    await update.message.reply_text(f"Updated plan {plan_id} price to {price}")

async def cmd_disable_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /disable_plan <plan_id>")
        return
    pid = int(context.args[0])
    execute("UPDATE plans SET active=0 WHERE plan_id=?", (pid,))
    await update.message.reply_text(f"Disabled plan {pid}")