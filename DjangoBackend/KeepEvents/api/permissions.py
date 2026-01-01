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


class IsIMGMember(BasePermission):
    def has_permission(self, request, view):
        return is_img_member(request.user)
    

class CanViewEvent(BasePermission):
    def has_object_permission(self, request, view, obj):
        
        # ... rest of your logic
        if request.user == obj.eventCreator:
            return True
        if obj.visibility == "public":
            return True
        if obj.visibility == "img" and is_img_member(request.user):
            return True
        if obj.visibility == "admin" and is_admin(request.user):
            return True
        return request.user.has_perm("events.view_event_obj", obj)

class CanEditEvent(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.eventCreator:
            return True
        if obj.visibility == "admin" and is_admin(request.user):
            return True
        if obj.visibility == "img" and is_admin(request.user):
            return True
        return request.user.has_perm("change_event_obj", obj)

class CanSendInvitation(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.eventCreator:
            return True
        
        if obj.visibility == "admin"  and is_admin(request.user):
            return True
        
        if obj.visibility == "img" and is_admin(request.user):
            return True
        return request.user.has_perm("invite_event_obj", obj)

class CanDeleteEvent(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.visibility == "admin" and is_admin(request.user):
            return True
        if obj.visibility == "img" and is_admin(request.user):
            return True
        return request.user.has_perm("delete_event_obj", obj)
    
    

#for photos

class canViewPhoto(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.user == obj.uploadedBy:
            return True
        if obj.event.visibility == "public":
            return True
        if obj.event.visibility == "img" and is_img_member(request.user):
            return True
        if obj.event.visibility == "admin" and is_admin(request.user):
            return True
        return request.user.has_perm("events.view_photo_only", obj.event)
    
class canEditPhoto(BasePermission):
    def has_object_permission(self, request, view, obj):
        if  request.user == obj.uploadedBy:
            return True
        if obj.event.visibility == "admin" and is_admin(request.user):
            return True
        if obj.event.visibility == "img" and is_admin(request.user):
            return True
        return request.user.has_perm("events.change_photo_obj", obj)

class canDeletePhoto(BasePermission):
    def has_object_permission(self, request, view, obj):
        if  request.user == obj.uploadedBy:
            return True
        if obj.event.visibility == "admin" and is_admin(request.user):
            return True
        if obj.event.visibility == "img" and is_admin(request.user):
            return True
        return request.user.has_perm("events.delete_photo_obj", obj)
    
class canAddPhoto(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.event.visibility == "admin" and is_admin(request.user):
            return True
        if obj.event.visibility == "img" and is_admin(request.user):
            return True
        if obj.event.visibility == "img" and is_img_member(request.user):
            return True
        return request.user.has_perm("events.change_event_obj", obj.event)