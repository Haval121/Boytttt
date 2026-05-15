import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN"
API_KEY = "c3421c6a-c1d6-463a-aa9c-d817727e18c3"
API_URL = "https://api.example.com/process"


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]

        file = await context.bot.get_file(photo.file_id)
        image_url = file.file_path

        payload = {
            "api_key": API_KEY,
            "image_url": image_url
        }

        r = requests.post(API_URL, json=payload, timeout=60)

        if r.status_code == 200:
            data = r.json()

            if "result_url" in data:
                await update.message.reply_photo(data["result_url"])
            else:
                await update.message.reply_text("API وەڵامی دروست نەدا")
        else:
            await update.message.reply_text(f"هەڵە: {r.status_code}")

    except Exception as e:
        await update.message.reply_text(f"کراش: {str(e)}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.PHOTO, handle_photo)
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
