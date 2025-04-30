from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Profile

CustomUser = get_user_model()

class ExactProfileSerializer(serializers.ModelSerializer):
    """
    Serializer, der exakt die gewünschte JSON-Struktur abbildet.
    Kombiniert Felder von CustomUser und Profile.
    """
    user = serializers.IntegerField(source='user.id', read_only=True) 
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name') 
    last_name = serializers.CharField(source='user.last_name')  
    type = serializers.CharField(source='user.type', read_only=True)
    email = serializers.EmailField(source='user.email')        
    file = serializers.ImageField(source='profile_picture', read_only=True) 


    class Meta:
        model = Profile
        fields = [
            'user', 
            'username',
            'first_name',
            'last_name',
            'file',         
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]
        read_only_fields = ('user', 'username', 'type', 'created_at', 'file') 

    def update(self, instance, validated_data):
        user_data = {}
        if 'user' in validated_data: 
             user_data = validated_data.pop('user', {}) 
        else: 
             if 'first_name' in validated_data: user_data['first_name'] = validated_data.pop('first_name')
             if 'last_name' in validated_data: user_data['last_name'] = validated_data.pop('last_name')
             if 'email' in validated_data: user_data['email'] = validated_data.pop('email')

        profile_user = instance.user

        if user_data:
            profile_user.first_name = user_data.get('first_name', profile_user.first_name)
            profile_user.last_name = user_data.get('last_name', profile_user.last_name)
            profile_user.email = user_data.get('email', profile_user.email)
            profile_user.save()
        instance = super().update(instance, validated_data)
        return instance

class BaseProfileListSerializer(serializers.ModelSerializer):
    """ Basis-Serializer für Profil-Listen mit User-Infos. (Ohne business_name) """
    user = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    type = serializers.CharField(source='user.type')
    file = serializers.ImageField(source='profile_picture', read_only=True)
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)


    class Meta:
        model = Profile
        fields = ('user', 'username', 'first_name', 'last_name', 'type', 'file', 'uploaded_at') 
        read_only_fields = fields

class CustomerProfileListSerializer(BaseProfileListSerializer):
    """Serializer für die Kundenprofil-Liste."""
    class Meta(BaseProfileListSerializer.Meta):
         fields = ('user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type')
         read_only_fields = fields


class BusinessProfileListSerializer(BaseProfileListSerializer):
    """Serializer für die Geschäftsprofil-Liste."""

    uploaded_at = None 

    class Meta(BaseProfileListSerializer.Meta):
        fields = ('user', 'username', 'first_name', 'last_name', 'file',
                  'location', 'tel', 'description', 'working_hours', 'type')
        read_only_fields = fields