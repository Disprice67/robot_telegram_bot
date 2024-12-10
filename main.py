import asyncio
from aiogram import Bot, Dispatcher
from presentation.telegram_bot.redis_listener import listen_to_logs
from presentation.telegram_bot.handlers import start_router
from presentation.telegram_bot.middleware import PrimaryUserCheckMiddleware
from presentation.telegram_bot.tdb_query import create_db
from config.config import BOT_TOKEN, ADMIN_CHAT_ID


bot = Bot(BOT_TOKEN)
dp = Dispatcher()
dp.include_router(start_router)
create_db()
dp.message.middleware(PrimaryUserCheckMiddleware())


async def on_start():
    await dp.start_polling(bot, skip_updates=True)


async def main():
    listen_task = asyncio.create_task(listen_to_logs(bot, ADMIN_CHAT_ID))
    bot_task = asyncio.create_task(on_start())
    await asyncio.gather(listen_task, bot_task)

if __name__ == "__main__":
    asyncio.run(main())
