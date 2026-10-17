import asyncio
import logging
import re

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

TOKEN = "8725595567:AAGo5csE6V6jFEJI5XLEYPtfcOscaTDZNLc"
ADMIN_ID = 8734106005

DELETE_DELAY = 185
PHOTO_DELETE_DELAY = 600  # 3 hours

URL_REGEX = re.compile(
    r'(https?://\S+|t\.me/\S+|www\.\S+|@\w+)',
    re.IGNORECASE
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# دروستکردنی بۆت و دیسپاچەر بە خێراییەکی بەرز
bot = Bot(token=TOKEN)
dp = Dispatcher()


async def delete_msg(chat_id: int, msg_id: int):
    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=msg_id
        )
    except Exception as e:
        logging.warning(f"Delete error: {e}")


async def delete_photo(chat_id: int, msg_id: int):
    await asyncio.sleep(PHOTO_DELETE_DELAY)
    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=msg_id
        )
    except Exception as e:
        logging.warning(f"Photo delete error: {e}")


async def process_media(
    chat_id: int,
    msg_id: int,
    file_id: str,
    caption: str,
    is_video: bool = True
):
    await asyncio.sleep(DELETE_DELAY)
    await delete_msg(chat_id, msg_id)

    try:
        if is_video:
            await bot.send_video(
                chat_id=ADMIN_ID,
                video=file_id,
                caption=caption
            )
        else:
            await bot.send_animation(
                chat_id=ADMIN_ID,
                animation=file_id,
                caption=caption
            )
    except Exception as e:
        logging.error(f"Media error: {e}")


@dp.message()
async def handle(message: Message):
    try:
        if not message:
            return

        # 👤 Delete join messages
        if message.new_chat_members:
            await delete_msg(
                message.chat.id,
                message.message_id
            )
            return

        # =========================
        # Forward media only
        # =========================
        if not message.text:
            try:
                await message.forward(
                    chat_id=ADMIN_ID
                )
            except Exception as e:
                logging.error(f"Forward error: {e}")

        # =========================
        # Text / Caption
        # =========================
        text = message.text or message.caption or ""

        # 🔗 Block links + usernames
        if URL_REGEX.search(text):
            await delete_msg(
                message.chat.id,
                message.message_id
            )
            return

        # 🤖 Block ONLY bot text messages
        if (
            message.text
            and message.from_user
            and message.from_user.is_bot
        ):
            await delete_msg(
                message.chat.id,
                message.message_id
            )
            return

        # =========================
        # Video
        # =========================
        if message.video:
            asyncio.create_task(
                process_media(
                    message.chat.id,
                    message.message_id,
                    message.video.file_id,
                    message.caption,
                    True
                )
            )

        # =========================
        # GIF / Animation
        # =========================
        elif message.animation:
            asyncio.create_task(
                process_media(
                    message.chat.id,
                    message.message_id,
                    message.animation.file_id,
                    message.caption,
                    False
                )
            )

        # =========================
        # Photo
        # =========================
        elif message.photo:
            asyncio.create_task(
                delete_photo(
                    message.chat.id,
                    message.message_id
                )
            )

    except Exception as e:
        logging.exception(f"Handler error: {e}")


async def main():
    print("Bot is running with aiogram...")
    # لابردنی نامە کۆنەکان لە کاتی داگیرساندندا
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception(f"Bot crashed: {e}")
        
