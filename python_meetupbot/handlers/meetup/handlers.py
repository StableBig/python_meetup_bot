from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler
from python_meetupbot.models import Users, Speakers
from python_meetupbot.handlers.meetup import static_text
from  keyboard_utils import make_speaker_keyboard

def test(update: Update, _):
    pass


def get_speaker_commands(update: Update, _):
    speaker = Users.objects.get(telegram_id=update.message.from_user.id)
    if Speakers.objects.filter(telegram_id=speaker) is None:
        update.message.reply_text(static_text.only_for_speakers)
        return ConversationHandler.END
    text = static_text.speaker_text
    update.message.reply_text(text=text,
                              reply_markup=make_speaker_keyboard())


def exit(update, _):
    first_name = update.message.from_user.first_name
    text = static_text.bye_bye.format(
        first_name=first_name
    )
    update.message.reply_text(text=text)
    return ConversationHandler.END
