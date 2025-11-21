
# forwarder.py
import logging
from telegram import Update
from telegram.ext import ContextTypes
from db import fetchall, execute
from subscriptions import is_user_allowed
from utils import now_iso, ensure_logs_folder
import config
import os

logger = logging.getLogger(__name__)

def write_forward_log_line(mapping_id, user_id, message_id, source, target, status, error_text=""):
    ensure_logs_folder()
    line = f"{now_iso()} | mapping:{mapping_id} | user:{user_id} | msg:{message_id} | src:{source} | tgt:{target} | status:{status} | error:{error_text}\n"
    try:
        with open(config.FORWARD_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        logger.exception("Failed to write forward log")

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if not msg:
        return
    src_chat = update.effective_chat  # channel
    src = src_chat.username or str(src_chat.id)
    # find mappings for this source
    rows = fetchall("SELECT * FROM mappings WHERE source_channel=? AND active=1", (src,))
    for r in rows:
        uid = r["user_id"]
        mapping_id = r["mapping_id"]
        # check subscription/free
        if not is_user_allowed(uid):
            # skip and optionally write file log
            write_forward_log_line(mapping_id, uid, msg.message_id, src, r["target_channel"], "SKIPPED", "No active subscription")
            continue
        try:
            if msg.text:
                await context.bot.send_message(chat_id=r["target_channel"], text=msg.text)
            elif msg.photo:
                await context.bot.send_photo(chat_id=r["target_channel"], photo=msg.photo[-1].file_id, caption=msg.caption or "")
            elif msg.video:
                await context.bot.send_video(chat_id=r["target_channel"], video=msg.video.file_id, caption=msg.caption or "")
            elif msg.document:
                await context.bot.send_document(chat_id=r["target_channel"], document=msg.document.file_id, caption=msg.caption or "")
            elif msg.audio:
                await context.bot.send_audio(chat_id=r["target_channel"], audio=msg.audio.file_id, caption=msg.caption or "")
            elif msg.voice:
                await context.bot.send_voice(chat_id=r["target_channel"], voice=msg.voice.file_id, caption=msg.caption or "")
            elif msg.sticker:
                await context.bot.send_sticker(chat_id=r["target_channel"], sticker=msg.sticker.file_id)
            elif msg.poll:
                # polls cannot be forwarded by file_id; forward_message works
                await context.bot.forward_message(chat_id=r["target_channel"], from_chat_id=src_chat.id, message_id=msg.message_id)
            else:
                # fallback to forward method
                await context.bot.forward_message(chat_id=r["target_channel"], from_chat_id=src_chat.id, message_id=msg.message_id)
            write_forward_log_line(mapping_id, uid, msg.message_id, src, r["target_channel"], "OK", "")
        except Exception as e:
            write_forward_log_line(mapping_id, uid, msg.message_id, src, r["target_channel"], "FAILED", str(e))
            logger.exception("Forward failed")

async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return
    uid = msg.from_user.id
    rows = fetchall("SELECT * FROM mappings WHERE user_id=? AND active=1", (uid,))
    for r in rows:
        try:
            if msg.text:
                await context.bot.send_message(chat_id=r["target_channel"], text=msg.text)
            elif msg.photo:
                await context.bot.send_photo(chat_id=r["target_channel"], photo=msg.photo[-1].file_id, caption=msg.caption or "")


            elif msg.video:
                await context.bot.send_video(chat_id=r["target_channel"], video=msg.video.file_id, caption=msg.caption or "")
            elif msg.document:
                await context.bot.send_document(chat_id=r["target_channel"], document=msg.document.file_id, caption=msg.caption or "")
            else:
                await context.bot.forward_message(chat_id=r["target_channel"], from_chat_id=msg.chat.id, message_id=msg.message_id)
            write_forward_log_line(r["mapping_id"], uid, msg.message_id, msg.chat.id, r["target_channel"], "OK", "")
        except Exception as e:
            write_forward_log_line(r["mapping_id"], uid, msg.message_id, msg.chat.id, r["target_channel"], "FAILED", str(e))
            logger.exception("Forward private failed")