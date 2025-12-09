from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission , IsAuthenticated
from rest_framework.authentication import TokenAuthentication 
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFilter, CharFilter, NumberFilter
from .serializers import UserSerializer , EventSerializer , PhotoSerializer , commentSerializer, likedPhotoSerializer, downloadedPhotoSerializer, viewedPhotoSerializer
import hashlib
from rest_framework.pagination import LimitOffsetPagination # Or PageNumberPagination   
from users.models import users
from photos.models import Photo 
from photos.models import likedPhoto , comment , downloadedPhoto , viewedPhoto
from events.models import Events

# Use your actual users model
User = get_user_model()

class CreateOnlyPermission(BasePermission):
    """
    Allow POST for create and allow the 'login' action without auth.
    Require authentication for all other methods/actions.
    """
    def has_permission(self, request, view):
        # allow create (POST to /users/) without auth
        if request.method == 'POST' and view.action in [None, 'create']:
            return True

        # allow login endpoint without auth
        if view.action == 'login':
            return True

        # otherwise require authenticated user
        return bool(request.user and request.user.is_authenticated)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Use DRF TokenAuthentication
    authentication_classes = [TokenAuthentication]
    permission_classes = [CreateOnlyPermission]

    lookup_field = 'userid'

    pagination_class = LimitOffsetPagination
    page_size = 10
    

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'dept', 'userbio', 'enrollmentNo']
    filterset_fields = ['dept', 'batch', 'is_active']
    ordering_fields = ['username', 'date_joined', 'batch']
    ordering = ['username']

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'username and password required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize username: strigitp whitespace and use case-insensitive lookup
        username_norm = username.strip()
        try:
            user = users.objects.get(username__iexact=username_norm)
        except users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Use Django's built-in password checking
        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Use DRF Token model
        token_obj, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token_obj.key,
            'user': UserSerializer(user, context={'request': request}).data
        })
    

class EventViewSet(viewsets.ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # keep or change as needed

    pagination_class = LimitOffsetPagination
    page_size = 10

    lookup_field = "eventid"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["eventname", "eventlocation", "eventdesc"]
    filterset_fields = ["eventdate", "eventCreator", "eventlocation", "eventtime"]
    ordering_fields = ["eventname", "eventdate", "eventtime", "eventlocation"]
    ordering = ["eventdate", "eventname", "eventtime", "eventlocation"]  

      
    

class PhotoFilter(FilterSet):
    # filter by uploader user id: ?uploader=3
    uploader = NumberFilter(field_name="uploadedBy__id", lookup_expr="exact")
    # single tag: ?tag=fun
    tag = CharFilter(method="filter_by_tag")
    # exact date (date portion of uploadDate): ?date=2025-12-01
    date = DateFilter(field_name="uploadDate", lookup_expr="date")
    # range: ?date_after=YYYY-MM-DD & ?date_before=YYYY-MM-DD
    date_after = DateFilter(field_name="uploadDate", lookup_expr="date__gte")
    date_before = DateFilter(field_name="uploadDate", lookup_expr="date__lte")

    class Meta:
        model = Photo
        fields = []  # custom filters only

    def filter_by_tag(self, queryset, name, value):
        # Assumes extractedTags is a JSONField storing a list of strings.
        # PostgreSQL: list contains exact value
        # Django will translate extractedTags__contains=[value] to JSON containment
        return queryset.filter(extractedTags__contains=[value])

class PhotoViewSet(viewsets.ModelViewSet):
    """
    Photo viewset with combined filtering:
      - uploader (user id)
      - tag (single tag)
      - date / date_after / date_before
    Example: /api/photos/?uploader=3&tag=fun&date_after=2025-11-01
    """
    queryset = Photo.objects.all().select_related('event', 'uploadedBy')
    serializer_class = PhotoSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PhotoFilter

    pagination_class = LimitOffsetPagination
    page_size = 10

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # keep or change as needed

    search_fields = ["photoDesc", "event__eventname", "uploadedBy__username"]
    ordering_fields = ["uploadDate", "photoid"]
    ordering = ["-uploadDate"]



# -------- Like viewset --------
class LikedPhotoViewSet(viewsets.ModelViewSet):
    queryset = likedPhoto.objects.all().select_related('user', 'photo')
    serializer_class = likedPhotoSerializer
    pagination_class = LimitOffsetPagination
    page_size = 10
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'photo']
    search_fields = ['user__username', 'photo__photoDesc']
    ordering_fields = ['likedAt', 'id']
    ordering = ['-likedAt']   # default: newest first
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # keep or change as needed

# -------- Comment viewset --------
class CommentViewSet(viewsets.ModelViewSet):
    queryset = comment.objects.all().select_related('user', 'photo')
    serializer_class = commentSerializer
    filterset_fields = ['user', 'photo']
    pagination_class = LimitOffsetPagination
    page_size = 10
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['commentText', 'user__username', 'photo__photoDesc']
    ordering_fields = ['commentedAt', 'id']
    ordering = ['-commentedAt']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # keep or change as needed

# -------- Download viewset --------
class DownloadedPhotoViewSet(viewsets.ModelViewSet):
    queryset = downloadedPhoto.objects.all().select_related('user', 'photo')
    serializer_class = downloadedPhotoSerializer
    pagination_class = LimitOffsetPagination
    page_size = 10
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'photo', 'version']
    search_fields = ['user__username', 'photo__photoDesc', 'version']
    ordering_fields = ['downloadedAt', 'id']
    ordering = ['-downloadedAt']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # keep or change as needed

# -------- View viewset --------
class ViewedPhotoViewSet(viewsets.ModelViewSet):
    queryset = viewedPhoto.objects.all().select_related('user', 'photo')
    serializer_class = viewedPhotoSerializer
    pagination_class = LimitOffsetPagination
    page_size = 10
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'photo']
    search_fields = ['user__username', 'photo__photoDesc']
    ordering_fields = ['viewedAt', 'id']
    ordering = ['-viewedAt']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # keep or change as needed
