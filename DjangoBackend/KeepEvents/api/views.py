from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission , IsAuthenticated , AllowAny
from rest_framework.authentication import TokenAuthentication 
from rest_framework.authtoken.models import Token
from .permissions import IsAdmin , ReadOnly , IsSelfOrAdmin , IsEventOwnerOrAdmin , IsPhotoOwnerEventOwnerOrAdmin
from .permissions import is_admin , is_img_member
from django.contrib.auth import get_user_model 
from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFilter, CharFilter, NumberFilter
from .serializers import UserSerializer , EventSerializer , PhotoSerializer , commentSerializer, likedPhotoSerializer, downloadedPhotoSerializer, viewedPhotoSerializer
import hashlib

from guardian.shortcuts import get_objects_for_user
from .utils import set_event_perms


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

    authentication_classes = [TokenAuthentication]
    permission_classes = [CreateOnlyPermission]

    lookup_field = "userid"

    pagination_class = LimitOffsetPagination
    page_size = 10

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "dept", "userbio", "enrollmentNo"]
    filterset_fields = ["dept", "batch", "is_active"]
    ordering_fields = ["username", "date_joined", "batch"]
    ordering = ["username"]


    def perform_create(self, serializer):
        # Save the user first (all validations, constraints still apply)
        user = serializer.save()
        
        # Automatically add to Public group
        public_group, created = Group.objects.get_or_create(name='Public')
        user.groups.add(public_group)

    @action(detail=False, methods=["post"])
    def login(self, request):
        # 1) Get email + password from body
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "email and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2) Normalize email
        email_norm = email.strip().lower()

        # 3) Find user by email
        try:
            user = User.objects.get(email__iexact=email_norm)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 4) Check password
        if not user.check_password(password):
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # 5) Block if email not verified (OTP not done yet)
        if not user.is_active:
            return Response(
                {"error": "Email not verified"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 6) Issue DRF token
        token_obj, _ = Token.objects.get_or_create(user=user)

        # 7) Return token + user info
        return Response(
            {
                "token": token_obj.key,
                "user": UserSerializer(user, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [ReadOnly()]
        return [IsSelfOrAdmin()]


from .serializers import UserGroupSerializer

class UserGroupViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserGroupSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = "userid"  # or "id" if your pk is id




class EventViewSet(viewsets.ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventSerializer
    authentication_classes = [TokenAuthentication]
    pagination_class = LimitOffsetPagination
    page_size = 10
    lookup_field = "eventid"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["eventname", "eventlocation", "eventdesc"]
    filterset_fields = ["eventdate", "eventCreator", "eventlocation", "eventtime"]
    ordering_fields = ["eventname", "eventdate", "eventtime", "eventlocation"]
    ordering = ["eventdate", "eventname", "eventtime", "eventlocation"]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.groups.filter(name="Admin").exists()):
            return Events.objects.all()
        return get_objects_for_user(
            user=user,
            perms="view_event_obj",
            klass=Events,
            any_perm=True,
            with_superuser=True,
        )

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        if self.action == "create":
            # only Admin or IMG Member may create events
            return [IsAuthenticated()]
        # update/delete: owner or admin
        return [IsAuthenticated(), IsEventOwnerOrAdmin()]

    def perform_create(self, serializer):
        user = self.request.user
        if not (is_admin(user) or is_img_member(user)):
            # block non-admin, non-IMG member at runtime
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only Admin or IMG Member can create events.")
        visibility = serializer.validated_data.get("visibility", "public")
        event = serializer.save(eventCreator=user)
        extra_users = self.request.data.get("extra_users", [])
        set_event_perms(event, visibility, extra_user_ids=extra_users)

    def perform_update(self, serializer):
        visibility = self.request.data.get("visibility", None)
        event = serializer.save()
        if visibility is not None:
            extra_users = self.request.data.get("extra_users", [])
            set_event_perms(event, visibility, extra_user_ids=extra_users)

      
    

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
    event = NumberFilter(field_name="event_id")

    class Meta:
        model = Photo
        fields = [ "uploader", "tag", "date", "date_after", "date_before", "event"]  # custom filters only
    def filter_by_tag(self, queryset, name, value):
        # Assumes extractedTags is a JSONField storing a list of strings.
        # PostgreSQL: list contains exact value
        # Django will translate extractedTags__contains=[value] to JSON containment
        return queryset.filter(extractedTags__contains=[value])


class PhotoViewSet(viewsets.ModelViewSet):
    """
    Photo viewset with:
      - filtering (uploader, tag, date range)
      - single create/update/delete
      - bulk-create
      - bulk-delete
    """
    queryset = Photo.objects.all().select_related("event", "uploadedBy")
    serializer_class = PhotoSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PhotoFilter

    pagination_class = LimitOffsetPagination
    page_size = 10

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    search_fields = ["photoDesc", "event__eventname", "uploadedBy__username"]
    ordering_fields = ["uploadDate", "photoid"]
    ordering = ["-uploadDate"]

    def get_permissions(self):
        # Anyone authenticated can view photos
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        # Single create/update/delete require object-level permissions
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsPhotoOwnerEventOwnerOrAdmin()]
        # Bulk actions: use same permission as single create/delete
        if self.action in ["bulk_create", "bulk_delete"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Single create: uploader is always the request user
        serializer.save(uploader=self.request.user)

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        files = request.FILES.getlist("photoFile")
        descs = request.data.getlist("photoDesc")
        events = request.data.getlist("event")
        tags = request.data.getlist("extractedTags")

        if not files:
            return Response(
                {"error": "No files received"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []
        errors = []

        for i, file in enumerate(files):
            data = {
                "photoFile": file,
                "photoDesc": descs[i] if i < len(descs) else "",
                "event": events[i] if i < len(events) else None,
                "extractedTags": tags[i] if i < len(tags) else [],
                "uploader": request.user.pk,
            }

            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
            else:
                errors.append({"index": i, "errors": serializer.errors})

        return Response(
            {"created": created, "errors": errors},
            status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        """
        Delete multiple photos by ID list.
        Body: {"photo_ids": [1, 2, 3]}
        Each photo is deleted only if user passes IsPhotoOwnerEventOwnerOrAdmin.
        """
        ids = request.data.get("photo_ids", [])
        if not isinstance(ids, list):
            return Response({"error": "photo_ids must be a list"}, status=status.HTTP_400_BAD_REQUEST)

        photos = Photo.objects.filter(pk__in=ids).select_related("event", "uploadedBy")
        deleted = []
        skipped = []

        perm_checker = IsPhotoOwnerEventOwnerOrAdmin()

        for photo in photos:
            if perm_checker.has_object_permission(request, self, photo):
                deleted.append(photo.pk)
                photo.delete()
            else:
                skipped.append(photo.pk)

        return Response(
            {"deleted": deleted, "skipped_no_permission": skipped},
            status=status.HTTP_200_OK,
        )



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
