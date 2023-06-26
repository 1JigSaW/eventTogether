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
from .views import UserRegisterView, UserAuthView, EventViewSet, GetUserFavouritesView, AddUserFavouriteView

urlpatterns = [
    path('register/', UserRegisterView.as_view()),
    path('auth/', UserAuthView.as_view()),
    path('events/', EventViewSet.as_view({'get': 'list'})),
    path('favourites/', GetUserFavouritesView.as_view()),
    path('favourites/add/', AddUserFavouriteView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
