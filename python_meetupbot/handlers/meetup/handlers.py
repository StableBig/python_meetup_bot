from .keyboard_utils import make_choose_keyboard, make_speaker_keyboard, make_guest_keyboard, make_topic_keyboard, \
    make_keyboard_with_admin_features
from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, Filters
from python_meetupbot.models import Users, Speakers, Topics, Questions, Events
from python_meetupbot.handlers.meetup import static_text
from datetime import datetime

FEEDBACK_EVENT_COMMENTS, FEEDBACK_COMMENTS, FEEDBACK_QUESTIONS, GUEST_OPTIONS, ASK_QUESTION, LEAVE_FEEDBACK_TALK, \
    LEAVE_FEEDBACK_EVENT, CREATE_MEETUP, OPTION, MEETUP_END_TIME, MEETUP_DATE, MEETUP_START_TIME, SPEAKER_OPTIONS \
    = range(13)


def exit(update, _):
    first_name = update.message.from_user.first_name
    text = static_text.bye_bye.format(
        first_name=first_name
    )
    update.message.reply_text(text=text)
    return ConversationHandler.END


def guest_options(update: Update, _: CallbackContext):
    update.message.reply_text(static_text.choose_option, reply_markup=make_guest_keyboard())
    return GUEST_OPTIONS


def handle_guest_option(update: Update, _: CallbackContext):
    option = update.message.text

    if option == static_text.guest_options_buttons[0]:
        show_topics_schedule(update, _)
        return GUEST_OPTIONS

    elif option == static_text.guest_options_buttons[1]:
        update.message.reply_text(static_text.ask_question_text)
        return ASK_QUESTION

    # elif option == static_text.guest_options_buttons[2]:
    #     update.message.reply_text(static_text.leave_feedback_talk_text)
    #     return LEAVE_FEEDBACK_TALK

    # elif option == static_text.guest_options_buttons[3]:
    #     update.message.reply_text(static_text.leave_feedback_event_text)
    #     return LEAVE_FEEDBACK_EVENT

    return ConversationHandler.END


def ask_question(update: Update, _):
    question_text = update.message.text
    try:
        topic = Topics.objects.get(start__lt=datetime.now(), end__gt=datetime.now())
        Questions.objects.create(
            telegram_id=Users.objects.get(telegram_id=update.message.from_user.id),
            name=topic.event,
            speaker_id=topic.speaker,
            question=question_text
        )
        update.message.reply_text(static_text.question_sent)
        return ConversationHandler.END
    except:
        update.message.reply_text(static_text.no_topic)
        return ConversationHandler.END


# def leave_feedback_talk(update: Update, _):
#     feedback_text = update.message.text
#     try:
#         topic = Topics.objects.get(start__lt=datetime.now(), end__gt=datetime.now())
#         Comments.objects.create(
#             telegram_id=Users.objects.get(telegram_id=update.message.from_user.id),
#             name=topic.event,
#             speaker_id=topic.speaker,
#             question=feedback_text
#         )
#         update.message.reply_text(static_text.feedback_talk_sent)
#         return ConversationHandler.END
#     except:
#         update.message.reply_text(static_text.no_topic)
#         return ConversationHandler.END


# def leave_feedback_event(update: Update, _):
#     print('leave_feedback_event')
#     feedback_text = update.message.text
#     Eventcomments.objects.create(
#         telegram_id=Users.objects.get(telegram_id=update.message.from_user.id),
#         date=Events.objects.get(date=datetime.now().date()),
#         meetup_comment=feedback_text
#     )
#     update.message.reply_text(static_text.feedback_event_sent)
#     return ConversationHandler.END


# def show_events_schedule(update: Update, _):
#     events = Events.objects.all().order_by('date')
#
#     if not events:
#         update.message.reply_text(static_text.no_events)
#         return ConversationHandler.END
#
#     response = static_text.events_schedule_header
#     for event in events:
#         response += f"{static_text.event_date}: {event.date}\n"
#         response += f"{static_text.event_start}: {event.start}\n"
#         response += f"{static_text.event_end}: {event.end}\n"
#         response += "\n"
#
#     update.message.reply_text(response)
#     return ConversationHandler.END


def show_topics_schedule(update: Update, _):
    try:
        event = Events.objects.get(date=datetime.now().date())
        topics = Topics.objects.filter(event=event).order_by('start')

        if not topics:
            update.message.reply_text(static_text.no_topics)
            return ConversationHandler.END

        response = static_text.topics_schedule_header

        for topic in topics:
            response += f"{static_text.event_start}: {topic.start}\n"
            response += f"{static_text.event_end}: {topic.end}\n"
            response += f"{static_text.topic_speaker}: {topic.speaker}\n"
            response += f"{static_text.topic_name}: {topic.title}\n"
            response += "\n"
        update.message.reply_text(response)
        return ConversationHandler.END

    except:
        update.message.reply_text(static_text.no_event)
        return ConversationHandler.END


def get_speaker_commands(update: Update, _: CallbackContext):
    speaker = Users.objects.get(telegram_id=update.message.from_user.id)
    try:
        Speakers.objects.get(telegram_id=speaker)
        update.message.reply_text(text=static_text.speaker_text)
        update.message.reply_text(static_text.get_questions, reply_markup=make_speaker_keyboard())
        return SPEAKER_OPTIONS

    except Speakers.DoesNotExist:
        update.message.reply_text(static_text.only_for_speakers)
        return ConversationHandler.END


def get_speaker_choice(update: Update, _: CallbackContext):
    print('get_speaker_choice')
    speaker_option = update.message.text
    speaker = Users.objects.get(telegram_id=update.message.from_user.id)
    topics = Topics.objects.all()
    speaker_topics = [topic.title for topic in topics if topic.speaker.telegram_id == speaker]
    if speaker_option == static_text.speaker_choose[0]:
        get_questions(update, _, speaker)
        return ConversationHandler.END
    # elif speaker_option == static_text.speaker_choose[1]:
    #     get_topic(update, _, speaker_topics)
    # elif speaker_option in speaker_topics:
    #     get_topic_comments(update, _, speaker_option)
    # elif speaker_option == static_text.back:
    #     return get_speaker_commands(update, _)
    else:
        return ConversationHandler.END


def get_questions(update: Update, _, speaker):
    questions = Questions.objects.all()
    speaker_questions = [question for question in questions if question.speaker_id.telegram_id == speaker]
    if not speaker_questions:
        update.message.reply_text(static_text.no_questions)
        return ConversationHandler.END

    response = static_text.speaker_questions
    for question in speaker_questions:
        response += f"{question.telegram_id}: {question.question}\n"
        response += "\n"

    update.message.reply_text(response)
    return ConversationHandler.END


def get_topic(update: Update, _: CallbackContext, speaker_topics):
    update.message.reply_text(text=static_text.topics)
    update.message.reply_text(static_text.choose_option, reply_markup=make_topic_keyboard(speaker_topics))


# def get_topic_comments(update: Update, _, topic_name):
#     comments = Comments.objects.all()
#     topic_comments = [comment for comment in comments if comment.topic.title == topic_name]
#     if not topic_comments:
#         update.message.reply_text(static_text.topic_no_comments.format(topic_name))
#         return ConversationHandler.END
#
#     response = static_text.topic_comments.format(topic_name)
#     for comment in topic_comments:
#         response += f"{comment.telegram_id}: {comment.comment}\n"
#         response += "\n"
#
#     update.message.reply_text(response)
#     return ConversationHandler.END


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
    return ConversationHandler.END


def choose_admin_button(update: Update, _):
    print('choose_admin_button')
    answer = update.message.text
    print('answer', answer)
    if static_text.features_choose.index(answer) == 0:
        text = static_text.meetup_name
        update.message.reply_text(
            text=text
        )
        return CREATE_MEETUP
    elif static_text.features_choose.index(answer) == 1:
        text = static_text.admin_features
        update.message.reply_text(text=text,
                                  reply_markup=make_keyboard_with_admin_features())
    elif static_text.features_choose.index(answer) == 2:
        list_event = Events.objects.all().order_by('date')
        text = static_text.choose_meetup
        update.message.reply_text(
            text=text
        )
        for event in list_event:
            text = static_text.list_meetup.format(
                name=event.name,
                date=event.date,
                start_time=event.start,
                end_time=event.end
            )
            update.message.reply_text(text=text)
        return FEEDBACK_EVENT_COMMENTS
    elif static_text.features_choose.index(answer) == 3:
        list_topic = Topics.objects.all()
        text = static_text.choose_topic
        update.message.reply_text(
            text=text
        )
        for topic in list_topic:
            user = Speakers.objects.get(id=topic.speaker_id)
            text = static_text.list_topic.format(
                title=topic.title,
                speaker=user.fio,
                id=topic.id
            )
            update.message.reply_text(text=text)
        return FEEDBACK_COMMENTS


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


# def get_feedback_event_comments(update: Update, _):
#     print('get_feedback_comments')
#     event_id = Events.objects.get(name=update.message.text).id
#     feedbacks = Eventcomments.objects.filter(name_id=event_id)
#     for feedback in feedbacks:
#         print(feedback)
#         update.message.reply_text(text=str(feedback))


# def get_feedback_comments(update: Update, _):
#     print('get_feedback_questions')
#     print(update.message.text)
#     feedbacks = Comments.objects.filter(topic_id=update.message.text)
#     for feedback in feedbacks:
#         print(feedback)
#         update.message.reply_text(text=str(feedback))
