from rest_framework import serializers
from ..models import UserProfile, ProfileType


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer für das UserProfile-Modell.
    Wird für Detailansicht, Listen und Updates verwendet.
    Blendet 'working_hours' für Customer aus.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True, use_url=True) 
    location = serializers.CharField(required=False, allow_blank=True, max_length=255)
    tel = serializers.CharField(required=False, allow_blank=True, max_length=50)
    description = serializers.CharField(required=False, allow_blank=True, style={'base_template': 'textarea.html'})
    working_hours = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    type = serializers.CharField(source='profile_type', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username', 'first_name', 'last_name', 'email',
            'profile_picture', 'location', 'tel', 'description',
            'working_hours', 'type',
        ]
        read_only_fields = ['user', 'username', 'first_name', 'last_name', 'email']

    def to_representation(self, instance):
        """ Passt die Ausgabe an: Entfernt 'working_hours' für Customer. """
        representation = super().to_representation(instance)
        if instance.profile_type == ProfileType.CUSTOMER:
            representation.pop('working_hours', None)
        return representation