class NotificationFormatter:
    """Класс для форматирования сообщений уведомлений."""

    @staticmethod
    def format_message(notification: dict) -> str:
        """Форматирует сообщение на основе типа уведомления."""
        notification_type = notification.get("type")

        if notification_type == "CRITICAL":
            return (
                f"⚠️ <b>Критическая ошибка!</b>\n"
                f"📂 <b>Лог файл: Во вложении</b>\n"
                "\n🔴 <i>Требуется немедленное внимание!</i>"
                "\n🔴 <i>Сервис недоступен!</i>"
            )

        elif notification_type == "SUCCESS":
            return (
                f"✅ <b>Успешно обработан файл:</b> {notification.get('file_name')}\n"
                "\n🎉 <i>Файл обновлен и записан в систему.</i>"
            )

        elif notification_type == "ERROR":
            return (
                f"🚨 <b>Уровень:</b> {notification_type}\n"
                f"📄 <b>Файл:</b> {notification.get('file_name', 'Файла нет')}\n"
                f"📊 <b>Excel файл:</b> {notification.get('excel_file_path', 'Файла нет')}\n"
                "\n🔍 <i>Пожалуйста, проверьте проблему.</i>"
            )

        return "⚠️ <b>Неизвестный тип уведомления</b>"
