import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command, Text

telegram_token = os.environ.get('TELEGRAM_API_TOKEN')
admin_password = os.environ.get('ADMIN_PASSWORD')

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
    },
    'questions': []  # Список вопросов гостей
}


def get_user_role(user_id):
    return user_data['users'].get(str(user_id), {}).get('role')


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    user_id = message.from_user.id
    user_role = get_user_role(user_id)

    if user_role:
        # Повторно отправляем приветствие в зависимости от роли
        await message.reply(f'Привет! Вы {user_role}.')
    else:
        # Предлагаем пользователю установить роль
        keyboard = types.InlineKeyboardMarkup()
        roles = [('Гость', 'гость'), ('Докладчик', 'докладчик'), ('Организатор', 'организатор')]
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

    # Запрашиваем пароль, если это организатор или докладчик
    if user_role == 'организатор' or user_role == 'докладчик':
        await bot.send_message(user_id, 'Пожалуйста, введите пароль:')
    elif user_role == 'гость':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Задать вопрос", callback_data='ask'))
        await bot.send_message(user_id,
                               f'Ваша роль установлена как {user_role}. Вы можете задать вопрос докладчику.',
                               reply_markup=keyboard)
    else:
        await bot.send_message(user_id, 'Вы не авторизованы.')


@dp.message_handler(lambda message: get_user_role(message.from_user.id) in ['организатор', 'докладчик'])
async def on_password_entry(message: types.Message):
    user_id = message.from_user.id
    user_role = get_user_role(user_id)
    password = message.text

    if user_role == 'организатор' and password == admin_password:
        await message.reply('Доступ разрешен. Вы можете начать публиковать информацию о своих встречах.')
    elif user_role == 'докладчик' and password == admin_password:
        await message.reply('Доступ разрешен. Вы можете начать отвечать на вопросы гостей.')
    else:
        await message.reply('Неверный пароль. Попробуйте еще раз.')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('ask'))
async def on_ask(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, 'Введите ваш вопрос:')
    # Устанавливаем состояние, чтобы ожидать ввода вопроса от гостя
    await dp.current_state().set_state('waiting_for_question')


@dp.message_handler(state='waiting_for_question', content_types=types.ContentTypes.TEXT)
async def on_guest_question_entry(message: types.Message):
    user_id = message.from_user.id
    question_text = message.text
    user_data['questions'].append({'user_id': user_id, 'question': question_text})
    await message.reply('Ваш вопрос отправлен!')
    # Сбрасываем состояние после получения вопроса от гостя
    await dp.current_state().reset_state()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('setrole:'))
async def on_setrole(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_role = callback_query.data.split(':')[1]
    # Сохраняем роль пользователя
    user_data['users'][str(user_id)] = {'role': user_role}
    await bot.answer_callback_query(callback_query.id)

    # Запрашиваем пароль, если это организатор или докладчик
    if user_role == 'организатор' or user_role == 'докладчик':
        await bot.send_message(user_id, 'Пожалуйста, введите пароль:')
    elif user_role == 'гость':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Задать вопрос', callback_data='ask'))
        await bot.send_message(user_id,
                               f'Ваша роль установлена как {user_role}. Вы можете задать вопрос докладчику.',
                               reply_markup=keyboard)
    else:
        await bot.send_message(user_id, 'Вы не авторизованы.')


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
