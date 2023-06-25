import logging
import sys

import telegram.error
from telegram import Bot
from telegram.ext import (CommandHandler, ConversationHandler, Dispatcher,
                          Filters, MessageHandler, Updater,
                          CallbackQueryHandler, ShippingQueryHandler)
from python_meetup.settings import DEBUG, TELEGRAM_TOKEN
from python_meetupbot.handlers.meetup.handlers import (guest_options, handle_guest_option, ask_question,
                                                       leave_feedback_talk, leave_feedback_event, exit,
                                                       GUEST_OPTIONS, ASK_QUESTION, LEAVE_FEEDBACK_TALK,
                                                       LEAVE_FEEDBACK_EVENT)
from python_meetupbot.handlers.common import handlers as common_handlers
from python_meetupbot.handlers.meetup import handlers as meetup_handlers
from python_meetupbot.handlers.admin import handlers as admin_handlers

meetup_handlers = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex('^(Гость)$'),
                       meetup_handlers.guest_options),
        MessageHandler(Filters.regex('^(Докладчик)$'),
                       meetup_handlers.get_speaker_commands),
        MessageHandler(Filters.regex('^(Организатор)$'),
                       admin_handlers.command_admin),
        MessageHandler(Filters.regex('^(Выход)$'),
                       meetup_handlers.exit),
    ],
    states={
            GUEST_OPTIONS: [MessageHandler(Filters.text & ~Filters.command, handle_guest_option)],
            ASK_QUESTION: [MessageHandler(Filters.text & ~Filters.command, ask_question)],
            LEAVE_FEEDBACK_TALK: [MessageHandler(Filters.text & ~Filters.command, leave_feedback_talk)],
            LEAVE_FEEDBACK_EVENT: [MessageHandler(Filters.text & ~Filters.command, leave_feedback_event)],
    },
    fallbacks=[
        CommandHandler("cancel", common_handlers.command_cancel)
    ]
    #
)

def setup_dispatcher(dp):
    dp.add_handler(meetup_handlers)

    dp.add_handler(CommandHandler("start", common_handlers.command_start))
    dp.add_handler(CommandHandler("cancel", common_handlers.command_cancel))
    # dp.add_handler(CommandHandler("admin", admin_handlers.command_admin))
    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f'https://t.me/{bot_info["username"]}'

    print(f"Pooling of '{bot_link}' started")

    updater.start_polling()
    updater.idle()


bot = Bot(TELEGRAM_TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except telegram.error.Unauthorized:
    logging.error(f"Invalid TELEGRAM_TOKEN.")
    sys.exit(1)

n_workers = 1 if DEBUG else 4
dispatcher = setup_dispatcher(
    Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True)
)
