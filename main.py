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
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-vcodec", "libx264",
        "-acodec", "aac",
        "-strict", "experimental",
        output_path
    ], capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {result.stderr.decode()}")


async def send_previews(context, u1, u2):
    tmpdir = tempfile.mkdtemp()

    try:
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

    except Exception as e:
        logging.error(f"send_previews error: {e}")
        await context.bot.send_message(u1, "❌ هەڵەیەک ڕوویدا لە کاتی نێردنی پریڤیوو. دووبارە ویدیۆت بنێرە.")
        await context.bot.send_message(u2, "❌ هەڵەیەک ڕوویدا لە کاتی نێردنی پریڤیوو. دووبارە ویدیۆت بنێرە.")


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
                "ئێستا ویدیۆی خۆت بنێرە تا ئاڵۆگۆری ویدیۆ بکەین."
            )
        else:
            await update.message.reply_text("❌ ئەم لینکە کار نادات یان بەسەرچووە.")
    else:
        await update.message.reply_text(
            "سڵاو! 👋\n\n"
            "ویدیۆی خۆت بنێرە، لینکێک وەردەگریت.\n"
            "ئەو لینکە بنێرە بۆ ئە
