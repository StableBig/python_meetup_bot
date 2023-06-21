import os
import json
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types


load_dotenv()

telegram_token = os.getenv('TELEGRAM_API_TOKEN')

# Включаем логгирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=telegram_token)
dp = Dispatcher(bot)

# Мок данных
user_data = {
    'users': {},
    'speakers': {
        '1': {'name': 'Валентин'},
        '2': {'name': 'Макс'}
    }
}


def get_user_role(user_id):
    return user_data['users'].get(str(user_id), {}).get('role')


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    user_id = message.from_user.id
    user_role = get_user_role(user_id)

    if user_role:
        # Повторно отправляем приветствие в зависимости от роли
        greeting_by_role = {
            'гость': 'Привет, гость! Ты можешь просматривать информацию о событиях и задавать вопросы.',
            'выступающий': 'Привет, выступающий! Ты можешь ответить на вопросы гостей.',
            'организатор': 'Привет, докладчик! Ты можешь публиковать информацию о своих докладах и отвечать на вопросы.'
        }
        await message.reply(greeting_by_role.get(user_role, 'Привет!'))
    else:
        # Предлагаем пользователю установить роль
        keyboard = types.InlineKeyboardMarkup()
        roles = [('Гость', 'гость'), ('Выступающий', 'выступающий'), ('Организатор', 'организатор')]
        for name, role in roles:
            button = types.InlineKeyboardButton(name, callback_data=f'setrole:{role}')
            keyboard.add(button)
        await message.reply('Выберите вашу роль:', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('setrole:'))
async def on_setrole(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_role = callback_query.data.split(':')[1]
    # Сохраняем роль пользователя
    user_data['users'][str(user_id)] = {'role': user_role}
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, f'Ваша роль установлена как {user_role}.')


@dp.message_handler(commands=['ask'])
async def on_ask(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    speakers = user_data['speakers']
    for id, speaker in speakers.items():
        button = types.InlineKeyboardButton(speaker['name'], callback_data=f'ask:{id}')
        keyboard.add(button)
    await message.reply('Выбери выступающего, чтобы задать вопрос:', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('ask:'))
async def on_question(callback_query: types.CallbackQuery):
    speaker_id = callback_query.data.split(':')[1]
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f'Вы можете задать вопрос выступающему с ID {speaker_id}')


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
