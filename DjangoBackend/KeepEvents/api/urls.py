from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet , EventViewSet , PhotoViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'events', EventViewSet, basename='event')
router.register(r'photos', PhotoViewSet, basename='photo')

urlpatterns = [
    path('', include(router.urls)),
]

