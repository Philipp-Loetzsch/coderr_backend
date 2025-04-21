
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from profile_app.models import UserProfile, ProfileType
from django.db import transaction

User = get_user_model() 

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer für die Benutzerregistrierung.
    Validiert Eingaben und erstellt User + zugehöriges Profil.
    """
    repeated_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )
    type = serializers.ChoiceField(
        choices=ProfileType.choices,
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}}
        }

    def validate(self, data):
        """
        Zusätzliche Validierungen: Passwort-Match, Passwort-Stärke, E-Mail/Username-Eindeutigkeit.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"password": "Passwörter stimmen nicht überein."})

        try:
            validate_password(data['password'], user=None)
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Ein Benutzer mit dieser E-Mail existiert bereits."})

        if User.objects.filter(username=data['username']).exists():
             raise serializers.ValidationError({"username": "Ein Benutzer mit diesem Benutzernamen existiert bereits."})

        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        profile_type = validated_data.pop('type')
        user = None

        try:
            with transaction.atomic(): 
                user = User.objects.create_user(**validated_data)
                UserProfile.objects.create(user=user, profile_type=profile_type)

        except Exception as e:
            print(f"FEHLER bei Registrierung (Rollback durchgeführt): {e}")
            raise serializers.ValidationError(f"Registrierung fehlgeschlagen: {e}")
       
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer für den User-Login. Nimmt Username/Passwort entgegen.
    Die eigentliche Authentifizierung findet in der View statt.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )