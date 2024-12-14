from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from .menu import get_main_menu, get_file_type_menu
from aiogram import F

start_router = Router()

@start_router.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Добро пожаловать!", reply_markup=get_main_menu())

@start_router.message(F.text == 'Обновить файл')
async def handle_update_file(message: Message):
    await message.answer("Выберите тип файла:", reply_markup=get_file_type_menu())

@start_router.message(F.text.in_(["Свод", "Закупки"]))
async def handle_file_choice(message: Message):
    await message.answer("Пришлите файл для загрузки.")

# @start_router.message(F.document)
# async def handle_file_upload(message: Message):
#     if message.document:
#         file_path = await message.document.download(destination_dir="uploads")
#         await excel_service.process_file(file_path)
#         await message.answer("Файл обработан.")
