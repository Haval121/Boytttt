import asyncio
import uuid
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8197236990:AAGPM5Wxb-a6DjMOwLh5HqlMvsVKvGPiBFs"
BOT_NAME = "pamay_c_bot"

rooms = {}
logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if args:
        context.user_data["join"] = args[0]
        await update.message.reply_text("ڤیدیۆکەت بنێرە")
    else:
        await update.message.reply_text("ڤیدیۆی خۆت بنێرە")


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    file_id = update.message.video.file_id
    room = context.user_data.get("join")

    if room and room in rooms:
        rooms[room]["u2"] = user
        rooms[room]["v2"] = file_id
        await preview(context, room)

    else:
        room = str(uuid.uuid4())[:8]
        rooms[room] = {
            "u1": user,
            "v1": file_id,
            "a1": False,
            "a2": False
        }

        link = f"https://t.me/{BOT_NAME}?start={room}"
        await update.message.reply_text(link)


async def preview(context, room):
    r = rooms[room]

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅", callback_data=f"yes:{room}"),
        InlineKeyboardButton("❌", callback_data=f"no:{room}")
    ]])

    await context.bot.send_video(r["u1"], r["v2"], reply_markup=kb)
    await context.bot.send_video(r["u2"], r["v1"], reply_markup=kb)

    await asyncio.sleep(60)

    if room in rooms:
        del rooms[room]


async def click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    action, room = q.data.split(":")
    r = rooms.get(room)

    if not r:
        return

    if action == "no":
        del rooms[room]
        await q.edit_message_text("هەڵوەشایەوە")
        return

    if q.from_user.id == r["u1"]:
        r["a1"] = True
    else:
        r["a2"] = True

    if r["a1"] and r["a2"]:
        await context.bot.send_video(r["u1"], r["v2"])
        await context.bot.send_video(r["u2"], r["v1"])
        del rooms[room]


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(CallbackQueryHandler(click))

    app.run_polling()


if __name__ == "__main__":
    main()
