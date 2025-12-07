from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import UserSerializer
import hashlib
from users.models import users

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

