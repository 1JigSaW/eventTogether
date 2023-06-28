from django.contrib import admin

from app.models import UserProfile, Interest, Event, Message, UserFavourite, Language

admin.site.register(UserProfile)
admin.site.register(Interest)
admin.site.register(Language)
admin.site.register(Event)
admin.site.register(Message)
admin.site.register(UserFavourite)
