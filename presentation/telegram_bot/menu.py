from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

# Главное меню
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Обновить файл"))
    return builder.as_markup(resize_keyboard=True)

# Меню выбора типа файла
def get_file_type_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Свод"))
    builder.add(KeyboardButton(text="Закупки"))
    return builder.as_markup(resize_keyboard=True)