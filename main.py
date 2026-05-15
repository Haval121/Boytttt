import os import requests from telegram import Update from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = "PUT_YOUR_TELEGRAM_BOT_TOKEN" API_KEY = "c3421c6a-c1d6-463a-aa9c-d817727e18c3" API_URL = "https://api.example.com/process"  # گۆڕە بۆ API URL ـی ڕاستەقینە

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE): photo = update.message.photo[-1] file = await context.bot.get_file(photo.file_id) image_url = file.file_path

payload = {
    "api_key": API_KEY,
    "image_url": image_url
}

r = requests.post(API_URL, json=payload)

if r.status_code == 200:
    result = r.json().get("result_url")
    await update.message.reply_photo(result)
else:
    await update.message.reply_text("هەڵەیەک ڕوویدا")

def main(): app = Application.builder().token(BOT_TOKEN).build() app.add_handler(MessageHandler(filters.PHOTO, handle_photo)) app.run_polling()

if name == "main": main()
