import logging
import os
import subprocess
import tempfile
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "8197236990:AAEZYdLrnnattTanBeUUTtqz9f_4tm0sB4s"

logging.basicConfig(level=logging.INFO)

waiting_users = []
pairs = {}
videos = {}
approved = {}
preview_dirs = {}


def trim_video(input_path: str, output_path: str, duration: int = 2):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-c", "copy",
        output_path
    ], check=True, capture_output=True)


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    msg = update.message

    if not msg.video:
        return

    videos[user] = msg.video.file_id

    if user not in waiting_users:
        waiting_users.append(user)

    await context.bot.send_message(user, "⏳ چاوەڕوانی بەکارهێنەرێکی دیکە بکە...")

    if len(waiting_users) >= 2:
        u1 = waiting_users.pop(0)
        u2 = waiting_users.pop(0)

        pairs[u1] = u2
        pairs[u2] = u1
        approved[u1] = False
        approved[u2] = False

        tmpdir = tempfile.mkdtemp()
        preview_dirs[u1] = tmpdir
        preview_dirs[u2] = tmpdir

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
            InlineKeyboardButton("✅", callback_data="yes"),
            InlineKeyboardButton("❌", callback_data="no")
        ]])

        with open(trim2, "rb") as v:
            await context.bot.send_video(
                u1,
                v,
                caption="2 چرکە preview\n✅ یان ❌",
                reply_markup=keyboard
            )

        with open(trim1, "rb") as v:
            await context.bot.send_video(
                u2,
                v,
                caption="2 چرکە preview\n✅ یان ❌",
                reply_markup=keyboard
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
            await context.bot.send_message(user, "✅ هەردووکتان قبووڵتان کرد!")
            await context.bot.send_message(partner, "✅ هەردووکتان قبووڵتان کرد!")
        else:
            await context.bot.send_message(user, "✅ تۆ قبووڵت کرد، چاوەڕوانی بەکارهێنەرەکەی دیکە بکە...")

    else:
        await context.bot.send_message(user, "❌ ڕەتکرایەوە")
        if partner:
            await context.bot.send_message(partner, "❌ ڕەتکرایەوە")

        approved[user] = False
        if partner:
            approved[partner] = False


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()


if __name__ == "__main__":
    main()
