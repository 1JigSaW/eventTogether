from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions

from .models import Event, UserFavourite, Interest, Language, UserProfile
from .serializers import UserSerializer, EventSerializer, UserFavouriteSerializer, InterestSerializer, \
    LanguageSerializer, UserProfileSerializer


def authenticateAuth(request, email=None, password=None):
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
        if check_password(password, user.password):
            return user
    except User.DoesNotExist:
        return None


class UserRegisterView(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAuthView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticateAuth(request, email=email, password=password)

        if user is not None:
            return Response({'message': 'User authenticated', 'userId': user.id}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Check your password or email'}, status=status.HTTP_401_UNAUTHORIZED)


class TenPerPagePagination(PageNumberPagination):
    page_size = 10


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('date')
    serializer_class = EventSerializer
    pagination_class = TenPerPagePagination


class AddUserFavouriteView(APIView):
    def post(self, request, format=None):
        print(request.data)
        serializer = UserFavouriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveUserFavouriteView(APIView):
    def delete(self, request, format=None):
        user = request.data.get('user')
        favourite_event = request.data.get('favourite_event')

        try:
            favourite = UserFavourite.objects.get(user=user, favourite_event=favourite_event)
            favourite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserFavourite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GetUserFavouritesView(APIView):
    def get(self, request, user_id, format=None):
        user = User.objects.get(pk=user_id)
        favourites = UserFavourite.objects.filter(user=user)
        serializer = UserFavouriteSerializer(favourites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetEventView(APIView):
    def get(self, request, event_id, format=None):
        try:
            event = Event.objects.get(pk=event_id)
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class InterestSearchView(APIView):
    def get(self, request, format=None):
        query = request.GET.get('query', '')
        interests = Interest.objects.filter(name__icontains=query)[:5]  # limiting results to 5
        serializer = InterestSerializer(interests, many=True)
        return Response(serializer.data)


class LanguageSearchView(APIView):
    def get(self, request, format=None):
        query = request.GET.get('query', '')
        languages = Language.objects.filter(name__icontains=query)[:5]  # limiting results to 5
        serializer = LanguageSerializer(languages, many=True)
        return Response(serializer.data)


class UserProfileUpdateView(APIView):
    def put(self, request, user_id, format=None):
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        except UserProfile.DoesNotExist:
            serializer = UserProfileSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetailView(APIView):
    def get(self, request, user_id, format=None):
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)


class ChangePasswordView(APIView):

    def post(self, request, format=None):
        old_password = request.data.get('old_password', None)
        new_password = request.data.get('new_password', None)
        user = request.data.get('user', None)
        user = User.objects.get(id=user)

        if authenticate(username=user.username, password=old_password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Wrong old password"}, status=status.HTTP_400_BAD_REQUEST)
