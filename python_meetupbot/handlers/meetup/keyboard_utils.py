from telegram import KeyboardButton, ReplyKeyboardMarkup
from .static_text import speaker_choose, guest_options_buttons, features_choose, back
from python_meetupbot.models import Topics

def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def make_choose_keyboard() -> ReplyKeyboardMarkup:
    print('make_choose_keyboard')
    buttons = [KeyboardButton(choose) for choose in features_choose]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=3),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup


def make_speaker_keyboard() -> ReplyKeyboardMarkup:
    print('make_speaker_keyboard')
    buttons = [KeyboardButton(button) for button in speaker_choose]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=2),
        resize_keyboard=True
    )
    return reply_markup


def make_topic_keyboard(speaker_topics) -> ReplyKeyboardMarkup:
    print('make_topic_keyboard')
    buttons = [KeyboardButton(button) for button in speaker_topics]
    buttons.append(back)
    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=1),
        resize_keyboard=True
    )
    return reply_markup


def make_guest_keyboard() -> ReplyKeyboardMarkup:
    print('make_guest_keyboard')
    buttons = [KeyboardButton(button) for button in guest_options_buttons]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(buttons, n_cols=1),
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return reply_markup
