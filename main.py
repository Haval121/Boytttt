import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json, os

TOKEN = "8197236990:AAGPM5Wxb-a6DjMOwLh5HqlMvsVKvGPiBFs"
ADMIN_ID = 5313754716
CHANNEL = "@pamay_cts"

bot = telebot.TeleBot(TOKEN)

buttons = ["کورد","مناڵ","کامێرای چاودێری","مەلف","بیانی"]

if not os.path.exists("videos.json"):
    with open("videos.json","w") as f:
        json.dump({x:[] for x in buttons},f)

with open("videos.json","r") as f:
    videos=json.load(f)

def save():
    with open("videos.json","w") as f:
        json.dump(videos,f)

def joined(user):
    try:
        s=bot.get_chat_member(CHANNEL,user).status
        return s in ["member","administrator","creator"]
    except:
        return False

def join_menu():
    kb=InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("چوونە ناو چەناڵ",url="https://t.me/pamay_cts"))
    kb.add(InlineKeyboardButton("جۆینم کرد",callback_data="check"))
    return kb

def main_menu():
    kb=InlineKeyboardMarkup()
    for b in buttons:
        kb.add(InlineKeyboardButton(b,callback_data=b))
    return kb

@bot.message_handler(commands=['start'])
def start(m):
    if not joined(m.from_user.id):
        bot.send_message(m.chat.id,"تکایە سەرەتا جۆینی چەناڵ بکە",reply_markup=join_menu())
    else:
        bot.send_message(m.chat.id,
"""╭━━━━━━━━━━━━━━━━━━━

ئەزیزم بەخێر بیت بەشێک هەڵبژێرە 😘

╰━━━━━━━━━━━━━━━━

بۆ بینی ڤیدۆ بەشک هەڵبژێرە👇""",reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c:True)
def call(c):
    if c.data=="check":
        if joined(c.from_user.id):
            bot.send_message(c.message.chat.id,"جۆین کرا ✅",reply_markup=main_menu())
        else:
            bot.answer_callback_query(c.id,"هێشتا جۆینت نەکردووە")
    elif c.data in videos:
        for v in videos[c.data]:
            bot.send_video(c.message.chat.id,v)

@bot.message_handler(commands=['add'])
def add(m):
    if m.from_user.id==ADMIN_ID:
        msg=bot.reply_to(m,"ناوی بەش بنێرە")
        bot.register_next_step_handler(msg,getcat)

def getcat(m):
    cat=m.text
    if cat in buttons:
        msg=bot.reply_to(m,"ڤیدیۆ بنێرە")
        bot.register_next_step_handler(msg,savevideo,cat)

def savevideo(m,cat):
    if m.video:
        videos[cat].append(m.video.file_id)
        save()
        bot.reply_to(m,"زیادکرا ✅")

@bot.message_handler(commands=['del'])
def delete(m):
    if m.from_user.id==ADMIN_ID:
        x=m.text.replace("/del ","")
        if x in videos and videos[x]:
            videos[x].pop()
            save()
            bot.reply_to(m,"سڕایەوە ✅")

print("started")
bot.infinity_polling()
