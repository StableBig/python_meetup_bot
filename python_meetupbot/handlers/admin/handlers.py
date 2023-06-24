from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler

from python_meetupbot.handlers.admin import static_text
from python_meetupbot.models import Users, Events
from .keyboard_utils import make_keyboard_with_admin_features


def command_admin(update: Update, _):
    print('command_admin')
    user = Clients.objects.get(telegram_id=update.message.from_user.id)
    if not user.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return ConversationHandler.END
    text = static_text.admin_features

    update.message.reply_text(text=text,
                              reply_markup=make_keyboard_with_admin_features())
