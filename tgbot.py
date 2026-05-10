import asyncio
import os
import re
import yt_dlp

from aiogram import Bot, Dispatcher
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart

TOKEN = os.getenv ("8325957768:AAFRRCd5GyVlZJ84b1jN35jKyzbciul5QXE")

bot = Bot(token=TOKEN)
dp = Dispatcher()


# перевірка чи це посилання
def is_url(text):
    return bool(re.search(r'https?://\S+', text))


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Надішли посилання на відео, і я його скачаю")


@dp.message()
async def download(message: Message):
    text = message.text

    # якщо повідомлення пусте
    if not text:
        return

    # якщо це НЕ посилання → ігноруємо
    if not is_url(text):
        return

    # якщо в групі → працюємо тільки з посиланнями
    if message.chat.type != "private" and not is_url(text):
        return

    url = re.search(r'https?://\S+', text).group(0)

    await message.answer("⏳ Завантажую...")

    try:
        ydl_opts = {
            "outtmpl": "video.%(ext)s",
            "format": "best[ext=mp4]",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.exists(filename):
            await message.answer("❌ Не вдалося скачати")
            return

        # перевірка розміру (Telegram ~50MB)
        if os.path.getsize(filename) > 50 * 1024 * 1024:
            await message.answer("❌ Відео занадто велике")
            os.remove(filename)
            return

        video = FSInputFile(filename)
        await message.answer_video(video)

        os.remove(filename)

    except Exception as e:
        await message.answer("❌ Соррі помилка.")


async def main():
    print("🤖 Бот запущений")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())