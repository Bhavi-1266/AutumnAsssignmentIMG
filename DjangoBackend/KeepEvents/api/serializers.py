from rest_framework import serializers
from users.models import users
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

