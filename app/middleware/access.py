from aiogram import BaseMiddleware
from ..database.tdb_query import add_user_to_db, is_user_in_db
from aiogram import types

ALLOWED_USER_IDS = [530731938, 221748119]
USER_CACHE = {}

class PrimaryUserCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.Message, data: dict):
        user_id = event.from_user.id
        if user_id in USER_CACHE:
            return await handler(event, data)

        if user_id not in ALLOWED_USER_IDS:
            await event.answer("⛔ Доступ запрещен.")
            raise Exception("Access denied")

        if not is_user_in_db(user_id):
            add_user_to_db(user_id, event.chat.id)
            await event.answer(f"Ваш chat_id: {event.chat.id} успешно добавлен в базу данных.")

        USER_CACHE[user_id] = "active"
        return await handler(event, data)
