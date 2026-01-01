from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet , EventViewSet , PhotoViewSet , ViewedPhotoViewSet , logout ,AcceptInviteView
from .views import UserGroupViewSet, LikedPhotoViewSet , CommentViewSet , DownloadedPhotoViewSet 
from .views_otp import request_email_otp, verify_email_otp
from .views_otp import me
from .views import my_activity_summary  






router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r"user-groups", UserGroupViewSet, basename="user-groups")

router.register(r'events', EventViewSet, basename='event')
router.register(r'photos', PhotoViewSet, basename='photo')
router.register(r'likes', LikedPhotoViewSet, basename='likedphoto')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'downloads', DownloadedPhotoViewSet, basename='downloadedphoto')
router.register(r'views', ViewedPhotoViewSet, basename='viewedphoto')

urlpatterns = [
    path("", include(router.urls)),
    path("auth/request-otp/", request_email_otp),
    path("auth/verify-otp/", verify_email_otp),
    path("me/", me),
    path("logout/", logout),
     path("auth/me/", me),
    path("users/me/activity-summary/", my_activity_summary),
    path("invite/<uuid:token>/accept/", AcceptInviteView.as_view()),
]
    