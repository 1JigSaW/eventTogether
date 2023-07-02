from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

from app.models import Event, UserFavourite, Interest, Language, UserProfile


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This email is already in use.")]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

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
        fields = ['user', 'first_name', 'last_name', 'age', 'language', 'interests', 'description']


