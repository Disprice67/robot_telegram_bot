import aioredis
import asyncio
import json
from typing import Optional
from app.queue.formatters import NotificationFormatter
from aiogram import types, Bot
from aiogram.types import FSInputFile
from pathlib import Path


async def connect_to_redis(redis_url: str, redis_port: int) -> aioredis.Redis:
    """
    Устанавливает соединение с Redis.
    """
    return aioredis.from_url(redis_url, port=redis_port, encoding="utf-8", decode_responses=True)


async def fetch_log_message(redis: aioredis.Redis, queue: str) -> Optional[dict]:
    """
    Извлекает сообщение из очереди Redis.

    :param redis: Объект Redis.
    :param queue: Название очереди.
    :return: Данные сообщения в виде словаря или None, если сообщение отсутствует.
    """
    try:
        log_message = await redis.brpop(queue)
        return json.loads(log_message[1]) if log_message else None
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        return None


async def send_notification(bot: Bot, chat_id: int, message: str) -> None:
    """
    Отправляет уведомление в Telegram.

    :param bot: Объект Telegram-бота.
    :param chat_id: Идентификатор чата.
    :param message: Текст сообщения.
    """
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


async def send_files(bot: Bot, chat_id: int, file_paths: list[str]) -> None:
    """
    Отправляет файлы в Telegram.

    :param bot: Объект Telegram-бота.
    :param chat_id: Идентификатор чата.
    :param file_paths: Список путей к файлам.
    """
    media = []
    for file_path in file_paths:
        try:
            document = FSInputFile(file_path)
            media.append(types.InputMediaDocument(media=document))
        except FileNotFoundError:
            await send_notification(bot, chat_id, f"❌ Файл не найден: {file_path}")
        except Exception as e:
            await send_notification(bot, chat_id, f"❌ Ошибка при обработке файла {file_path}: {e}")
    if media:
        try:
            await bot.send_media_group(chat_id=chat_id, media=media)
        except Exception as e:
            await send_notification(bot, chat_id, f"❌ Ошибка при отправке группы файлов: {e}")


async def process_logs(bot: Bot, chat_id: int, redis: aioredis.Redis, queue: str) -> None:
    """
    Обрабатывает логи из очередей Redis и отправляет уведомления в Telegram.

    :param bot: Объект Telegram-бота.
    :param chat_id: Идентификатор чата.
    :param redis: Объект Redis.
    :param queue: очередь.
    """
    robot_data_path = Path(__file__).parent.parent
    notification_data = await fetch_log_message(redis, queue)
    if not notification_data:
        return
    formatted_message = NotificationFormatter.format_message(notification_data)
    await send_notification(bot, chat_id, formatted_message)
    file_paths = [
        robot_data_path / 'data/robot/logs/robot.log' if notification_data.get("log_file_path") else None,
        robot_data_path / f'data/robot/excel_files/{notification_data.get("excel_file_path")}' if notification_data.get("excel_file_path") else None,
    ]
    file_paths = [path for path in file_paths if path]
    if file_paths:
        await send_files(bot, chat_id, file_paths)


async def listen_to_logs(redis_url: str, redis_port: int, bot: Bot, chat_id: int) -> None:
    """
    Основной цикл обработки очередей Redis.

    :param bot: Объект Telegram-бота.
    :param chat_id: Идентификатор чата.
    """
    try:
        redis = await connect_to_redis(redis_url, redis_port)
    except ConnectionError as e:
        await send_notification(bot, chat_id, f"❌ Ошибка подключения к Redis: {e}")
        return

    queue = "logs_queue"

    while True:
        try:
            await process_logs(bot, chat_id, redis, queue)
            await asyncio.sleep(1)
        except Exception as e:
            await send_notification(bot, chat_id, f"❌ Ошибка в цикле обработки очередей: {e}")
            await asyncio.sleep(1)
