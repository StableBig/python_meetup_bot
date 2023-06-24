from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler

from python_meetupbot.handlers.admin import static_text


def test(update: Update, _):
    pass


def get_speaker_commands(update: Update, _):
    pass


def exit(update, _):
    first_name = update.message.from_user.first_name
    text = static_text.bye_bye.format(
        first_name=first_name
    )
    update.message.reply_text(text=text)
    return ConversationHandler.END
