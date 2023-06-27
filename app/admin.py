from django.contrib import admin

from app.models import UserProfile, Interest, Event, Message, UserFavourite

admin.site.register(UserProfile)
admin.site.register(Interest)
admin.site.register(Event)
admin.site.register(Message)
admin.site.register(UserFavourite)
