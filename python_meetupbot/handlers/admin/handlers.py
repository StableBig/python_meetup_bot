from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext

from python_meetupbot.handlers.admin import static_text
from python_meetupbot.models import Users
from .keyboard_utils import make_keyboard_with_admin_features

# ADMIN_BUTTON, CREATE_MEETUP = range(2)


# def command_admin(update: Update, _):
#     print('command_admin')
#     user = Users.objects.get(telegram_id=update.message.from_user.id)
#     if not user.is_admin:
#         update.message.reply_text(static_text.only_for_admins)
#         return ConversationHandler.END
#     text = static_text.admin_features
#
#     update.message.reply_text(text=text,
#                               reply_markup=make_keyboard_with_admin_features())
#     print('urrr')
#     return choose_admin_button


# def choose_admin_button(update: Update, context: CallbackContext):
#     print('choose_admin_button')
#     query = update.callback_query.data
#     if query == '1':
#         print(query)
#         return CREATE_MEETUP
#     elif query == '2':
#         pass
#     else:
#         pass


