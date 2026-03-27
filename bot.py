"""
PipBot — Умный модератор для Telegram
Точка входа: bot.py
"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database.models import init_db
from middlewares import GroupMiddleware, AntiSpamMiddleware
from handlers import start, admin, welcome, messages, settings
from utils.scheduler import setup_scheduler
from utils.logger import log


async def main():
    log.info("🐍 Starting PipBot...")

    await init_db()
    log.info("✅ Database initialized")

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Middlewares
    dp.message.middleware(GroupMiddleware())
    dp.callback_query.middleware(GroupMiddleware())
    dp.message.middleware(AntiSpamMiddleware())

    # Routers
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(welcome.router)
    dp.include_router(settings.router)
    dp.include_router(messages.router)

    # Scheduler
    scheduler = setup_scheduler(bot)
    scheduler.start()
    log.info("✅ Scheduler started")

    # Bot commands
    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="rules", description="Правила группы"),
        BotCommand(command="myprofile", description="Мой профиль"),
        BotCommand(command="shop", description="Магазин Pips 💰"),
        BotCommand(command="report", description="Пожаловаться (ответом на сообщение)"),
        BotCommand(command="warn", description="[Админ] Предупреждение"),
        BotCommand(command="unwarn", description="[Админ] Снять предупреждение"),
        BotCommand(command="mute", description="[Админ] Заглушить"),
        BotCommand(command="unmute", description="[Админ] Разглушить"),
        BotCommand(command="ban", description="[Админ] Заблокировать"),
        BotCommand(command="unban", description="[Админ] Разблокировать"),
        BotCommand(command="stats", description="[Админ] Статистика группы"),
        BotCommand(command="logs", description="[Админ] Последние логи"),
        BotCommand(command="settings", description="[Админ] Настройки группы"),
        BotCommand(command="setwelcome", description="[Админ] Задать приветствие"),
        BotCommand(command="setrules", description="[Админ] Задать правила"),
        BotCommand(command="badword", description="[Админ] Управление чёрным списком"),
        BotCommand(command="allowdomain", description="[Админ] Добавить домен в белый список"),
    ])

    log.info("🚀 PipBot is live! Press Ctrl+C to stop.")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()
        log.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
