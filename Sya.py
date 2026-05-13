import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json, os

TOKEN = "8197236990:AAGPM5Wxb-a6DjMOwLh5HqlMvsVKvGPiBFs"
ADMIN_ID = 5313754716

bot = telebot.TeleBot(TOKEN)

if not os.path.exists("videos.json"):
    with open("videos.json","w") as f:
        json.dump({},f)

with open("videos.json","r") as f:
    videos=json.load(f)

def save():
    with open("videos.json","w") as f:
        json.dump(videos,f)

def menu():
    kb=InlineKeyboardMarkup()
    for x in videos:
        kb.add(InlineKeyboardButton(x,callback_data=x))
    return kb

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id,
"""╭━━━━━━━━━━━━━━━━━━━
ئەزیزم جۆینی چەناڵەکەمان بکە 😘

⚡️ t.me/pamay_cts

╰━━━━━━━━━━━━━━━━

بۆ بینی ڤیدۆ بەشک هەڵبژێرە👇""",reply_markup=menu())

@bot.callback_query_handler(func=lambda c:True)
def call(c):
    if c.data in videos:
        bot.send_video(c.message.chat.id,videos[c.data])

@bot.message_handler(commands=['add'])
def add(m):
    if m.from_user.id==ADMIN_ID:
        msg=bot.reply_to(m,"ناوی بەش؟")
        bot.register_next_step_handler(msg,getname)

def getname(m):
    name=m.text
    msg=bot.reply_to(m,"ڤیدیۆ بنێرە")
    bot.register_next_step_handler(msg,savevideo,name)

def savevideo(m,name):
    if m.video:
        videos[name]=m.video.file_id
        save()
        bot.reply_to(m,"زیادکرا ✅")

@bot.message_handler(commands=['del'])
def delete(m):
    if m.from_user.id==ADMIN_ID:
        name=m.text.replace("/del ","")
        if name in videos:
            del videos[name]
            save()
            bot.reply_to(m,"سڕایەوە ✅")

print("started")
bot.infinity_polling()
