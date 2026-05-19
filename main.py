import asyncio
import uuid
import logging
import os
import subprocess
import tempfile
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8197236990:AAEZYdLrnnattTanBeUUTtqz9f_4tm0sB4s"
BOT_NAME = "pamay_c_bot"

rooms = {}
logging.basicConfig(level=logging.INFO)


def make_preview(input_path: str, output_path: str):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", "2",
        "-vf", "scale=-2:90",
        "-c:v", "libx264",
        "-preset", "fast",
        "-an",
        output_path
    ], check=True, capture_output=True)


async def download_video(bot, file_id: str, dest_path: str):
    f = await bot.get_file(file_id)
    await f.download_to_drive(dest_path)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if args:
        room_id = args[0]
        if room_id not in rooms:
            await update.message.reply_text("ببورە، ئەم لینکە کاتی تێپەڕیوە یان بەکارهاتووە. داوا بکە لینکێکی نوێ بنێرنت.")
            return
        context.user_data["join"] = room_id
        await update.message.reply_text(
            "🎬 ڤیدیۆکەت بنێرە!

"
            "دوای وەرگرتنی ڤیدیۆکەت، هەر دووتان ٢ چرکەی ڤیدیۆی ئەوی تر دەبینن.
"
            "ئەگەر هەر دووکتان ✅ کردن ← ڤیدیۆی تەواو وەر دەگرن."
        )
    else:
        await update.message.reply_text(
            "بەخێر بیت بۆ بۆتی ئاڵوگۆڕی ڤیدیۆ 🎬

"
            "تکایە ڤیدیۆکەت بنێرە، لینکێک وەر دەگریت 🖇️
"
            "ئەو لینکە بنێرە بۆ ئەو کەسی دەتەوێت لەگەڵی ئاڵوگۆڕی ڤیدیۆ بکەیت.

"
            "هەر یەکێک لە ئێوە ٢ چرکەی ڤیدیۆی ئەوی تر وەر دەگرێت بە کوالێتی 90p.

"
            "ئەگەر هەر دووکتان ✅ رازی بوون ← ڤیدیۆکان وەر دەگرن
"
            "❌ هیچ کامێکتان رازی نەبوو ← ڤیدیۆ وەرناگرن"
        )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    file_id = update.message.video.file_id
    room = context.user_data.get("join")

    if room and room in rooms:
        rooms[room]["u2"] = user
        rooms[room]["v2"] = file_id
        await update.message.reply_text("چاوەڕێ بکە، ڤیدیۆکەت پرۆسێس دەکرێت...")
        asyncio.create_task(preview(context, room))
    else:
        room = str(uuid.uuid4())[:8]
        rooms[room] = {"u1": user, "v1": file_id, "a1": False, "a2": False}
        link = f"https://t.me/{BOT_NAME}?start={room}"
        await update.message.reply_text(link)


async def preview(context, room):
    r = rooms[room]
    bot = context.bot

    with tempfile.TemporaryDirectory() as tmp:
        v1_orig = os.path.join(tmp, "v1_orig.mp4")
        v2_orig = os.path.join(tmp, "v2_orig.mp4")
        v1_prev = os.path.join(tmp, "v1_prev.mp4")
        v2_prev = os.path.join(tmp, "v2_prev.mp4")

        await asyncio.gather(
            download_video(bot, r["v1"], v1_orig),
            download_video(bot, r["v2"], v2_orig),
        )

        await asyncio.gather(
            asyncio.to_thread(make_preview, v1_orig, v1_prev),
            asyncio.to_thread(make_preview, v2_orig, v2_prev),
        )

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅", callback_data=f"yes:{room}"),
            InlineKeyboardButton("❌", callback_data=f"no:{room}")
        ]])

        with open(v2_prev, "rb") as f2, open(v1_prev, "rb") as f1:
            await asyncio.gather(
                bot.send_video(r["u1"], f2, reply_markup=kb, caption="٢ چرکەی پێشبینی — پەسەندت دەکات؟"),
                bot.send_video(r["u2"], f1, reply_markup=kb, caption="٢ چرکەی پێشبینی — پەسەندت دەکات؟"),
            )

    await asyncio.sleep(60)
    if room in rooms:
        del rooms[room]


async def click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    action, room = q.data.split(":")
    r = rooms.get(room)

    if not r:
        await q.edit_message_caption("ماوەکە تەواو بووە یان هەڵوەشاوەتەوە.")
        return

    if action == "no":
        del rooms[room]
        await q.edit_message_caption("هەڵوەشایەوە ❌")
        return

    if q.from_user.id == r["u1"]:
        r["a1"] = True
    elif q.from_user.id == r["u2"]:
        r["a2"] = True

    await q.edit_message_caption("چاوەڕێی ئەوی تر دەکات... ✅")

    if r["a1"] and r["a2"]:
        await asyncio.gather(
            context.bot.send_video(r["u1"], r["v2"], caption="ڤیدیۆی تەواو 🎉"),
            context.bot.send_video(r["u2"], r["v1"], caption="ڤیدیۆی تەواو 🎉"),
        )
        del rooms[room]


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(CallbackQueryHandler(click))
    app.run_polling()


if __name__ == "__main__":
    main()