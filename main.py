import logging
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


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    msg = update.message

    if not msg.video:
        return

    videos[user] = msg.video.file_id

    if user not in waiting_users:
        waiting_users.append(user)

    if len(waiting_users) >= 2:
        u1 = waiting_users.pop(0)
        u2 = waiting_users.pop(0)

        pairs[u1] = u2
        pairs[u2] = u1

        approved[u1] = False
        approved[u2] = False

        await context.bot.send_video(
            u1,
            videos[u2],
            start_timestamp=0,
            caption="2 چرکە preview\n✅ یان ❌",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅", callback_data="yes"),
                InlineKeyboardButton("❌", callback_data="no")
            ]])
        )

        await context.bot.send_video(
            u2,
            videos[u1],
            start_timestamp=0,
            caption="2 چرکە preview\n✅ یان ❌",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅", callback_data="yes"),
                InlineKeyboardButton("❌", callback_data="no")
            ]])
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

    else:
        await context.bot.send_message(user, "❌ ڕەتکرایەوە")
        await context.bot.send_message(partner, "❌ ڕەتکرایەوە")

        approved[user] = False
        approved[partner] = False


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()


if __name__ == "__main__":
    main()
