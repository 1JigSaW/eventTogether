from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# from .views import UserRegisterView
#
# urlpatterns = [
#     path('api/register', UserRegisterView.as_view()),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# if settings.DEBUG:
#     urlpatterns += staticfiles_urlpatterns()

from django.urls import path
from .views import UserRegisterView, UserAuthView, EventViewSet, GetUserFavouritesView, AddUserFavouriteView, \
    RemoveUserFavouriteView, GetEventView, InterestSearchView, LanguageSearchView, UserProfileUpdateView, \
    UserProfileDetailView, ChangePasswordView

urlpatterns = [
    path('register/', UserRegisterView.as_view()),
    path('auth/', UserAuthView.as_view()),
    path('events/', EventViewSet.as_view({'get': 'list'})),
    path('events/<int:event_id>/', GetEventView.as_view()),
    path('favourites/<int:user_id>/', GetUserFavouritesView.as_view()),
    path('favourites/add/', AddUserFavouriteView.as_view()),
    path('favourites/remove/', RemoveUserFavouriteView.as_view()),
    path('interests/search/', InterestSearchView.as_view()),
    path('languages/search/', LanguageSearchView.as_view()),
    path('userprofile/update/<int:user_id>/', UserProfileUpdateView.as_view()),
    path('userprofile/<int:user_id>/', UserProfileDetailView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
