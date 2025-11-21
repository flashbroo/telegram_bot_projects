# mappings.py
from telegram import Update
from telegram.ext import ContextTypes
from db import execute, fetchall
from utils import now_iso

async def cmd_add_mapping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /add_mapping <source_channel> <target_channel> [watermark 0/1]
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add_mapping <source_channel> <target_channel> [watermark(0/1)]")
        return
    src = context.args[0]
    tgt = context.args[1]
    watermark = int(context.args[2]) if len(context.args) >= 3 else 0
    uid = update.effective_user.id
    execute("INSERT INTO mappings (user_id,source_channel,target_channel,filters,watermark,active,created_at) VALUES (?,?,?,?,?,?,?)",
            (uid, src, tgt, "", watermark, 1, now_iso()))
    await update.message.reply_text(f"Mapping added: {src} -> {tgt}")

async def cmd_list_mappings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    rows = fetchall("SELECT * FROM mappings WHERE user_id=?", (uid,))
    if not rows:
        await update.message.reply_text("No mappings found.")
        return
    msg = "Your mappings:\n"
    for r in rows:
        msg += f"{r['mapping_id']}: {r['source_channel']} -> {r['target_channel']} active={r['active']} watermark={r['watermark']}\n"
    await update.message.reply_text(msg)

async def cmd_remove_mapping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /remove_mapping <mapping_id>")
        return
    mid = int(context.args[0]); uid = update.effective_user.id
    execute("DELETE FROM mappings WHERE mapping_id=? AND user_id=?", (mid, uid))
    await update.message.reply_text(f"Removed mapping {mid}")