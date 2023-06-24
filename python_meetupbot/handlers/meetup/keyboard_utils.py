import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .static_text import speaker_choose


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def make_speaker_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(speaker_choose[0],
                              callback_data='questions')],
        [InlineKeyboardButton(speaker_choose[1],
                              callback_data='comments')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    return reply_markup
