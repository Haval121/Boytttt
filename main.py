import uuid
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "8197236990:AAGPM5Wxb-a6DjMOwLh5HqlMvsVKvGPiBFs"
BOT_NAME = "pamay_c_bot"
rooms = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ڤیدیۆ بنێرە")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    file_id = update.message.video.file_id

    room = str(uuid.uuid4())[:8]
    rooms[room] = {"u1": user, "v1": file_id}

    link = f"https://t.me/{BOT_NAME}?start={room}"
    await update.message.reply_text(link)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VIDEO, video))

app.run_polling()
