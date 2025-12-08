from rest_framework import serializers
from users.models import users
from events.models import Events
import hashlib


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}, 'token': {'write_only': True}}
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = users.objects.create(**validated_data)
        if password:
            user.password = hashlib.sha256(password.encode()).hexdigest()
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password = hashlib.sha256(password.encode()).hexdigest()
        instance.save()
        return instance

class EventSerializer(serializers.ModelSerializer):
    # Writable field - accepts user ID for creating/updating
    eventCreator = serializers.PrimaryKeyRelatedField(
        queryset=users.objects.all(),
        required=False,
        allow_null=True
    )
    
    # Read-only field - returns full URL to the uploaded image
    eventCoverPhoto_url = serializers.SerializerMethodField()
    
    # Read-only field - returns full user details
    eventCreator_detail = UserSerializer(source="eventCreator", read_only=True)
    
    class Meta:
        model = Events
        fields = (
            "eventid",
            "eventname",
            "eventdesc",
            "eventdate",
            "eventtime",
            "eventlocation",
            "eventCoverPhoto",      # Writable - upload file here
            "eventCoverPhoto_url",  # Read-only - returns full URL
            "eventCreator",         # Writable - accepts user ID
            "eventCreator_detail"   # Read-only - returns full user object
        )
        read_only_fields = ("eventid", "eventCoverPhoto_url", "eventCreator_detail")
        extra_kwargs = {
            'eventname': {'required': False},
            'eventdesc': {'required': False},
            'eventdate': {'required': False},
            'eventtime': {'required': False},
            'eventlocation': {'required': False},
            'eventCoverPhoto': {'required': False},
        }
    def get_eventCoverPhoto_url(self, obj):
        """Generate full URL for the event cover photo"""
        if obj.eventCoverPhoto:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.eventCoverPhoto.url)
            return obj.eventCoverPhoto.url
        return None

