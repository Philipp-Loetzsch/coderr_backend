# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from ..models import Profile

# CustomUser = get_user_model()

# class ExactProfileSerializer(serializers.ModelSerializer):
#     """
#     Serializer for detailed profile view and update.
#     Handles fields from both the Profile model and the related User model.
#     Allows updating user's first_name, last_name, and email alongside profile fields.
#     """
#     user = serializers.IntegerField(source='user.id', read_only=True)
#     username = serializers.CharField(source='user.username', read_only=True)
#     first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True, max_length=150)
#     last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True, max_length=150)
#     type = serializers.CharField(source='user.type', read_only=True)
#     email = serializers.EmailField(source='user.email', required=False)
#     file = serializers.ImageField(source='profile_picture', required=False, allow_null=True)
#     location = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
#     tel = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
#     description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     working_hours = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
#     created_at = serializers.DateTimeField(read_only=True)

#     class Meta:
#         model = Profile
#         fields = [
#             'user', 'username', 'first_name', 'last_name', 'file', 'location',
#             'tel', 'description', 'working_hours', 'type', 'email', 'created_at',
#         ]
#         read_only_fields = ('user', 'username', 'type', 'created_at')

#     def update(self, instance, validated_data):
#         profile_user = instance.user    
#         user_updated = False
        
#         user_data = validated_data.pop('user', None)
#         if user_data:
#             if 'first_name' in user_data:
#                 profile_user.first_name = user_data['first_name']
#                 user_updated = True
#             if 'last_name' in user_data:
#                 profile_user.last_name = user_data['last_name']
#                 user_updated = True
#             if 'email' in user_data:
#                 profile_user.email = user_data['email']
#                 user_updated = True
        
#         if user_updated:
#             profile_user.save()
            
#         instance = super().update(instance, validated_data)

#         return instance

# class BaseProfileListSerializer(serializers.ModelSerializer):
#     """
#     Base serializer for profile list views, providing common user and profile information.
#     Designed to be inherited by more specific list serializers.
#     """
#     user = serializers.IntegerField(source='user.id', read_only=True)
#     username = serializers.CharField(source='user.username', read_only=True)
#     first_name = serializers.CharField(source='user.first_name', read_only=True)
#     last_name = serializers.CharField(source='user.last_name', read_only=True)
#     type = serializers.CharField(source='user.type', read_only=True)
#     file = serializers.ImageField(source='profile_picture', read_only=True)
#     uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)

#     class Meta:
#         model = Profile
#         fields = ('user', 'username', 'first_name', 'last_name', 'type', 'file', 'uploaded_at')
#         read_only_fields = fields

# class CustomerProfileListSerializer(BaseProfileListSerializer):
#     """
#     Serializer for listing customer profiles. Inherits from BaseProfileListSerializer.
#     """
#     class Meta(BaseProfileListSerializer.Meta):
#           fields = ('user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type')
#           read_only_fields = fields


# class BusinessProfileListSerializer(BaseProfileListSerializer):
#     """
#     Serializer for listing business profiles. Inherits from BaseProfileListSerializer
#     and adds business-specific fields.
#     """
#     uploaded_at = None
#     location = serializers.CharField(max_length=100, read_only=True)
#     tel = serializers.CharField(max_length=20, read_only=True)
#     description = serializers.CharField(read_only=True)
#     working_hours = serializers.CharField(max_length=100, read_only=True)

#     class Meta(BaseProfileListSerializer.Meta):
#          fields = ('user', 'username', 'first_name', 'last_name', 'file',
#                    'location', 'tel', 'description', 'working_hours', 'type')
#          read_only_fields = fields

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Profile

CustomUser = get_user_model()

class ExactProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True, max_length=150, allow_null=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True, max_length=150, allow_null=True)
    type = serializers.CharField(source='user.type', read_only=True)
    email = serializers.EmailField(source='user.email', required=False, allow_null=True)
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        fields_to_empty_string_if_null = [
            'first_name', 'last_name', 'email', 'file',
            'location', 'tel', 'description', 'working_hours'
        ]
        for field_name in fields_to_empty_string_if_null:
            if field_name in representation and representation[field_name] is None:
                representation[field_name] = ""
        return representation

    def update(self, instance, validated_data):
        profile_user = instance.user
        user_updated = False
        
        user_data_from_request = {}
        if 'first_name' in validated_data:
            user_data_from_request['first_name'] = validated_data.pop('first_name')
        if 'last_name' in validated_data:
            user_data_from_request['last_name'] = validated_data.pop('last_name')
        if 'email' in validated_data:
            user_data_from_request['email'] = validated_data.pop('email')
        
        if user_data_from_request.get('first_name') is not None:
            profile_user.first_name = user_data_from_request['first_name']
            user_updated = True
        if user_data_from_request.get('last_name') is not None:
            profile_user.last_name = user_data_from_request['last_name']
            user_updated = True
        if user_data_from_request.get('email') is not None:
            profile_user.email = user_data_from_request['email']
            user_updated = True
        
        if user_updated:
            profile_user.save()
            
        instance = super().update(instance, validated_data)
        return instance

class BaseProfileListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True, allow_null=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True, allow_null=True)
    type = serializers.CharField(source='user.type', read_only=True)
    file = serializers.ImageField(source='profile_picture', read_only=True, allow_null=True)
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)
    location = serializers.CharField(max_length=100, read_only=True, allow_null=True)
    tel = serializers.CharField(max_length=20, read_only=True, allow_null=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    working_hours = serializers.CharField(max_length=100, read_only=True, allow_null=True)

    class Meta:
        model = Profile
        fields = ('user', 'username', 'first_name', 'last_name', 'type', 'file', 'uploaded_at',
                  'location', 'tel', 'description', 'working_hours')
        read_only_fields = fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        fields_to_empty_string_if_null = [
            'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours'
        ]
        for field_name in fields_to_empty_string_if_null:
            if field_name in self.fields and field_name in representation and representation[field_name] is None:
                representation[field_name] = ""
        return representation

class CustomerProfileListSerializer(BaseProfileListSerializer):
    class Meta(BaseProfileListSerializer.Meta):
          fields = ('user', 'username', 'first_name', 'last_name', 'type', 'file', 'uploaded_at')

class BusinessProfileListSerializer(BaseProfileListSerializer):
    class Meta(BaseProfileListSerializer.Meta):
         fields = ('user', 'username', 'first_name', 'last_name', 'type', 'file',
                   'location', 'tel', 'description', 'working_hours')
