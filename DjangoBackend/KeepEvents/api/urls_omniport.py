from django.urls import path
from .views_omniport import omniport_login, omniport_callback

urlpatterns = [
    path("login/", omniport_login),
    path("callback/", omniport_callback),
]
