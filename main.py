import os import uuid import asyncio import subprocess from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv"8197236990:AAGPM5Wxb-a6DjMOwLh5HqlMvsVKvGPiBFs" BOT_NAME = "pamay_c_bot" rooms = {}

def make_preview(video_path, out): subprocess.run([ "ffmpeg", "-i", video_path, "-t", "2", "-c:v", "libx264", "-c:a", "aac", "-y", out ], check=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): args = context.args if args and args[0].startswith("join_"): context.user_data["join"] = args[0].split("_")[1] await update.message.reply_text("ڤیدیۆکەت بنێرە") else: await update.message.reply_text("ڤیدیۆکەت بنێرە")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.message.from_user.id video = update.message.video file = await context.bot.get_file(video.file_id) path = f"{user}.mp4" await file.download_to_drive(path)

room_id = context.user_data.get("join")

if room_id and room_id in rooms:
    rooms[room_id]["user2"] = user
    rooms[room_id]["video2"] = path
    await process(room_id, context)
else:
    room_id = str(uuid.uuid4())[:8]
    rooms[room_id] = {"user1": user, "video1": path, "approved1": False, "approved2": False}
    link = f"https://t.me/{BOT_NAME}?start=join_{room_id}"
    await update.message.reply_text(link)

async def process(room_id, context): room = rooms[room_id] p1, p2 = f"{room_id}_1.mp4", f"{room_id}_2.mp4" make_preview(room["video1"], p1) make_preview(room["video2"], p2)

kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅", callback_data=f"yes_{room_id}"), InlineKeyboardButton("❌", callback_data=f"no_{room_id}")]])

await context.bot.send_video(room["user1"], open(p2, "rb"), reply_markup=kb)
await context.bot.send_video(room["user2"], open(p1, "rb"), reply_markup=kb)

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE): q = update.callback_query await q.answer() action, room_id = q.data.split("_") room = rooms[room_id] user = q.from_user.id

if action == "no":
    del rooms[room_id]
    await q.edit_message_text("هەڵوەشایەوە")
    return

if user == room["user1"]:
    room["approved1"] = True
else:
    room["approved2"] = True

if room["approved1"] and room["approved2"]:
    await context.bot.send_video(room["user1"], open(room["video2"], "rb"))
    await context.bot.send_video(room["user2"], open(room["video1"], "rb"))
    del rooms[room_id]

app = ApplicationBuilder().token(TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(MessageHandler(filters.VIDEO, handle_video)) app.add_handler(CallbackQueryHandler(approve)) app.run_polling()
