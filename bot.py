import os
from dotenv import load_dotenv
import logging
from aiogram import Bot, Dispatcher, types

'''
from aiogram.types import ParseMode
from aiogram.utils import executor
'''

load_dotenv()

telegram_token = os.getenv('TELEGRAM_API_TOKEN')

# Включаем логгирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=telegram_token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    # Приветствие и интро
    await message.reply('Привет! Я PythonMeetup BOT. Задавай вопросы выступающим и отслеживай программу мероприятия.')

@dp.message_handler(commands=['ask'])
async def on_ask(message: types.Message):
    # Показать выступающих и задавать вопросы
    keyboard = types.InlineKeyboardMarkup()
    # Выступающих нужно заменить на тех, что в базе данных
    speakers = [('Валентин', '1'), ('Макс', '2')]
    for name, id in speakers:
        button = types.InlineKeyboardButton(name, callback_data=f'ask:{id}')
        keyboard.add(button)
    await message.reply('Выбери выступающего, чтобы задать вопрос:', reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('ask:'))
async def on_question(callback_query: types.CallbackQuery):
    # Достать id выступающего
    speaker_id = callback_query.data.split(":")[1]
    # Оповестить пользователя
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f'Вы можете задать вопрос выступающему с ID {speaker_id}')

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
