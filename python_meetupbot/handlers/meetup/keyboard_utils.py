from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from .static_text import (
    features_choose
)


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
