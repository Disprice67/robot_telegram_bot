import asyncio
from aiogram import Bot, Dispatcher
from app import listen_to_logs, start_router, PrimaryUserCheckMiddleware, create_db
from config.config import BOT_TOKEN, ADMIN_CHAT_ID, REDIS_URL


bot = Bot(BOT_TOKEN)
dp = Dispatcher()
dp.include_router(start_router)
create_db()
dp.message.middleware(PrimaryUserCheckMiddleware())


async def on_start():
    await dp.start_polling(bot, skip_updates=True)


async def main():
    listen_task = asyncio.create_task(listen_to_logs(REDIS_URL, bot, ADMIN_CHAT_ID))
    bot_task = asyncio.create_task(on_start())
    await asyncio.gather(listen_task, bot_task)

if __name__ == "__main__":
    asyncio.run(main())
