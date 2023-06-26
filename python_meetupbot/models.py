import uuid

from django.db import models
from django.utils import timezone


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Users(UUIDMixin, TimeStampedMixin):
    telegram_id = models.IntegerField(unique=True, default=False)
    username = models.CharField(
        max_length=64,
        null=True,
        blank=False,
        verbose_name='User Name'
    )
    first_name = models.CharField(
        max_length=256,
        null=True,
        blank=False,
        verbose_name='First Name'
    )
    last_name = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name='Last Name'
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Phone Number'
    )
    email = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='email'
    )
    is_admin = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        verbose_name='Администратор'
    )

    def __str__(self):
        if self.username:
            return f'@{self.username}'
        else:
            return f'{self.telegram_id}'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Speakers(UUIDMixin, TimeStampedMixin):
    telegram_id = models.ForeignKey(Users, on_delete=models.DO_NOTHING, related_name='tg_id', null=True, blank=True,
                                    default=False)
    fio = models.CharField(max_length=100, verbose_name='FIO Speaker', null=True, blank=True)
    email = models.CharField(max_length=100, verbose_name='Email speaker', null=True, blank=True)

    class Meta:
        verbose_name = 'Speaker'
        verbose_name_plural = 'Speakers'

    def __str__(self):
        return f'{self.fio} - {self.email}'


class Events(UUIDMixin, TimeStampedMixin):
    name = models.CharField(max_length=100, verbose_name='event name', null=True, blank=True)
    date = models.DateField(verbose_name='Date of the event', default=timezone.now, )
    start = models.TimeField(verbose_name='Time start event', null=True, blank=True)
    end = models.TimeField(verbose_name='Time end event', null=True, blank=True)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f'Event {self.name}-{self.date}'


class Topics(UUIDMixin, TimeStampedMixin):
    event = models.ForeignKey(Events, on_delete=models.DO_NOTHING, verbose_name='Event', null=True)
    speaker = models.ForeignKey(Speakers, on_delete=models.DO_NOTHING, verbose_name='Speaker', null=True)
    title = models.CharField(max_length=300, verbose_name='Topic', null=True)
    start = models.TimeField(verbose_name='Topic start time', null=True,
                             blank=True)
    end = models.TimeField(verbose_name='Topic end time', null=True,
                           blank=True)

    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'

    def __str__(self):
        return f'{self.title} - {self.speaker.fio}'


# class Comments(UUIDMixin, TimeStampedMixin):
#     telegram_id = models.ForeignKey(Users, on_delete=models.DO_NOTHING, related_name='td_id', null=True, blank=True,
#                                     default=False)
#     date = models.ForeignKey(Events, on_delete=models.DO_NOTHING, related_name='date_event', default=False)
#     speaker = models.ForeignKey(Speakers, on_delete=models.DO_NOTHING, related_name='speaker', null=True)
#     topic = models.ForeignKey(Topics, on_delete=models.DO_NOTHING, related_name='topic', null=True)
#     comment = models.CharField(max_length=200, verbose_name='Comment to the speaker', null=True,
#                                blank=True)
#
#     class Meta:
#         verbose_name = 'Comment'
#         verbose_name_plural = 'Comments'
#
#     def __str__(self):
#         return f'{self.telegram_id} - {self.comment}'


class Questions(UUIDMixin, TimeStampedMixin):
    telegram_id = models.ForeignKey(Users, on_delete=models.DO_NOTHING, related_name='questions_td_id', null=True,
                                    blank=True, default=False)
    name = models.ForeignKey(Events, on_delete=models.DO_NOTHING, related_name='Eventname', default=False)
    speaker_id = models.ForeignKey(Speakers, on_delete=models.DO_NOTHING, related_name='questions_speaker', null=True)
    question = models.CharField(max_length=200, verbose_name='Question to the speaker', null=True, blank=True)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f'{self.telegram_id} - {self.question}'


# class Eventcomments(UUIDMixin, TimeStampedMixin):
#     telegram_id = models.ForeignKey(Users, on_delete=models.DO_NOTHING, related_name='Event_comments_td_id', null=True,
#                                     blank=True, default=False)
#     name = models.ForeignKey(Events, on_delete=models.DO_NOTHING, related_name='Event_name', default=False)
#     meetup_comment = models.CharField(max_length=200, verbose_name='Comment about meetup', null=True, blank=True)
#
#     class Meta:
#         verbose_name = 'Meetup Comment'
#         verbose_name_plural = 'Meetup Comments'
#
#     def __str__(self):
#         return f'{self.telegram_id} - {self.meetup_comment}'
