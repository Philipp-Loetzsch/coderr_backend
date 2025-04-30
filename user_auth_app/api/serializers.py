from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

CustomUser = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer für die Benutzerregistrierung.
    Erstellt einen Benutzer und gibt einen Token zurück.
    """
    token = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('user_id', 'username', 'email', 'password', 'type', 'token')
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'email': {'required': True, 'allow_blank': False},
            'type': {'required': True}
        }

    def get_token(self, user):
        token, created = Token.objects.get_or_create(user=user)
        return token.key

    def get_user_id(self, user):
        return user.id

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            type=validated_data['type']
        )
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer für den Benutzer-Login.
    Authentifiziert Benutzer und gibt Token, Username und User-ID zurück.
    """
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