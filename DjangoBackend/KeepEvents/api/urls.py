from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet , EventViewSet , PhotoViewSet , LikedPhotoViewSet , CommentViewSet , DownloadedPhotoViewSet , ViewedPhotoViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'events', EventViewSet, basename='event')
router.register(r'photos', PhotoViewSet, basename='photo')
router.register(r'likes', LikedPhotoViewSet, basename='likedphoto')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'downloads', DownloadedPhotoViewSet, basename='downloadedphoto')
router.register(r'views', ViewedPhotoViewSet, basename='viewedphoto')

urlpatterns = [
    path('', include(router.urls)),
]

