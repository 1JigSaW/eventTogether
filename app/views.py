from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets

from .models import Event, UserFavourite
from .serializers import UserSerializer, EventSerializer, UserFavouriteSerializer


def authenticate(request, email=None, password=None):
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

        user = authenticate(request, email=email, password=password)

        if user is not None:
            return Response({'message': 'Authentication successful'}, status=status.HTTP_200_OK)
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
        serializer = UserFavouriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserFavouritesView(APIView):
    def get(self, request, format=None):
        user = request.user
        favourites = UserFavourite.objects.filter(user=user)
        serializer = UserFavouriteSerializer(favourites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
