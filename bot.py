import asyncio
import os
import re
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from better_profanity import profanity

# Токен
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN not set")

# Настройка мата
profanity.load_censor_words()
russian_profanity = ["хуй", "пизда", "бля", "ебать", "сука", "мудак", "пидор"]
profanity.add_censor_words(russian_profanity)

# Разрешённые ссылки
ALLOWED_DOMAINS = ["t.me", "telegram.me", "youtube.com", "youtu.be"]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

def has_forbidden_link(text: str) -> bool:
    urls = re.findall(r'(https?://[^\s]+|www\.[^\s]+)', text)
    for url in urls:
        allowed = False
        for domain in ALLOWED_DOMAINS:
            if domain in url:
                allowed = True
                break
        if not allowed:
            return True
    return False

@dp.message()
async def filter_message(message: types.Message):
    if not message.text or message.from_user.id == bot.id:
        return
    
    text = message.text.lower()
    
    if profanity.contains_profanity(text):
        await message.delete()
        await message.reply("❌ Мат запрещён!")
        return
    
    if has_forbidden_link(text):
        await message.delete()
        await message.reply("❌ Ссылки запрещены!")
        return

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply("🐍 PipBot запущен! Добавьте меня в группу и дайте права администратора.")

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.reply("📝 Бот удаляет мат и ссылки. /start - меню")

async def main():
    print("🤖 PipBot запущен!")
    await dp.start_polling(bot)

if name == "__main__":
    asyncio.run(main())
