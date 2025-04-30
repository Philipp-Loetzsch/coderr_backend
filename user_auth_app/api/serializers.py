from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

CustomUser = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source='auth_token.key', read_only=True)
    user_id = serializers.IntegerField(source='id', read_only=True) 
    repeated_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('user_id', 'username', 'email', 'password', 'repeated_password', 'type', 'token')
        read_only_fields = ('user_id', 'token')
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'email': {'required': True, 'allow_blank': False},
            'type': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            type=validated_data['type']
        )
        Token.objects.get_or_create(user=user)
        return user

    def to_representation(self, instance):
        return {
            'token': instance.auth_token.key,
            'username': instance.username,
            'email': instance.email,
            'user_id': instance.id
        }

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')
        token, created = Token.objects.get_or_create(user=user)
        data['user'] = user
        data['token'] = token.key
        data['user_id'] = user.id
        return data
class UserDetailsSerializer(serializers.ModelSerializer):
     class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'type')