import os
import uuid
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from moviepy.editor import VideoFileClip

TOKEN = "8197236990:AAGPM5Wxb-a6DjMOwLh5HqlMvsVKvGPiBFs"

rooms = {}

def make_preview(video_path, out):
    clip = VideoFileClip(video_path).subclip(0, 2)
    clip.write_videofile(out, codec="libx264", audio_codec="aac")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ڤیدیۆ بنێرە")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    video = update.message.video

    file = await context.bot.get_file(video.file_id)
    path = f"{user}.mp4"
    await file.download_to_drive(path)

    if "join" in context.args:
        room_id = context.args[0]
        if room_id in rooms:
            rooms[room_id]["user2"] = user
            rooms[room_id]["video2"] = path
            await process(room_id, context)
    else:
        room_id = str(uuid.uuid4())[:8]
        rooms[room_id] = {
            "user1": user,
            "video1": path,
            "approved1": False,
            "approved2": False
        }
        link = f"https://t.me/YOUR_BOT?start=join_{room_id}"
        await update.message.reply_text(f"ئەم لینکە بنێرە بۆ کەسی دووەم:\n{link}")

async def process(room_id, context):
    room = rooms[room_id]

    p1 = f"{room_id}_1.mp4"
    p2 = f"{room_id}_2.mp4"

    make_preview(room["video1"], p1)
    make_preview(room["video2"], p2)

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ڕازیم", callback_data=f"yes_{room_id}"),
            InlineKeyboardButton("❌ نەخێر", callback_data=f"no_{room_id}")
        ]
    ])

    await context.bot.send_video(room["user1"], open(p2,"rb"), caption="60 چرکە بڕیار بدە", reply_markup=kb)
    await context.bot.send_video(room["user2"], open(p1,"rb"), caption="60 چرکە بڕیار بدە", reply_markup=kb)

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    action, room_id = q.data.split("_")
    room = rooms[room_id]
    user = q.from_user.id

    if action == "no":
        await q.edit_message_text("مامەڵە هەڵوەشایەوە")
        del rooms[room_id]
        return

    if user == room["user1"]:
        room["approved1"] = True
    elif user == room["user2"]:
        room["approved2"] = True

    if room["approved1"] and room["approved2"]:
        await context.bot.send_video(room["user1"], open(room["video2"],"rb"))
        await context.bot.send_video(room["user2"], open(room["video1"],"rb"))
        del rooms[room_id]

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(CallbackQueryHandler(approve))

    app.run_polling()

if __name__ == "__main__":
    main()
