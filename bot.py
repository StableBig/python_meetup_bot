import os
import django
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import BoundFilter
from asgiref.sync import async_to_sync, sync_to_async
from django.conf import settings


# Установка переменных окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_meetup.settings')
django.setup()

from django.contrib.auth.models import User, Group
from python_meetupbot.models import Events, Users, Speakers, Comments, Topics

telegram_token = settings.TELEGRAM_TOKEN
admin_password = os.environ.get('ADMIN_PASSWORD')

# Включаем логгирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=telegram_token)
dp = Dispatcher(bot)


class Form(StatesGroup):
    waiting_for_question = State()
    waiting_for_password = State()
    waiting_for_event_registration = State()
    waiting_for_speaker_topic = State()


class CommentForm(StatesGroup):
    waiting_for_speaker_selection = State()
    waiting_for_comment_text = State()


class UserRoleFilter(BoundFilter):
    key = 'user_role'

    def __init__(self, user_role):
        self.user_role = user_role

    async def check(self, message: types.Message):
        # Здесь можем добавить нашу логику для проверки роли пользователя.
        # Например, можно проверить роль пользователя в базе данных.
        return True


# Регистрируем фильтр
dp.filters_factory.bind(UserRoleFilter)


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    user_id = message.from_user.id

    # Проверить, существует ли пользователь в базе данных
    user, created = await sync_to_async(Users.objects.get_or_create)(telegram_id=user_id)

    # Предлагаем пользователю установить роль, если это первый вход
    if created:
        keyboard = types.InlineKeyboardMarkup()
        roles = [('Гость', 'гость'), ('Докладчик', 'докладчик'), ('Организатор', 'организатор')]
        for name, is_admin in roles:
            button = types.InlineKeyboardButton(name, callback_data=f'setrole:{is_admin}')
            keyboard.add(button)
        await message.reply('Выберите вашу роль:', reply_markup=keyboard)
    else:
        await message.reply('Добро пожаловать обратно!')
        # Отправляем кнопки на основе роли пользователя
        await send_action_buttons(message, user.is_admin)


@dp.message_handler(lambda message: message.text.lower() == 'регистрация на событие', state='*', user_role='докладчик')
async def register_for_event(message: types.Message):
    await Form.waiting_for_event_registration.set()
    await message.reply('Введите дату события (гггг-мм-дд):')


@dp.message_handler(state=Form.waiting_for_event_registration, content_types=types.ContentTypes.TEXT)
async def on_event_date_entry(message: types.Message, state: FSMContext):
    event_date = message.text
    # Проверяем, существует ли событие с указанной датой
    event = await sync_to_async(Events.objects.filter)(date=event_date).first()

    if event:
        # Сохраняем идентификатор события во временное хранилище
        await state.update_data(event_id=event.id)
        await Form.waiting_for_speaker_topic.set()
        await message.reply('Введите название вашей темы:')
    else:
        await message.reply('Событие с указанной датой не найдено. Пожалуйста, введите дату снова:')


@dp.message_handler(state=Form.waiting_for_speaker_topic, content_types=types.ContentTypes.TEXT)
async def on_speaker_topic_entry(message: types.Message, state: FSMContext):
    topic_title = message.text
    data = await state.get_data()
    event_id = data.get('event_id')
    speaker_telegram_id = message.from_user.id

    # Получаем speaker, или создаем
    speaker, created = await sync_to_async(Speakers.objects.get_or_create)(
        telegram_id=speaker_telegram_id,
        defaults={'fio': message.from_user.full_name}
    )

    # Создаем новую тему с указанной темой и связанным докладчиком
    topic = await sync_to_async(Topics.objects.create)(
        title=topic_title,
        event_id=event_id,
        speaker=speaker
    )

    await message.reply('Ваша тема успешно зарегистрирована!')
    await state.finish()


@dp.message_handler(lambda message: message.text.lower() == 'посмотреть темы', state='*')
async def view_event_topics(message: types.Message):
    events = await sync_to_async(Events.objects.all)()
    events_message = '\n'.join([f'{event.date}: /event_{event.id}' for event in events])
    await message.reply(f'Выберите дату события:\n{events_message}')


@dp.message_handler(lambda message: message.text.lower().startswith('/event_'), state='*')
async def on_event_selected(message: types.Message):
    event_id = message.text.split('_')[1]
    topics = await sync_to_async(Topics.objects.filter)(event_id=event_id)
    topics_message = '\n'.join([f'{topic.title} ({topic.speaker.fio})' for topic in topics])
    await message.reply(f'Темы события:\n{topics_message}')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('setrole:'))
async def on_setrole(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_role = callback_query.data.split(':')[1]

    # Сохраняем роль пользователя в базу данных
    user = await sync_to_async(Users.objects.get)(telegram_id=user_id)
    user.role = user_role
    await sync_to_async(user.save)()

    # Отправляем сообщение с инструкциями в зависимости от выбранной роли
    if user_role in ['организатор', 'докладчик']:
        await bot.send_message(user_id, 'Пожалуйста, введите пароль для доступа.')
        await Form.waiting_for_password.set()
    elif user_role == 'гость':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Задать вопрос', callback_data='ask'))
        await bot.send_message(user_id,
                               'Вы можете задать вопрос докладчику.',
                               reply_markup=keyboard)


@dp.message_handler(state=Form.waiting_for_password, content_types=types.ContentTypes.TEXT)
async def on_password_entry(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await sync_to_async(Users.objects.get)(telegram_id=user_id)
    password = message.text

    # Проверить пароль и разрешить доступ к функциям организатора или докладчика (или УДАЛИТЬ)
    if user.role in ['организатор', 'докладчик'] and password == admin_password:
        await message.reply('Доступ разрешен.')
        if user.role == 'организатор':
            # Разрешить доступ к панели организатора - СДЕЛАТЬ
            await message.reply('Вы можете начать публиковать информацию о своих встречах.')
        else:
            # Разрешить доступ к панели докладчика - СДЕЛАТЬ
            await message.reply('Вы можете начать отвечать на вопросы гостей.')
    else:
        await message.reply('Неверный пароль. Попробуйте еще раз.')

    await state.finish()


async def send_action_buttons(message: types.Message, role: str):
    keyboard = types.InlineKeyboardMarkup()

    if not role:
        buttons = [
            ('Задать вопрос', 'ask_question'),
            ('Расписание мероприятий', 'schedule')
            # Добавить другие кнопки для гостей...
        ]
    elif role == 'докладчик':
        buttons = [
            ('Посмотреть вопросы', 'view_questions'),
            # Добавить другие кнопки для докладчиков...
        ]
    elif role == 'организатор':
        buttons = [
            ('Добавить докладчика', 'add_speaker'),
            ('Изменить программу', 'change_program'),
            # Добавить другие кнопки для организаторов...
        ]

    for name, callback_data in buttons:
        button = types.InlineKeyboardButton(name, callback_data=callback_data)
        keyboard.add(button)

    await message.reply('Выберите действие:', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text.lower() == 'оставить комментарий', state='*')
async def leave_comment(message: types.Message, state: FSMContext):
    speakers = await sync_to_async(Speakers.objects.all)()
    speakers_message = '\n'.join([f'{speaker.fio}: /speaker_{speaker.id}' for speaker in speakers])
    await message.reply(f'Выберите докладчика для комментария:\n{speakers_message}')
    await state.set_state(CommentForm.waiting_for_speaker_selection)


@dp.message_handler(lambda message: message.text.lower().startswith('/speaker_'),
                    state=CommentForm.waiting_for_speaker_selection)
async def on_speaker_selected(message: types.Message, state: FSMContext):
    speaker_id = message.text.split('_')[1]
    await state.update_data(speaker_id=speaker_id)
    await message.reply('Пожалуйста, введите текст комментария:')
    await CommentForm.waiting_for_comment_text.set()


@dp.message_handler(state=CommentForm.waiting_for_comment_text, content_types=types.ContentTypes.TEXT)
async def on_comment_entry(message: types.Message, state: FSMContext):
    comment_text = message.text
    data = await state.get_data()
    speaker_id = data.get('speaker_id')
    telegram_user_id = message.from_user.id

    # Пользователь, который оставляет комментарий
    user = await sync_to_async(Users.objects.get)(telegram_id=telegram_user_id)

    # Создать новый комментарий
    comment = await sync_to_async(Comments.objects.create)(
        telegram_id=user,
        speaker_id_id=speaker_id,
        comment=comment_text
    )

    await message.reply('Ваш комментарий успешно сохранен!')
    await state.finish()


# Избавиться от on_ask
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('ask'))
async def on_ask(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, 'Введите ваш вопрос:')
    await Form.waiting_for_question.set()


@dp.callback_query_handler(lambda c: c.data == 'ask_question')
async def on_ask_question(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, 'Введите ваш вопрос:')
    await Form.waiting_for_question.set()


@dp.message_handler(state=Form.waiting_for_question, content_types=types.ContentTypes.TEXT)
async def on_guest_question_entry(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    question_text = message.text
    user = await sync_to_async(Users.objects.get)(telegram_id=user_id)

    # Сохраняем вопрос в базе данных
    await sync_to_async(Comments.objects.create)(user=user, text=question_text)

    await message.reply('Ваш вопрос отправлен!')
    await state.finish()


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
