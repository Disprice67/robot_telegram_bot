import asyncio
from aiogram import Bot, Dispatcher
from app import start_router, PrimaryUserCheckMiddleware, create_db
from config.config import BOT_TOKEN, ADMIN_CHAT_ID, REDIS_HOST, REDIS_PORT
from app.handlers.commands import set_bot_commands


bot = Bot(BOT_TOKEN)
dp = Dispatcher()
dp.include_router(start_router)
create_db()
dp.message.middleware(PrimaryUserCheckMiddleware())


async def on_startup(bot: Bot):
    await set_bot_commands(bot)


async def on_start():
    await dp.start_polling(bot, skip_updates=True)


# Основная функция для запуска бота
async def main():
    # Устанавливаем команды бота
    await on_startup(bot)

    # Запускаем polling
    await dp.start_polling(bot, skip_updates=True)

# Запуск приложения
if __name__ == "__main__":
    asyncio.run(main())
