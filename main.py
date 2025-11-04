import os, re
from datetime import datetime, timedelta
from telegram import ChatInviteLink, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]
FLOW_CHAT_ID = int(os.environ.get("FLOW_CHAT_ID", "0"))  # e.g., -1001234567890
HANDLE_RE = re.compile(r"^@([A-Za-z0-9_]{2,15})$")

WELCOME = ("Hey! 👋 Drop your *X handle* (e.g., @yourhandle).\n"
           "By applying, you agree to follow the Flow rules.")
APPROVED = ("✅ Approved, {name}!\n"
            "Here is your *one-time invite* (expires in 24h).")
REJECTED = ("❌ That doesn't look like a valid handle.\n"
            "Use the format @yourhandle (2–15 chars, letters/numbers/_).")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, parse_mode="Markdown")

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Yap Hub Flow – Rules:\n"
        "1) Campaign posts only (no chat)\n"
        "2) Apply per-campaign form\n"
        "3) Share proofs in assigned thread\n"
        "4) Respect deadlines\n"
        "5) Breaking rules = removal"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    m = HANDLE_RE.match(text)
    if not m:
        await update.message.reply_text(REJECTED)
        return

    if FLOW_CHAT_ID == 0:
        await update.message.reply_text("Admin hasn’t configured FLOW_CHAT_ID yet. Try later.")
        return

    # Create single-use invite link (24h expiry)
    expire_at = datetime.utcnow() + timedelta(hours=24)
    link: ChatInviteLink = await context.bot.create_chat_invite_link(
        chat_id=FLOW_CHAT_ID,
        expire_date=expire_at,
        member_limit=1,
        creates_join_request=False
    )

    name = update.effective_user.first_name or "there"
    await update.message.reply_text(APPROVED.format(name=name), parse_mode="Markdown")
    await update.message.reply_text(link.invite_link)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
