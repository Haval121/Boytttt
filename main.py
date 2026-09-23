import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import Message

# زانیاریە ڕاستەقینەکانی بۆتەکەت
API_ID = 36234377
API_HASH = "5e199e2ae89cc1c42a6a4853951ff98f"
BOT_TOKEN = "8725595567:AAGvrUoWr4HU801sH20JjCPdDa_naCTTNo0"

# ئەو IDـیەی کە شتەکانی بۆ فۆروارد دەکرێت
TARGET_CHAT_ID = 8734106005

app = Client("telegram_mod_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ڕێزمانی (Regex) دۆزینەوەی لینک و یوزەرنەیم
LINK_REGEX = r"https?://\S+|t\.me/\S+|www\.\S+|@\w+"

def has_link(text):
    if not text:
        return False
    return bool(re.search(LINK_REGEX, text))

@app.on_message(filters.group & (filters.text | filters.caption))
async def handle_text_messages(client: Client, message: Message):
    # تەنها بۆ پەیامی نوسینی بێ میدیا
    if message.text:
        text = message.text
        if has_link(text):
            try:
                await message.delete()
            except Exception as e:
                print(f"ناتوانێت پەیامی نوسین بسڕێتەوە: {e}")

@app.on_message(filters.group & (filters.video | filters.photo))
async def handle_media_messages(client: Client, message: Message):
    try:
        caption = message.caption or ""
        
        # ئەگەر نوسینی سەر وێنە یان ڤیدیۆکە لێنکی تێدابوو، یەکسەر دەسڕێتەوە و هیچی تر ناکات
        if has_link(caption):
            await message.delete()
            return

        # 1. فۆرواردکردنی وێنە یان ڤیدیۆ بۆ ئەو IDـیەی دیاری کراوە
        await message.forward(chat_id=TARGET_CHAT_ID)
        
        # 2. چاوەڕوانکردنی 3 خولەک (180 چرکە) بۆ هەردووکیان
        await asyncio.sleep(180)
        
        # 3. سڕینەوەی ڤیدیۆ یان وێنەکە لە گرووپ دوای ٣ خولەک
        try:
            await message.delete()
        except Exception as e:
            print(f"هەڵە لە سڕینەوەی پەیام: {e}")
            
        # 4. ئەگەر ڤیدیۆ بوو، دووبارە دەنێردرێتەوە بۆ هەمان ID (وێنە دوبارە لانێردرێتەوە)
        if message.video:
            await client.send_video(
                chat_id=TARGET_CHAT_ID,
                video=message.video.file_id,
                caption=caption
            )

    except Exception as e:
        print(f"هەڵە لە پرۆسێسکردنی میدیا: {e}")

# دەستپێکردنی بۆت
print("بۆتەکە کار دەکات...")
app.run()
