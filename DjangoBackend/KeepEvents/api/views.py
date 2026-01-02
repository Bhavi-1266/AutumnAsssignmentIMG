from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission , IsAuthenticated , AllowAny
from .permissions import IsAdmin , ReadOnly , IsSelfOrAdmin , IsEventOwnerOrAdmin , IsPhotoOwnerEventOwnerOrAdmin  , IsIMGMember
from .permissions import is_admin , is_img_member
from django.contrib.auth import get_user_model 
from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFilter, CharFilter, NumberFilter
from .serializers import UserSerializer , EventSerializer , PhotoSerializer , commentSerializer, likedPhotoSerializer
from .serializers import RegisterSerializer , downloadedPhotoSerializer, viewedPhotoSerializer

import hashlib

from rest_framework_simplejwt.tokens import RefreshToken

from guardian.shortcuts import get_objects_for_user
from .utils import set_event_perms

from django.db.models import Q


from rest_framework.pagination import LimitOffsetPagination # Or PageNumberPagination   
from users.models import users
from photos.models import Photo 
from photos.models import likedPhoto , comment , downloadedPhoto , viewedPhoto
from events.models import Events

# Use your actual users model
User = get_user_model()

from rest_framework.permissions import BasePermission

class CreateOnlyPermission(BasePermission):
    """
    Allow:
    - POST /users/ (registration)
    - POST /users/login/ (login)

    Require authentication for everything else.
    """

    def has_permission(self, request, view):
        # Allow unauthenticated create
        if request.method == "POST" and getattr(view, "action", None) == "create":
            return True

        # Allow unauthenticated login
        if getattr(view, "action", None) == "login":
            return True

        # Otherwise require auth
        return bool(request.user and request.user.is_authenticated)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    
    permission_classes = [CreateOnlyPermission]

    lookup_field = "userid"

    pagination_class = LimitOffsetPagination
    page_size = 10

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "dept", "userbio", "enrollmentNo"]
    filterset_fields = ["dept", "batch", "is_active"]
    ordering_fields = ["username", "date_joined", "batch"]
    ordering = ["username"]


    def get_serializer_class(self):
        if self.action == "create":
            return RegisterSerializer
        return UserSerializer

    def perform_create(self, serializer):
        # Save the user first (all validations, constraints still apply)
        user = serializer.save()
        
        # Automatically add to Public group
        public_group, created = Group.objects.get_or_create(name='Public')
        user.groups.add(public_group)

    @action(detail=False, methods=["post"] , authentication_classes=[] )
    def login(self, request):   
        # 1) Get email + password
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "email and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2) Normalize email
        email_norm = email.strip().lower()

        # 3) Find user
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

        # 5) Check email verification
        if not user.is_active:
            return Response(
                {"error": "Email not verified"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 6) Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # 7) Prepare response (NO TOKEN IN BODY)
        response = Response(
            {
                "user": UserSerializer(user, context={"request": request}).data
            },
            status=status.HTTP_200_OK,
        )

        # 8) Set HTTP-only cookies
        response.set_cookie(
            key="access",
            value=access_token,
            httponly=True,
            secure=False,      # 🔴 True in production (HTTPS)
            samesite="Lax",
            max_age=60 * 60 ,   #  15 hours
        )

        response.set_cookie(
            key="refresh",
            value=str(refresh),
            httponly=True,
            secure=False,      # 🔴 True in production
            samesite="Lax",
            max_age=7 * 24 * 60 ,  # 7 days
        )

        return response

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [ReadOnly()]
        return [IsSelfOrAdmin()]
    

from rest_framework.decorators import api_view, permission_classes

@api_view(["POST"])
@permission_classes([AllowAny()])
def logout(request):
    response = Response(
        {"detail": "Logged out successfully"},
        status=status.HTTP_200_OK,
    )

    # Delete access token cookie
    response.delete_cookie(
        key="access",
        path="/",
    )

    # Delete refresh token cookie
    response.delete_cookie(
        key="refresh",
        path="/",
    )

    return response

from .serializers import UserGroupSerializer

class UserGroupViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserGroupSerializer
    
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = "userid"  # or "id" if your pk is id



from  .utils import CreateEventPerms
from .permissions import  CanSendInvitation , CanEditEvent , CanViewEvent
from events.models import EventInvite
from KeepEvents.settings import FRONTEND_URL
from guardian.shortcuts import get_users_with_perms , get_objects_for_user , remove_perm
from django.shortcuts import get_object_or_404
from guardian.models import UserObjectPermission

from django.db.models import IntegerField
from django.db.models.functions import Cast

class EventViewSet(viewsets.ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventSerializer
    
    pagination_class = LimitOffsetPagination
    page_size = 10
    lookup_field = "eventid"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["eventname", "eventlocation", "eventdesc" , "eventlocation"]
    filterset_fields = {
          "eventdate": ["exact", "gte", "lte", "range"],
        "eventCreator": ["exact"],
        "eventlocation": ["exact", "in"],
        "eventtime": ["exact"],
        "visibility": ["exact"],
    }

    ordering_fields = ["eventname", "eventdate", "eventtime", "eventlocation"]
    ordering = ["eventdate", "eventname", "eventtime", "eventlocation"]




    def get_queryset(self):
        user = self.request.user

        return get_objects_for_user(
            user=user,
            perms="events.view_event_obj",
            klass=Events,
            with_superuser=True,
        )
    
    @action(detail=True, methods=['get'] , permission_classes=[CanEditEvent(), IsAuthenticated()])
    def viewers(self, request, eventid=None):
        """Get users with view_event permission on this event"""
        event = self.get_object()
        viewers = get_users_with_perms(event, only_with_perms_in=['view_event_obj'])
        serializer = UserSerializer(viewers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'] , permission_classes=[CanEditEvent(), IsAuthenticated()])
    def editors(self, request, eventid=None):
        """Get users with edit_event permission on this event"""
        event = self.get_object()
        editors = get_users_with_perms(event, only_with_perms_in=['change_event_obj'])
        serializer = UserSerializer(editors, many=True)
        return Response(serializer.data)
    # views.py - Fix your remove actions:
    @action(detail=True, methods=['delete'] , permission_classes=[CanEditEvent(), IsAuthenticated()])
    def remove_viewer(self, request, eventid=None ):
        event = self.get_object()
        userid = request.query_params.get('userid')  # ✅ From query params
        user = get_object_or_404(get_user_model(), userid=userid)
        remove_perm('view_event_obj', user, event)
        return Response({"message": "Viewer removed"})

    @action(detail=True, methods=['delete'] , permission_classes=[CanEditEvent(), IsAuthenticated()]) 
    def remove_editor(self, request, eventid=None):
        event = self.get_object()
        userid = request.query_params.get('userid')
        user = get_object_or_404(get_user_model(), userid=userid)
        remove_perm('change_event_obj', user, event)
        return Response({"message": "Editor removed"})

    
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated(), CanSendInvitation()],
    )
    def invite(self, request, eventid=None):
        
        event = self.get_object()

        role = request.data.get("role")
        expires_at = request.data.get("expires_at")

        if role not in ["viewer", "editor"]:
            return Response({"error": "Invalid role"}, status=400)

        invite = EventInvite.objects.create(
            event=event,
            role=role,
            expires_at=expires_at,
        )

        invite_url = f"{FRONTEND_URL}/invite/{invite.token}"

        return Response({
            "invite_url": invite_url,
            "role": role,
        })
    

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [CanViewEvent(),IsAuthenticated() ]
        if self.action == "create":
            # only Admin or IMG Member may create events
            return [IsAuthenticated() ]
        # update/delete: owner or admin
        if self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), CanEditEvent()]
        # delete: owner or admin
        if self.action == "destroy":
            return [IsAuthenticated(), CanEditEvent()]  
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        visibility = serializer.validated_data.get("visibility", "private")
        event = serializer.save(eventCreator=user)
        CreateEventPerms(event, visibility, user)

    def perform_update(self, serializer):
        visibility = self.request.data.get("visibility", None)
        event = serializer.save()
        if visibility is not None:  
            extra_users = self.request.data.get("extra_users", [])
            set_event_perms(event, visibility, extra_user_ids=extra_users)


from rest_framework.views import APIView
from .utils import accept_invite
class AcceptInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, token):
        return accept_invite(request, token)

    

class PhotoFilter(FilterSet):
    # unified search (text + tags + location)
    search = CharFilter(method="filter_search")

    uploader = NumberFilter(field_name="uploadedBy__id", lookup_expr="exact")
    tag = CharFilter(method="filter_by_tag")
    date = DateFilter(field_name="uploadDate", lookup_expr="date")
    date_after = DateFilter(field_name="uploadDate", lookup_expr="date__gte")
    date_before = DateFilter(field_name="uploadDate", lookup_expr="date__lte")
    event = NumberFilter(field_name="event_id")

    class Meta:
        model = Photo
        fields = [
            "search",
            "uploader",
            "tag",
            "date",
            "date_after",
            "date_before",
            "event",
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(photoDesc__icontains=value) |
            Q(event__eventname__icontains=value) |
            Q(event__eventlocation__icontains=value) |
            Q(uploadedBy__username__icontains=value) |
            Q(extractedTags__contains=[value])
        )

    def filter_by_tag(self, queryset, name, value):
        return queryset.filter(extractedTags__contains=[value])



from .permissions import canViewPhoto , canEditPhoto , canDeletePhoto , canAddPhoto
class PhotoViewSet(viewsets.ModelViewSet):
    """
    Photo viewset with:
      - filtering (search, uploader, tag, date range, event)
      - ordering
      - single create/update/delete
      - bulk-create
      - bulk-delete
      - like / unlike
    """

    queryset = Photo.objects.all().select_related("event", "uploadedBy")
    serializer_class = PhotoSerializer

    # Filtering & ordering
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_class = PhotoFilter

    ordering_fields = ["uploadDate", "photoid"]
    ordering = ["-uploadDate"]

    pagination_class = LimitOffsetPagination
    page_size = 10

    permission_classes = [IsAuthenticated]

    # 🔑 IMPORTANT: pass request to serializer (for isLikedByCurrentUser)
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
    
    def get_queryset(self):
        user = self.request.user

        # 1. Get events user can view
        allowed_events = get_objects_for_user(
            user,
            "events.view_event_obj",
            Events,
        )

        # 2. Return only photos belonging to those events
        return Photo.objects.filter(event__in=allowed_events)


    # Permissions per action
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated() , canViewPhoto() ]

        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), canEditPhoto()]

        if self.action in ["bulk_create", "bulk_delete", "toggle_like"]:
            return [IsAuthenticated()]

        return super().get_permissions()

    # Single create
    def perform_create(self, serializer):
        permission_classes = [IsAuthenticated , canAddPhoto]
        serializer.save(uploadedBy=self.request.user)

    # -------------------------
    # BULK CREATE
    # -------------------------
    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        permission_classes = [IsAuthenticated , canAddPhoto ]
        files = request.FILES.getlist("photoFile")
        descs = request.data.getlist("photoDesc")
        event_ids = request.data.getlist("event_id")
        tags = request.data.getlist("extractedTags")

        if not files:
            return Response(
                {"error": "No files received"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []
        errors = []

        import json

        for i, file in enumerate(files):
            extractedTags = json.loads(tags[i]) if i < len(tags) else []

            data = {
                "photoFile": file,
                "photoDesc": descs[i] if i < len(descs) else "",
                "event_id": event_ids[i] if i < len(event_ids) else None,  # ✅ FIX
                "extractedTags": extractedTags,
            }

            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save(uploadedBy=request.user)  # ✅ FIX
                created.append(serializer.data)
            else:
                errors.append({"index": i, "errors": serializer.errors})

        return Response(
            {"created": created, "errors": errors},
            status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED
        )

    # -------------------------
    # BULK DELETE
    # -------------------------
    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        ids = request.data.get("photo_ids", [])

        if not isinstance(ids, list):
            return Response(
                {"error": "photo_ids must be a list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        photos = Photo.objects.filter(pk__in=ids).select_related("event", "uploadedBy")
        deleted = []
        skipped = []

        perm_checker = canDeletePhoto()

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

    # -------------------------
    # LIKE / UNLIKE
    # -------------------------
    @action(detail=True, methods=["post"], url_path="toggle-like")
    def toggle_like(self, request, pk=None):
        photo = self.get_object()
        user = request.user

        like = likedPhoto.objects.filter(photo=photo, user=user).first()

        if like:
            like.delete()
            photo.likecount = max(photo.likecount - 1, 0)
            liked = False
        else:
            likedPhoto.objects.create(photo=photo, user=user)
            photo.likecount += 1
            liked = True

        photo.save(update_fields=["likecount"])

        return Response(
            {"liked": liked, "likes": photo.likecount},
            status=status.HTTP_200_OK,
        )




from django.db.models import Sum, Count, Min
from collections import Counter

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_activity_summary(request):
    user = request.user
    photos = Photo.objects.filter(uploadedBy=user).select_related("event")

    # ---- BASIC STATS ----
    stats = photos.aggregate(
        total_photos=Count("photoid"),
        total_likes=Sum("likecount"),
        total_views=Sum("viewcount"),
        total_downloads=Sum("downloadcount"),
        total_comments=Sum("commentcount"),
        first_upload_date=Min("uploadDate"),
    )

    # ---- TOP TAGS ----
    tag_counter = Counter()
    for p in photos:
        if p.extractedTags:
            tag_counter.update(p.extractedTags)

    top_tags = [
        {"tag": tag, "count": count}
        for tag, count in tag_counter.most_common(10)
    ]

    # ---- TOP LOCATIONS (via events) ----
    location_counter = Counter()
    for p in photos:
        if p.event and p.event.eventlocation:
            location_counter[p.event.eventlocation] += 1

    top_locations = [
        {"location": loc, "count": count}
        for loc, count in location_counter.most_common(5)
    ]

    # ---- MAJOR EVENTS ----
    major_events = (
        photos.values("event__eventid", "event__eventname")
        .annotate(photo_count=Count("photoid"))
        .order_by("-photo_count")[:5]
    )

    return Response({
        "user": {
            "username": user.username,
            "email": user.email,
        },
        "stats": stats,
        "activity": {
            "top_tags": top_tags,
            "top_locations": top_locations,
            "major_events": list(major_events),
        },
    })




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
    
    permission_classes = [IsAuthenticated]  # keep or change as needed

# -------- Comment viewset --------
from django.core.exceptions import ValidationError
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
    
    permission_classes = [IsAuthenticated]  # keep or change as needed
    def perform_create(self, serializer):
        photo_id = self.request.data.get('photo_id')
        if not photo_id:  # Only raise if photo is actually missing
            raise ValidationError({"photo": "This field is required."})
        
        # Continue with save
        serializer.save(user=self.request.user)




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
    
    permission_classes = [IsAuthenticated]  # keep or change as needed
