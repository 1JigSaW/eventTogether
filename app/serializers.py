from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

from app.models import Event, UserFavourite, Interest, Language, UserProfile, Message, Chat


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This email is already in use.")],
        error_messages={
            'blank': 'Email is required.',
            'invalid': 'Invalid email address.'
        }
    )

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True,
                'error_messages': {
                    'blank': 'Password is required.',
                    'invalid': 'Invalid password.'
                }
            },
            'username': {
                'error_messages': {
                    'blank': 'Username is required.',
                    'invalid': 'Invalid username.'
                }
            }
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class UserFavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavourite
        fields = '__all__'


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    interests = serializers.SlugRelatedField(
        many=True,
        queryset=Interest.objects.all(),
        slug_field='name'
    )
    language = serializers.SlugRelatedField(
        many=True,
        queryset=Language.objects.all(),
        slug_field='name'
    )

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'first_name', 'last_name', 'age', 'language', 'interests', 'description', 'image']


class ChatSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user1 = UserProfileSerializer(read_only=True)
    user2 = UserProfileSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'event', 'user1', 'user2']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)
    chat = ChatSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp', 'sender', 'chat']


class WriteMessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp', 'sender', 'chat']

    def create(self, validated_data):
        sender = validated_data.pop('sender')
        chat = validated_data.pop('chat')
        message = Message.objects.create(sender=sender, chat=chat, **validated_data)
        return message


1
