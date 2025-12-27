from rest_framework import serializers
from users.models import users
from events.models import Events
from photos.models import Photo , likedPhoto , comment , downloadedPhoto , viewedPhoto
import hashlib
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from api.utils import create_and_send_email_otp
from django.db import models

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}, 
            'token': {'write_only': True} ,
            "username": {"validators": []},  # 🔴 disable default UniqueValidator
            "email": {"validators": []},  # 🔴 disable default UniqueValidator
                        }
    
    def create(self, validated_data):
        password = validated_data.pop("password", None)

        username = validated_data.get("username")
        email = validated_data.get("email")

        # Check if user already exists
        existing_user = users.objects.filter(
            models.Q(username=username) | models.Q(email=email)
        ).first()

        if existing_user:
            errors = {}

            if existing_user.username == username:
                errors["username"] = ["User with this username already exists."]

            if existing_user.email == email:
                errors["email"] = ["User with this email already exists."]

            # include current active status
            if not existing_user.is_active and password:
                existing_user.password = make_password(password)
                existing_user.save(update_fields=["password"])

            errors["is_active"] = existing_user.is_active


            raise serializers.ValidationError(errors)

        # Create new user
        user = users.objects.create(**validated_data)

        if password:
            user.set_password(password)
            user.is_active = False       # block until OTP verification
            user.save(update_fields=["password", "is_active"])

            # Send OTP email
            create_and_send_email_otp(user)

        return user



    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password = make_password(password)
        instance.save()
        return instance


class EventSerializer(serializers.ModelSerializer):
    eventCreator = serializers.PrimaryKeyRelatedField(
        queryset=users.objects.all(),
        required=False,
        allow_null=True
    )
    eventCoverPhoto_url = serializers.SerializerMethodField()
    eventCreator_detail = UserSerializer(source="eventCreator", read_only=True)

    # visibility field MUST be here, before Meta:
    visibility = serializers.ChoiceField(
        choices=[("admin", "Admin"), ("img", "IMG Member"), ("public", "Public")],
        required=False,
        default="public",
    )

    class Meta:
        model = Events
        fields = (
            "eventid",
            "eventname",
            "eventdesc",
            "eventdate",
            "eventtime",
            "eventlocation",
            "eventCoverPhoto",
            "eventCoverPhoto_url",
            "eventCreator",
            "eventCreator_detail",
            "visibility",              # make sure it's included here
        )
        read_only_fields = ("eventid", "eventCoverPhoto_url", "eventCreator_detail")
        extra_kwargs = {
            "eventname": {"required": False},
            "eventdesc": {"required": False},
            "eventdate": {"required": False},
            "eventtime": {"required": False},
            "eventlocation": {"required": False},
            "eventCoverPhoto": {"required": False},
        }

    def get_eventCoverPhoto_url(self, obj):
        if obj.eventCoverPhoto:
            request = self.context.get("request")
            if request is not None:
                return request.build_absolute_uri(obj.eventCoverPhoto.url)
            return obj.eventCoverPhoto.url
        return None 


class PhotoSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(source="likecount", read_only=True)
    isLikedByCurrentUser = serializers.SerializerMethodField()
    event = EventSerializer(read_only=True)        
    uploadedBy = UserSerializer(read_only=True)

    event_id = serializers.PrimaryKeyRelatedField(
        source="event",
        queryset=Events.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Photo
        fields = [
            "photoid",
            "photoFile",
            "photoDesc",
            "uploadDate",

            # ✅ KEEP THESE (your point was correct)
            "extractedTags",
            "photoMeta",

            # counters
            "likes",
            "viewcount",
            "downloadcount",
            "commentcount",

            # relations
            "event",
            "uploadedBy",
            "event_id",

            # per-user flag
            "isLikedByCurrentUser",
        ]

    def get_isLikedByCurrentUser(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        # uses likedPhoto via related_name="likes"
        return obj.likes.filter(user=request.user).exists()
  

class likedPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = likedPhoto
        fields = '__all__'

class commentSerializer(serializers.ModelSerializer):
    class Meta:
        model = comment
        fields = '__all__'

class downloadedPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = downloadedPhoto
        fields = '__all__'

class viewedPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = viewedPhoto
        fields = '__all__'



class UserGroupSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=Group.objects.all()
    )

    class Meta:
        model = User
        fields = ["userid", "username", "email", "groups"]  # adjust userid field name
        read_only_fields = ["username", "email"]


class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
