import aioredis
import asyncio
import json
from typing import Optional
from app.queue.formatters import NotificationFormatter
from aiogram import types, Bot
from aiogram.types import FSInputFile
from pathlib import Path
from config.config import ROBOT_FILES


class AsyncRedisClient:
    def __init__(self, redis_url: str, redis_port: int, bot: Bot, admin_chat_id: int):
        self.redis_url = redis_url
        self.redis_port = redis_port
        self.bot = bot
        self.admin_chat_id = admin_chat_id

        self.redis: Optional[aioredis.Redis] = None

        self._connect_to_redis

    async def _connect_to_redis(self) -> Optional[aioredis.Redis]:
        """
        Создает клиент Redis и сохраняет его в self.redis.
        """
        try:
            self.redis = await aioredis.from_url(self.redis_url, port=self.redis_port, encoding="utf-8", decode_responses=True)
            return self.redis
        except ConnectionError as e:
            await self._send_notification(f"❌ Ошибка подключения к Redis: {e}")
            return None

    async def _fetch_log_message(self, queue_name: str) -> Optional[dict]:
        """
        Извлекает сообщение из очереди Redis.

        :param redis: Объект Redis.
        :param queue_name: Название очереди.
        :return: Данные сообщения в виде словаря или None, если сообщение отсутствует.
        """
        if self.redis is None:
            await self._send_notification("❌ Redis не подключен.")
            return None
        try:
            log_message = await self.redis.brpop(queue_name)
            return json.loads(log_message[1]) if log_message else None
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")
            return None

    async def push_to_queue(self, queue_name: str, message: dict) -> bool:
        """
        Отправляет сообщения в очередь Redis.

        :param queue_name: Название очереди.
        :param message: Отправляемое сообщение.
        :param redis: Объект Redis.
        :return: bool значение статуса отправки сообщения.
        """
        try:
            serialized_message = json.dumps(message)
            await self.redis.lpush(queue_name, serialized_message)
            return True
        except Exception as e:
            print(f"Ошибка отправки сообщения в очередь: {e}")
            return False

    async def _send_notification(self, message: str) -> None:
        """
        Отправляет уведомление в Telegram.

        :param bot: Объект Telegram-бота.
        :param chat_id: Идентификатор чата.
        :param message: Текст сообщения.
        """
        try:
            await self.bot.send_message(chat_id=self.admin_chat_id, text=message, parse_mode="HTML")
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")

    async def _send_files(self, file_paths: list[str]) -> None:
        """
        Отправляет файлы в Telegram.

        :param bot: Объект Telegram-бота.
        :param chat_id: Идентификатор чата.
        :param file_paths: Список путей к файлам.
        """
        media = []
        for file_path in file_paths:
            try:
                if not Path(file_path).exists():
                    await self._send_notification(f"❌ Файл не найден: {file_path}")
                    continue

                file_size = Path(file_path).stat().st_size
                if file_size > 50 * 1024 * 1024:
                    await self._send_notification(f"❌ Файл слишком большой: {file_path}")
                    continue

                document = FSInputFile(file_path)
                media.append(types.InputMediaDocument(media=document))

            except Exception as e:
                await self._send_notification(f"❌ Ошибка при обработке файла {file_path}: {e}")

        if media:
            try:
                await self.bot.send_media_group(chat_id=self.admin_chat_id, media=media)
            except Exception as e:
                await self._send_notification(f"❌ Ошибка при отправке группы файлов: {e}")

    async def _process_logs(self, queue: str) -> None:
        """
        Обрабатывает логи из очередей Redis и отправляет уведомления в Telegram.

        :param bot: Объект Telegram-бота.
        :param chat_id: Идентификатор чата.
        :param redis: Объект Redis.
        :param queue: очередь.
        """
        notification_data = await self._fetch_log_message(queue)
        if not notification_data:
            return
        formatted_message = NotificationFormatter.format_message(notification_data)
        await self._send_notification(formatted_message)
        excel_files_path = notification_data.get("excel_file_path")
        log_file_path = notification_data.get("log_file_path")
        file_paths = [
            ROBOT_FILES / 'logs' / 'robot.log' if log_file_path else None,
            ROBOT_FILES / 'excel_files' / excel_files_path if excel_files_path else None,
        ]
        file_paths = [path for path in file_paths if path]
        if file_paths:
            await self._send_files(file_paths)

    async def listen_to_logs(self) -> None:
        """
        Основной цикл обработки очередей Redis.

        :param bot: Объект Telegram-бота.
        :param chat_id: Идентификатор чата.
        """

        queue = "logs_queue"

        while True:
            try:
                await self._process_logs(queue)
                await asyncio.sleep(1)
            except Exception as e:
                await self._send_notification(f"❌ Ошибка в цикле обработки очередей: {e}")
                await asyncio.sleep(1)
