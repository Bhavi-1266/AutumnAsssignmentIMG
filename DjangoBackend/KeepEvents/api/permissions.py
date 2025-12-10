from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS

User = get_user_model()

def is_admin(user):
    return (
        user
        and user.is_authenticated
        and (user.is_staff or user.groups.filter(name="Admin").exists())
    )

def is_img_member(user):
    return (
        user
        and user.is_authenticated
        and user.groups.filter(name="IMG Member").exists()
    )

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user)

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_admin(user):
            return True
        if isinstance(obj, User):
            return obj == user
        if hasattr(obj, "user"):
            return obj.user == user
        return False

class IsEventOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_admin(user):
            return True
        return getattr(obj, "eventCreator", None) == user

class IsPhotoOwnerEventOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_admin(user):
            return True
        if getattr(obj, "uploader", None) == user:
            return True
        event = getattr(obj, "event", None)
        if event is not None and getattr(event, "eventCreator", None) == user:
            return True
        return False
