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
from .views import UserRegisterView, UserAuthView

urlpatterns = [
    path('register/', UserRegisterView.as_view()),
    path('login/', UserAuthView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
