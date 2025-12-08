from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission , IsAuthenticated
from rest_framework.authentication import TokenAuthentication 
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import UserSerializer , EventSerializer
import hashlib
from users.models import users
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
    """
    ===============================================================================
                                 USERS API
===============================================================================
BASE URL (example):
    /api/users/

AUTHENTICATION:
    TokenAuthentication (DRF). Most endpoints require a token in the header:
    Authorization: Token <token>

VIEWSET BEHAVIOR SUMMARY:
    - ViewSet: ModelViewSet for User model (queryset = User.objects.all())
    - serializer_class: UserSerializer
    - authentication: TokenAuthentication
    - permission_classes: CreateOnlyPermission  # (custom) see notes below
    - lookup_field: 'userid'  -> detail endpoints use /api/users/<userid>/
    - Supports filtering, searching and ordering:
        * search_fields: username, email, dept, userbio, enrollmentNo
        * filterset_fields: dept, batch, is_active
        * ordering_fields: username, date_joined, batch
        * default ordering: ['username']

COMMON ENDPOINTS
-------------------------------------------------------------------------------
1) LIST USERS
    GET /api/users/
    Requires permission per CreateOnlyPermission (check that class).
    Supports ?search=, ?filter, ?ordering=

EXAMPLE:
    GET /api/users/?search=bhavy&ordering=-date_joined

SUCCESS (200):
    [
      { "userid": 1, "username": "alice", "email": "a@x.com", ... },
      ...
    ]

-------------------------------------------------------------------------------
2) RETRIEVE USER
    GET /api/users/<userid>/

EXAMPLE:
    GET /api/users/12/

SUCCESS (200):
    {
      "userid": 12,
      "username": "bob",
      "email": "bob@example.com",
      ...
    }

-------------------------------------------------------------------------------
3) CREATE USER
    POST /api/users/
    Content-Type: application/json (or multipart/form-data if uploading avatar)
    Body fields depend on your UserSerializer (username, password, email, ...)

EXAMPLE:
    POST /api/users/
    {
      "username": "newuser",
      "password": "s3cret",
      "email": "new@example.com",
      "dept": "CS",
      "batch": 2026
    }

SUCCESS (201): created user JSON (password not returned)

-------------------------------------------------------------------------------
4) UPDATE (PUT) / PARTIAL UPDATE (PATCH)
    PUT  /api/users/<userid>/
    PATCH /api/users/<userid>/

Note: permission class controls who can update. Confirm CreateOnlyPermission behaviour.

-------------------------------------------------------------------------------
5) DELETE
    DELETE /api/users/<userid>/
    (Check CreateOnlyPermission for delete rules)

-------------------------------------------------------------------------------
6) LOGIN ACTION (custom route)
    POST /api/users/login/

DESCRIPTION:
    Custom action defined with @action(detail=False, methods=['post']).
    Accepts username and password, returns DRF token and serialized user on success.

REQUEST:
    POST /api/users/login/
    Content-Type: application/json

    {
      "username": "alice",
      "password": "hunter2"
    }

BEHAVIOR:
    - Strips username whitespace and uses case-insensitive lookup:
        users.objects.get(username__iexact=username_norm)
      (This looks up in your custom users model; ensure get_user_model() usage)
    - Checks password with user.check_password(password)
    - Creates or retrieves a Token: Token.objects.get_or_create(user=user)
    - Returns: token and serialized user

SUCCESS (200):
    {
      "token": "0123456789abcdef...",
      "user": { "userid": 3, "username": "alice", "email": "alice@x.com", ... }
    }

ERRORS:
    - 400 Bad Request : if username or password missing
      { "error": "username and password required" }

    - 404 Not Found : if user not found
      { "error": "User not found" }

    - 401 Unauthorized : if password invalid
      { "error": "Invalid credentials" }

CURL EXAMPLE:
    curl -X POST http://localhost:8000/api/users/login/ \
      -H "Content-Type: application/json" \
      -d '{"username":"alice","password":"s3cret"}'

SECURITY NOTES:
    - Always call this endpoint over HTTPS in production.
    - Consider rate-limiting login attempts (throttling) to prevent brute force.
    - Using Django's built-in `authenticate()` is generally safer than manual lookup:
        user = authenticate(request, username=username_norm, password=password)
      because it respects authentication backends and account status.
    - Token creation here is idempotent: get_or_create ensures single token per user.
      If you want tokens to rotate on login, delete existing token and create a new one.
    - Avoid returning any sensitive fields in the serialized user data (do not return password).
    - Consider expiring tokens or using JWT if you need time-limited tokens.

PERMISSION CLASS NOTE:
    - `CreateOnlyPermission` is custom — confirm its semantics:
        * If it permits only create operations to unauthenticated users, it may
          block listing/retrieving by non-admins. If you want public read-only
          access, use `IsAuthenticatedOrReadOnly` or a custom policy.
    - Ensure login action is accessible without prior authentication (i.e., allow any),
      otherwise clients cannot obtain a token. If `permission_classes` at class level
      prevents anonymous POST to /login/, decorate the action with
        @action(detail=False, methods=['post'], permission_classes=[AllowAny])
      so users can login.

EXAMPLE tweak to allow anonymous login:
    from rest_framework.permissions import AllowAny
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(...): ...

===============================================================================

    """


class EventViewSet(viewsets.ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # keep or change as needed

    lookup_field = "eventid"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["eventname", "eventlocation", "eventdesc"]
    filterset_fields = ["eventdate", "eventCreator", "eventlocation", "eventtime"]
    ordering_fields = ["eventname", "eventdate", "eventtime", "eventlocation"]
    ordering = ["eventdate", "eventname", "eventtime", "eventlocation"]  

      
    """
    =====================================================================
                            EVENTS API GUIDE
    =====================================================================

    BASE URL:
        /api/events/

    AUTHENTICATION:
        Token Authentication (send in header)
        Header: Authorization: Token <your_token_here>

    PRIMARY KEY / LOOKUP FIELD:
        eventid (integer)

    =====================================================================
    1. LIST EVENTS
    =====================================================================

    GET /api/events/

    DESCRIPTION:
        Returns a list of all events. Supports:
            - Searching
            - Filtering
            - Ordering

    EXAMPLE REQUEST:
        GET /api/events/?search=tech
        GET /api/events/?eventlocation=Auditorium
        GET /api/events/?ordering=eventdate

    SUCCESS RESPONSE (200):
    [
        {
            "eventid": 1,
            "eventname": "Tech Fest",
            "eventdesc": "...",
            "eventdate": "2025-01-07",
            "eventtime": "12:00:00",
            "eventlocation": "Hall A",
            "eventCreator": 3,
            "eventCoverPhoto": "event_covers/banner.jpg",
            "eventCoverPhoto_url": "http://localhost:8000/media/event_covers/banner.jpg"
        },
        ...
    ]

    =====================================================================
    2. RETRIEVE A SINGLE EVENT
    =====================================================================

    GET /api/events/<eventid>/

    EXAMPLE:
    GET /api/events/5/

    SUCCESS RESPONSE (200):
    {
        "eventid": 5,
        "eventname": "Freshers Party",
        "eventdesc": "Welcome...",
        "eventdate": "2025-03-12",
        "eventtime": "18:00:00",
        "eventlocation": "Main Hall",
        "eventCreator": 7,
        "eventCoverPhoto": "",
        "eventCoverPhoto_url": null
    }

    =====================================================================
    3. CREATE EVENT
    =====================================================================

    POST /api/events/

    CONTENT TYPE:
        multipart/form-data  (required if sending images)

    REQUEST BODY:
    {
        "eventname": "Hackathon 2025",
        "eventdesc": "Come build cool projects!",
        "eventdate": "2025-10-12",
        "eventtime": "09:00:00",
        "eventlocation": "Auditorium",
        "eventCreator": 3,                     <-- Optional (creator id)
        "eventCoverPhoto": <upload file>       <-- Optional
    }

    CURL EXAMPLE:
    curl -X POST http://localhost:8000/api/events/ \
    -H "Authorization: Token YOUR_TOKEN" \
    -F "eventname=Hackathon" \
    -F "eventdesc=Big coding event" \
    -F "eventdate=2025-10-10" \
    -F "eventtime=10:00:00" \
    -F "eventlocation=Hall C" \
    -F "eventCreator=2" \
    -F "eventCoverPhoto=@/path/to/image.jpg"

    SUCCESS RESPONSE (201):
    {
        "eventid": 12,
        "eventname": "Hackathon",
        "eventCreator": 2,
        "eventCoverPhoto": "event_covers/image.jpg",
        "eventCoverPhoto_url": "http://localhost:8000/media/event_covers/image.jpg",
        ...
    }

    =====================================================================
    4. UPDATE EVENT (FULL UPDATE)
    =====================================================================

    PUT /api/events/<eventid>/

    CONTENT TYPE:
        multipart/form-data  (required if including image)

    EXAMPLE PUT:
    PUT /api/events/12/
    {
        "eventname": "Updated Hackathon",
        "eventdesc": "Updated description",
        "eventdate": "2025-10-11",
        "eventtime": "11:00:00",
        "eventlocation": "New Hall",
        "eventCreator": 4,
        "eventCoverPhoto": <new file> (optional)
    }

    =====================================================================
    5. PARTIAL UPDATE (PATCH)
    =====================================================================

    PATCH /api/events/<eventid>/

    EXAMPLE PATCH:
    PATCH /api/events/12/
    {
        "eventname": "New Name Only"
    }

    EXAMPLE PATCH TO CHANGE CREATOR:
    PATCH /api/events/12/
    {
        "eventCreator": 7
    }

    =====================================================================
    6. DELETE EVENT
    =====================================================================

    DELETE /api/events/<eventid>/

    EXAMPLE:
    DELETE /api/events/12/

    SUCCESS RESPONSE:
    204 No Content

    =====================================================================
    7. SEARCHING EVENTS
    =====================================================================

    You can search through:
        - eventname
        - eventlocation
        - eventdesc

    EXAMPLE:
    GET /api/events/?search=tech
    GET /api/events/?search=auditorium

    =====================================================================
    8. FILTERING EVENTS
    =====================================================================

    Filter by:
        - eventdate
        - eventCreator (user id)
        - eventlocation
        - eventtime

    EXAMPLES:
    GET /api/events/?eventdate=2025-04-20
    GET /api/events/?eventCreator=3
    GET /api/events/?eventlocation=Auditorium

    =====================================================================
    9. ORDERING EVENTS
    =====================================================================

    Order by:
        - eventname
        - eventdate
        - eventtime
        - eventlocation

    EXAMPLES:
    GET /api/events/?ordering=eventdate
    GET /api/events/?ordering=-eventname

    =====================================================================
                            END OF EVENTS API
    =====================================================================

    """


