
# payments_telegram.py
import logging
import traceback
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    InputFile
)
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

import config
import db
import subscriptions
from utils import now_iso
from upi_qr import generate_upi_qr

logger = logging.getLogger(__name__)


async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /buy <plan_key>  - must be used in private chat
    """
    try:
        if update.message.chat.type != "private":
            await update.message.reply_text("Use /buy in private chat.")
            return

        if len(context.args) != 1:
            await update.message.reply_text("Usage: /buy <plan_key>")
            return

        plan_key = context.args[0].strip()
        plan = config.PLANS.get(plan_key)
        if not plan:
            await update.message.reply_text("Invalid plan key. Use /list_plans.")
            return

        kb = [
            [InlineKeyboardButton("💠 Pay by UPI (locked amount)", callback_data=f"upi_{plan_key}")],
            [InlineKeyboardButton("💳 Telegram Payment", callback_data=f"tgpay_{plan_key}")],
            [InlineKeyboardButton("🅿️ PayPal (USD)", callback_data=f"paypal_{plan_key}")],
            [InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{config.ADMIN_USERNAME}")]
        ]

        msg = f"Choose a payment option for *{plan['name']}*\nPrice: {plan['price']} {plan['currency']}"
        await update.message.reply_text(escape_markdown(msg, version=2), reply_markup=InlineKeyboardMarkup(kb), parse_mode="MarkdownV2")
    except Exception:
        logger.error("cmd_buy error:\n%s", traceback.format_exc())
        await update.message.reply_text("Internal error preparing payment options. Contact admin.")


async def payment_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles inline button clicks for upi_, tgpay_, paypal_ prefixes.
    """
    q = update.callback_query
    await q.answer()
    try:
        data = (q.data or "").strip()
        if not data:
            await q.edit_message_text("Invalid action.")
            return

        # UPI flow: generate locked-amount QR and send to user (private)
        if data.startswith("upi_"):
            plan_key = data.replace("upi_", "", 1)
            plan = config.PLANS.get(plan_key)
            if not plan:
                await q.edit_message_text("Plan not found.")
                return

            if not getattr(config, "UPI_ID", None):
                txt = f"UPI not configured. Contact @{config.ADMIN_USERNAME}"
                await q.edit_message_text(escape_markdown(txt, version=2), parse_mode="MarkdownV2")
                return

            amount = float(plan["price"])

            # generate qr
            try:
                qr_bio = generate_upi_qr(upi_id=config.UPI_ID, name=config.UPI_NAME or config.ADMIN_USERNAME, amount=amount)
            except Exception:
                logger.exception("Failed to generate UPI QR")
                await q.edit_message_text(escape_markdown("Failed to generate UPI QR. Contact admin.", version=2), parse_mode="MarkdownV2")
                return

            # Inform user, then send photo privately
            await q.edit_message_text(escape_markdown("UPI QR generated — sending in private chat.", version=2), parse_mode="MarkdownV2")
            caption = (
                f"🟦 *UPI Payment — {plan['name']}*\n"
                f"💰 Amount: ₹{amount}\n"
                f"📍 UPI ID: {config.UPI_ID}\n\n"
                "Scan the QR or use the UPI ID (amount is locked).\n\n"
                "After payment, upload screenshot here with caption:\n"
                f"proof {plan_key}\n\n"
                f"Or send screenshot to @{config.ADMIN_USERNAME}"
            )
            try:
                await context.bot.send_photo(chat_id=q.from_user.id, photo=InputFile(qr_bio), caption=escape_markdown(caption, version=2), parse_mode="MarkdownV2")
            except Exception:
                # fallback: send QR inline if private chat blocked
                logger.exception("Failed to send QR in private chat")
                await q.edit_message_text(escape_markdown("Couldn't send private message with QR. Please open a private chat with the bot and try again.", version=2), parse_mode="MarkdownV2")
            return

        # Telegram Pay (native invoice)
        if data.startswith("tgpay_"):
            plan_key = data.replace("tgpay_", "", 1)
            plan = config.PLANS.get(plan_key)
            if not plan:
                await q.edit_message_text("Plan not found.")
                return

            if not getattr(config, "TELEGRAM_PROVIDER_TOKEN", None):
                txt = f"Telegram Payments not configured. Use UPI/PayPal or contact @{config.ADMIN_USERNAME}"
                await q.edit_message_text(escape_markdown(txt, version=2), parse_mode="MarkdownV2")
                return

            try:
                # price in smallest unit (paise/cents)
                amount = float(plan["price"])
                smallest = int(round(amount * 100))
                prices = [LabeledPrice(label=plan["name"], amount=smallest)]
                payload = f"buy_{plan_key}_{q.from_user.id}"
                await context.bot.send_invoice(
                    chat_id=q.from_user.id,
                    title=f"{plan['name']} Subscription",
                    description=plan.get("features", ""),
                    payload=payload,
                    provider_token=config.TELEGRAM_PROVIDER_TOKEN,
                    currency=plan.get("currency", config.DEFAULT_CURRENCY),
                    prices=prices,
                )
                await q.edit_message_text(escape_markdown("Invoice sent — check your private chat.", version=2), parse_mode="MarkdownV2")
            except Exception:
                logger.exception("Failed to send invoice")
                await q.edit_message_text(escape_markdown("Failed to create invoice. Contact admin.", version=2), parse_mode="MarkdownV2")
            return

        # PayPal flow (manual USD price from config)
        if data.startswith("paypal_"):
            plan_key = data.replace("paypal_", "", 1)
            plan = config.PLANS.get(plan_key)
            if not plan:
                await q.edit_message_text("Plan not found.")
                return

            usd_price = plan.get("paypal_price_usd")
            if usd_price is None:
                await q.edit_message_text(escape_markdown("PayPal price not set for this plan. Contact admin.", version=2), parse_mode="MarkdownV2")
                return

            paypal_base = getattr(config, "PAYPAL_LINK", "") or ""
            if paypal_base:
                # If admin provided a base PayPal link, attach amount param if not present
                if "?" in paypal_base:
                    link = f"{paypal_base}&amount={usd_price}"
                else:
                    link = f"{paypal_base}?amount={usd_price}"
            else:
                link = "Not configured"

            msg = (
                f"🅿️ *PayPal Payment — {plan['name']}*\n"
                f"Amount: ${usd_price}\n"
                f"PayPal Link: {link}\n\n"
                "After payment, upload screenshot with caption:\n"
                f"proof {plan_key}\n\n"
                f"Or send screenshot to @{config.ADMIN_USERNAME}"
            )
            await q.edit_message_text(escape_markdown(msg, version=2), parse_mode="MarkdownV2")
            return

        await q.edit_message_text("Unknown payment action.")
    except Exception:
        logger.error("payment_callback_handler error:\n%s", traceback.format_exc())
        try:
            await q.edit_message_text(escape_markdown("An internal error occurred. Contact admin.", version=2), parse_mode="MarkdownV2")
        except:
            pass


async def precheckout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.pre_checkout_query.answer(ok=True)
    except Exception:
        logger.exception("precheckout_handler error")


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        payment = update.message.successful_payment
        payload = getattr(payment, "invoice_payload", "")
        parts = payload.split("_")
        if len(parts) < 3:
            await update.message.reply_text("Payment received but payload invalid. Contact admin.")
            return

        _, plan_key, uid_str = parts[0], parts[1], parts[2]
        try:
            uid = int(uid_str)
        except:
            uid = update.effective_user.id

        db.execute(
            "INSERT INTO payments (user_id,provider,payload,status,ts) VALUES (?,?,?,?,?)",
            (uid, "telegram", str(payment.to_dict()), "success", now_iso())
        )

        amount = (getattr(payment, "total_amount", 0)) / 100.0
        subscriptions.activate_subscription(uid, plan_key, provider="telegram", provider_payment_id=str(getattr(payment, "provider_payment_charge_id", "") or ""), amount=amount)

        await update.message.reply_text("🎉 Payment successful! Your subscription is now active.")
    except Exception:
        logger.exception("successful_payment_handler error")
        await update.message.reply_text("Payment processed but an internal error occurred; contact admin.")


async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    User uploads screenshot with caption: proof <plan_key>
    """
    try:
        msg = update.message
        if not msg or not msg.photo:
            return
        caption = (msg.caption or "").strip()
        if not caption.lower().startswith("proof "):
            return
        parts = caption.split(" ", 1)
        if len(parts) != 2:
            await msg.reply_text("Use caption: proof <plan_key>")
            return
        plan_key = parts[1].strip()
        plan = config.PLANS.get(plan_key)
        if not plan:
            await msg.reply_text("Plan key not recognized.")
            return

        user = update.effective_user

        admin_text = (
            "📥 *New Payment Proof Received*\n\n"
            f"User: {user.full_name}\n"
            f"Username: @{user.username if user.username else 'N/A'}\n"
            f"User ID: {user.id}\n"
            f"Plan: {plan_key}\n"
            f"Amount: {plan.get('paypal_price_usd') if 'paypal' in caption.lower() else plan.get('price')} {('USD' if 'paypal' in caption.lower() else plan.get('currency'))}\n"
            f"Time: {now_iso()}"
        )
        await context.bot.send_message(chat_id=config.ADMIN_ID, text=escape_markdown(admin_text, version=2), parse_mode="MarkdownV2")
        await context.bot.forward_message(chat_id=config.ADMIN_ID, from_chat_id=msg.chat.id, message_id=msg.message_id)

        # Record pending payment
        db.execute("INSERT INTO payments (user_id,provider,payload,status,ts) VALUES (?,?,?,?,?)",
                   (user.id, "manual_proof", f"plan={plan_key}", "pending", now_iso()))

        await msg.reply_text("Thanks — proof sent to admin. Admin will verify and activate your plan using /manual_activate.")
    except Exception:
        logger.exception("handle_payment_proof error")
        try:
            await update.message.reply_text("Failed to forward proof. Try again or contact admin.")
        except:
            pass