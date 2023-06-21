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
    pass


@admin.register(Topics)
class TopicsAdmin(admin.ModelAdmin):
    pass


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    pass


@admin.register(Speakers)
class SpeakersAdmin(admin.ModelAdmin):
    pass
