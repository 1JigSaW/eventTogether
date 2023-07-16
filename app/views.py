import base64

from cloudinary.uploader import upload
from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import Q, Count, F
from django.http import Http404, JsonResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from django.utils import timezone

from .models import Event, UserFavourite, Interest, Language, UserProfile, Message, Chat
from .serializers import UserSerializer, EventSerializer, UserFavouriteSerializer, InterestSerializer, \
    LanguageSerializer, UserProfileSerializer, MessageSerializer, WriteMessageSerializer, ChatSerializer


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
    queryset = Event.objects.filter(date__gte=timezone.now()).order_by('date')
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
            user_profile = UserProfile(user_id=user_id)
            serializer = UserProfileSerializer(user_profile, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"user_profile_id": user_profile.id, "data": serializer.data}, status=status.HTTP_200_OK)

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


class AddUserToEventView(APIView):
    def post(self, request, event_id, format=None):
        try:
            event = Event.objects.get(id=event_id)
            user_profile = UserProfile.objects.get(user_id=request.data.get('user_id'))
        except (Event.DoesNotExist, UserProfile.DoesNotExist):
            raise Http404

        # Add the user to the event's awaiting_invite list
        event.awaiting_invite.add(user_profile)
        event.save()

        return Response({"message": "User successfully added to the event's awaiting list"}, status=status.HTTP_200_OK)


class RemoveUserFromEventView(APIView):
    def delete(self, request, event_id, user_id, format=None):
        try:
            event = Event.objects.get(id=event_id)
            user_profile = UserProfile.objects.get(user_id=user_id)

            if user_profile in event.awaiting_invite.all():
                event.awaiting_invite.remove(user_profile)
                event.save()
                return Response({"message": "User removed from event"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "User not found in the event"}, status=status.HTTP_404_NOT_FOUND)

        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class SearchEventView(APIView):
    def get(self, request, format=None):
        search_query = request.query_params.get('query', None)
        print(f"Received search query: {search_query}")

        if search_query is None:
            print("No search query provided")
            return Response({"error": "No search query provided"}, status=status.HTTP_400_BAD_REQUEST)

        matching_events = Event.objects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(place__icontains=search_query)
        )

        if not matching_events:
            print(f"No events found matching the search query: {search_query}")
            return Response({"message": "No events found matching the search query"}, status=status.HTTP_200_OK)

        serializer = EventSerializer(matching_events, many=True)
        print(f"Serialized data: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventProfilesView(APIView):
    def get(self, request, event_id, format=None):
        try:
            event = Event.objects.get(id=event_id)
        except ObjectDoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        profiles = UserProfile.objects.filter(events_awaiting_invite=event)

        # Create a pagination object.
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of items per page.

        # Apply the pagination to the queryset.
        page = paginator.paginate_queryset(profiles, request)

        serializer = UserProfileSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class ChatMessagesView(APIView):
    def get(self, request, chat_id, format=None):
        try:
            messages = Message.objects.filter(chat_id=chat_id).order_by('timestamp')
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Message.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UserChatsView(APIView):
    def get(self, request, user_id, format=None):
        try:
            user = UserProfile.objects.get(id=user_id)
            chats = Chat.objects.filter(Q(user1=user) | Q(user2=user))  # get all chats related to the user

            result = []
            for chat in chats:
                message = Message.objects.filter(chat=chat).latest('timestamp')  # get latest message for the chat
                result.append(message)

            serializer = MessageSerializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class SendMessageView(APIView):
    def post(self, request, format=None):
        serializer = WriteMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateChatView(APIView):
    def post(self, request, format=None):
        print(request.data)
        recipient_id = request.data.get('recipientUserId')
        sender_id = request.data.get('senderUserId')
        event_id = request.data.get('eventId')
        if recipient_id and sender_id and event_id:
            user_profile = UserProfile.objects.get(id=sender_id)
            recipient = UserProfile.objects.get(id=recipient_id)
            event = Event.objects.get(id=event_id)

            # Check if chat already exists for the specific event
            existing_chat = Chat.objects.filter(
                Q(user1=user_profile, user2=recipient, event=event) |
                Q(user1=recipient, user2=user_profile, event=event)
            ).first()

            if existing_chat:
                # If chat already exists, return messages in it
                messages = Message.objects.filter(chat=existing_chat)
                serializer = MessageSerializer(messages, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # If not, create new chat for the event
                new_chat = Chat.objects.create(user1=user_profile, user2=recipient, event=event)
                serializer = ChatSerializer(new_chat)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


class GetChatIDView(APIView):
    def get(self, request, format=None):
        recipient_id = request.GET.get('recipientUserId')
        sender_id = request.GET.get('senderUserId')
        event_id = request.GET.get('eventId')

        try:
            chat = Chat.objects.get(
                Q(user1__id=sender_id, user2__id=recipient_id, event__id=event_id) |
                Q(user1__id=recipient_id, user2__id=sender_id, event__id=event_id)
            )
            print(chat.id)
            return JsonResponse({"chat_id": chat.id})
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Chat not found"}, status=404)


class MatchUserView(APIView):
    def get(self, request, user_id, event_id, *args, **kwargs):
        user = UserProfile.objects.get(id=user_id)
        event = Event.objects.get(id=event_id)

        event_users = UserProfile.objects.filter(events_awaiting_invite=event).exclude(id=user_id)

        matched_users = event_users.annotate(
            language_matches=Count('language', filter=Q(language__in=user.language.all())),
            interest_matches=Count('interests', filter=Q(interests__in=user.interests.all())),
        )

        matched_users = matched_users.annotate(
            total_matches= F('language_matches') + F('interest_matches')
        ).order_by('-total_matches')

        serializer = UserProfileSerializer(matched_users, many=True)
        print(serializer.data)
        return Response(serializer.data)


class UserProfilePictureUpdateView(APIView):

    def put(self, request, *args, **kwargs):
        profile_id = kwargs.get('profile_id')
        try:
            profile = UserProfile.objects.get(user_id=profile_id)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        image_data = base64.b64decode(request.data['picture'])
        image_file = ContentFile(image_data, str(profile.user.id) + '.jpg')

        # Use the Cloudinary upload function to upload the image
        # This function will return a dictionary that includes the URL of the uploaded image
        upload_result = upload(image_file, folder='users')

        # Get the URL from the result and save it to the model
        profile.image = upload_result['url']
        profile.save()

        return Response(status=status.HTTP_200_OK)

