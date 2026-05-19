import logging
import os
import subprocess
import tempfile
import uuid
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "8197236990:AAEZYdLrnnattTanBeUUTtqz9f_4tm0sB4s"
BOT_USERNAME = "pamay_c_bot"

logging.basicConfig(level=logging.INFO)

pending_invites = {}
videos = {}
pairs = {}
approved = {}
waiting_for_partner = {}


def trim_video(input_path: str, output_path: str, duration: int = 2):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-c", "copy",
        output_path
    ], check=True, capture_output=True)


async def send_previews(context, u1, u2):
    tmpdir = tempfile.mkdtemp()

    file2 = await context.bot.get_file(videos[u2])
    path2 = os.path.join(tmpdir, "u2_orig.mp4")
    trim2 = os.path.join(tmpdir, "u2_trim.mp4")
    await file2.download_to_drive(path2)
    trim_video(path2, trim2)

    file1 = await context.bot.get_file(videos[u1])
    path1 = os.path.join(tmpdir, "u1_orig.mp4")
    trim1 = os.path.join(tmpdir, "u1_trim.mp4")
    await file1.download_to_drive(path1)
    trim_video(path1, trim1)

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ قبووڵ", callback_data="yes"),
        InlineKeyboardButton("❌ ڕەت", callback_data="no")
    ]])

    with open(trim2, "rb") as v:
        await context.bot.send_video(
            u1,
            v,
            caption="2 چرکە پریڤیوو — قبووڵ دەکەیت؟",
            reply_markup=keyboard
        )

    with open(trim1, "rb") as v:
        await context.bot.send_video(
            u2,
            v,
            caption="2 چرکە پریڤیوو — قبووڵ دەکەیت؟",
            reply_markup=keyboard
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    args = context.args

    if args:
        token = args[0]
        if token in pending_invites:
            inviter = pending_invites[token]
            if inviter == user:
                await update.message.reply_text("❌ ناتوانیت لینکی خۆت بکەیتەوە.")
                return

            waiting_for_partner[user] = token
            await update.message.reply_text(
                "✅ لینکەکە کارا بوو!\n\n"
                "ئێستا ڤیدیۆی خۆت بنێرە تا ئاڵۆگۆری ڤیدیۆ بکەین."
            )
        else:
            await update.message.reply_text("❌ ئەم لینکە کار نادات یان بەسەرچووە.")
    else:
        await update.message.reply_text(
            "سڵاو! 👋\n\n"
            "ڤیدیۆی خۆت بنێرە، لینکێک وەردەگریت.\n"
            "ئەو لینکە بنێرە بۆ ئەو کەسەی دەتەوێت ڤیدیۆی لەگەڵدا ئاڵوگۆڕبکەیت."
        )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    msg = update.message

    if not msg.video:
        return

    videos[user] = msg.video.file_id

    if user in waiting_for_partner:
        token = waiting_for_partner.pop(user)
        if token in pending_invites:
            inviter = pending_invites.pop(token)

            if inviter not in videos:
                await update.message.reply_text("❌ ئەو کەسەی لینکەکەی نێردووە هێشتا ویدیۆی نێردوونی.")
                return

            pairs[user] = inviter
            pairs[inviter] = user
            approved[user] = False
            approved[inviter] = False

            await update.message.reply_text("✅ ویدیۆت وەرگیرا! پریڤیووی یەکتری دەنێرین...")
            await context.bot.send_message(inviter, "✅ ئەو کەسەی لینکەکەت نێردووە ویدیۆی نێرد! پریڤیووی یەکتری دەنێرین...")

            await send_previews(context, inviter, user)
        return

    token = str(uuid.uuid4())[:8]
    pending_invites[token] = user

    link = f"https://t.me/{BOT_USERNAME}?start={token}"

    await update.message.reply_text(
        f"✅ ویدیۆت وەرگیرا!\n\n"
        f"ئەم لینکەی خوارەوە بنێرە بۆ ئەو کەسەی دەتەوێت ویدیۆی لەگەڵدا گۆڕبکەیت:\n\n"
        f"`{link}`",
        parse_mode="Markdown"
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user.id
    partner = pairs.get(user)

    await query.answer()

    if query.data == "yes":
        approved[user] = True

        if approved.get(partner):
            await context.bot.send_video(user, videos[partner])
            await context.bot.send_video(partner, videos[user])
            await context.bot.send_message(user, "✅ هەردووکتان قبووڵتان کرد! ویدیۆی تەواو بینە.")
            await context.bot.send_message(partner, "✅ هەردووکتان قبووڵتان کرد! ویدیۆی تەواو بینە.")
        else:
            await context.bot.send_message(user, "✅ تۆ قبووڵت کرد، چاوەڕوانی بەکارهێنەرەکەی دیکەی بکە...")

    else:
        await context.bot.send_message(user, "❌ ڕەتت کردەوە.")
        if partner:
            await context.bot.send_message(partner, "❌ بەکارهێنەرەکەی دیکە ڕەتی کردەوە.")

        approved[user] = False
        if partner:
            approved[partner] = False


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()


if __name__ == "__main__":
    main()
