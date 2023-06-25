from django.contrib import admin

from .models import Users, Comments, Topics, Events, Speakers


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'telegram_id', 'username', 'first_name', 'last_name',
        'is_admin',
    ]
    search_fields = ['telegram_id', 'username', 'last_name']


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'telegram_id', 'speaker_id', 'comment'
    ]

    search_fields = ['date', 'telegram_id', 'speaker_id']


@admin.register(Topics)
class TopicsAdmin(admin.ModelAdmin):
    list_display = [
        'event', 'speaker', 'title', 'start', 'end'
    ]

    search_fields = [
        'event', 'speaker', 'title'
    ]


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'date', 'start', 'end'
    ]

    search_fields = [
        'name', 'date'
    ]


@admin.register(Speakers)
class SpeakersAdmin(admin.ModelAdmin):
    list_display = [
        'telegram_id', 'fio', 'email'
    ]

    search_fields = [
        'fio', 'email'
    ]
