import pycountry
from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('NB', 'Non-Binary'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    age = models.PositiveIntegerField()
    language = models.ManyToManyField('Language')
    interests = models.ManyToManyField('Interest', related_name='interests')
    description = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    organizer_event = models.ForeignKey('Event', related_name='organizer_events', on_delete=models.CASCADE, null=True,
                                        blank=True)
    events = models.ManyToManyField('Event', related_name='events', blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Interest(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Language(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    EVENT_TYPES = [
        ('CONCERT', 'Concert'),
        ('CONFERENCE', 'Conference'),
        ('EXHIBITION', 'Exhibition'),
        ('WORKSHOP', 'Workshop'),
        ('SEMINAR', 'Seminar'),
        ('PARTY', 'Party'),
        ('EVENT', 'Event'),
    ]
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField()
    city = models.CharField(max_length=300)
    place = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=EVENT_TYPES, default='EVENT')
    attendees = models.ManyToManyField('UserProfile', related_name='favorite_events', blank=True)
    awaiting_invite = models.ManyToManyField('UserProfile', related_name='events_awaiting_invite', blank=True)
    price_low = models.FloatField(blank=True, null=True)
    price_high = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.title


class Chat(models.Model):
    event = models.ForeignKey(Event, related_name='chats', on_delete=models.CASCADE)
    user1 = models.ForeignKey(UserProfile, related_name='chats_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(UserProfile, related_name='chats_as_user2', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('event', 'user1', 'user2')


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(UserProfile, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender} to {self.chat.user1 if self.sender != self.chat.user1 else self.chat.user2}'


class UserFavourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    favourite_event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'favourite_event')
