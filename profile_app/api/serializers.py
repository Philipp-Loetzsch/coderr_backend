from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Profile

CustomUser = get_user_model()

class ExactProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True, max_length=150)
    type = serializers.CharField(source='user.type', read_only=True)
    email = serializers.EmailField(source='user.email', required=False)
    file = serializers.ImageField(source='profile_picture', required=False, allow_null=True)
    location = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    tel = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    working_hours = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location',
            'tel', 'description', 'working_hours', 'type', 'email', 'created_at',
        ]
        read_only_fields = ('user', 'username', 'type', 'created_at')

    def update(self, instance, validated_data):
        profile_user = instance.user    
        user_updated = False
        
        user_data = validated_data.pop('user', None)
        if user_data:
            if 'first_name' in user_data:
                profile_user.first_name = user_data['first_name']
                user_updated = True
            if 'last_name' in user_data:
                profile_user.last_name = user_data['last_name']
                user_updated = True
            if 'email' in user_data:
                profile_user.email = user_data['email']
                user_updated = True
        
        if user_updated:
            profile_user.save()
            
        instance = super().update(instance, validated_data)

        return instance

class BaseProfileListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    type = serializers.CharField(source='user.type', read_only=True)
    file = serializers.ImageField(source='profile_picture', read_only=True)
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Profile
        fields = ('user', 'username', 'first_name', 'last_name', 'type', 'file', 'uploaded_at')
        read_only_fields = fields

class CustomerProfileListSerializer(BaseProfileListSerializer):
    class Meta(BaseProfileListSerializer.Meta):
          fields = ('user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type')
          read_only_fields = fields


class BusinessProfileListSerializer(BaseProfileListSerializer):
    uploaded_at = None
    location = serializers.CharField(max_length=100, read_only=True)
    tel = serializers.CharField(max_length=20, read_only=True)
    description = serializers.CharField(read_only=True)
    working_hours = serializers.CharField(max_length=100, read_only=True)

    class Meta(BaseProfileListSerializer.Meta):
         fields = ('user', 'username', 'first_name', 'last_name', 'file',
                   'location', 'tel', 'description', 'working_hours', 'type')
         read_only_fields = fields