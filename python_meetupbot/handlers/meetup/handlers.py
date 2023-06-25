from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler
from python_meetupbot.models import Users, Events
from python_meetupbot.handlers.meetup import static_text
from .keyboard_utils import make_choose_keyboard

CREATE_MEETUP, OPTION, MEETUP_END_TIME, MEETUP_DATE, MEETUP_START_TIME = range(5)


def test(update: Update, _):
    pass


def exit(update, _):
    first_name = update.message.from_user.first_name
    text = static_text.bye_bye.format(
        first_name=first_name
    )
    update.message.reply_text(text=text)
    return ConversationHandler.END


def create_meetup(update: Update, meetup_description):
    print('create_meetup')
    meetup_description.bot_data['meetup_name'] = update.message.text
    text = static_text.meetup_date
    update.message.reply_text(
        text=text
    )
    return MEETUP_DATE


def meetup_date(update: Update, meetup_description):
    print('meetup_date')
    meetup_description.bot_data['meetup_date'] = update.message.text
    text = static_text.meetup_start_time
    update.message.reply_text(
        text=text
    )
    return MEETUP_START_TIME


def meetup_start_time(update: Update, meetup_description):
    print('meetup_start_time')
    print(update.message.text)
    meetup_description.bot_data['meetup_start_time'] = update.message.text
    text = static_text.meetup_end_time
    update.message.reply_text(
        text=text
    )
    return MEETUP_END_TIME


def meetup_end_time(update: Update, meetup_description):
    print('meetup_end_time')
    meetup_description.bot_data['meetup_end_time'] = update.message.text
    event = Events(name=meetup_description.bot_data['meetup_name'],
                   date=meetup_description.bot_data['meetup_date'],
                   start=meetup_description.bot_data['meetup_start_time'],
                   end=meetup_description.bot_data['meetup_end_time']
                   )
    event.save()
    text = static_text.meetup_created
    update.message.reply_text(
        text=text
    )


def choose_admin_button(update: Update, _):
    print('choose_admin_button')
    answer = update.message.text
    if static_text.features_choose.index(answer) == 0:
        text = static_text.meetup_name
        update.message.reply_text(
            text=text
        )
        return CREATE_MEETUP
    elif static_text.features_choose.index(answer) == 1:
        pass
    else:
        pass


def organization_option(update: Update, _):
    print('organization_option')
    user = Users.objects.get(telegram_id=update.message.from_user.id)
    if not user.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return ConversationHandler.END
    text = static_text.admin_features

    update.message.reply_text(text=text,
                              reply_markup=make_choose_keyboard())
    return OPTION
