import uuid

from telegram import Update
from telegram.ext import (
    ConversationHandler, CallbackContext
)

from selfstoragebot.handlers.common import static_text
from python_meetupbot.models import Users
from .keyboard_utils import make_keyboard_for_start_command


def command_start(update: Update, context):
    print('command_start')
    if update.message:
        user_info = update.message.from_user.to_dict()
    else:
        user_info = {}
        user_info['id'] = context.user_data['user_id']
        user_info['username'] = context.user_data['username']
        user_info['first_name'] = context.user_data['first_name']
    user, created = Users.objects.get_or_create(
        telegram_id=user_info['id'],
        username=user_info['username'],
    )

    args = context.args
    if args:
        link_id = args[0]
        try:
            invitation_link = InvitationLink.objects.get(link_id=link_id)
            invitation_link.click_count += 1
            invitation_link.save()
        except InvitationLink.DoesNotExist:
            pass

    if created:
        text = static_text.start_created.format(
            first_name=user_info['first_name']
        )
    else:
        text = static_text.start_not_created.format(
            first_name=user_info['first_name']
        )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=make_keyboard_for_start_command(),
    )


def command_cancel(update: Update, _):
    print('command_cancel')
    text = static_text.cancel_text
    update.message.reply_text(
        text=text,
        reply_markup=make_keyboard_for_start_command(),
    )
    return ConversationHandler.END
