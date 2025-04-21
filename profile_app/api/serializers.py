from rest_framework import serializers
from ..models import UserProfile

class ProfileBusinessListSerializer(serializers.ModelSerializer):
    """
    Serializer für die Listenansicht von Business-Profilen (/profiles/business/).
    """
    
    file = serializers.ImageField(source='profile_picture', read_only=True, required=False)
    type = serializers.CharField(source='profile_type', read_only=True)

    class Meta:
        model = UserProfile
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
        ]
        read_only_fields = [ 
            'user', 'username', 'first_name', 'last_name', 'type',
        ]


class ProfileCustomerListSerializer(serializers.ModelSerializer):
    """
    Serializer für die Listenansicht von Customer-Profilen (/profiles/customer/).
    """
    
    file = serializers.ImageField(source='profile_picture', read_only=True, required=False)
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True, format="%Y-%m-%dT%H:%M:%S")
    type = serializers.CharField(source='profile_type', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',       
            'username',     
            'first_name',   
            'last_name',    
            'file',         
            'uploaded_at',   
            'type',          
        ]
        read_only_fields = [
            'user', 'username', 'first_name', 'last_name', 'uploaded_at', 'type',
        ]


class CurrentUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer für die Detailansicht und zum Aktualisieren
    des Profils des aktuell eingeloggten Benutzers (/profile/).
    """
    
    username = serializers.CharField(read_only=True)    
    file = serializers.ImageField(source='profile_picture', required=False)
    type = serializers.CharField(source='profile_type', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',          
            'username',      
            'email',         
            'first_name',   
            'last_name',    
            'file',          
            'location',      
            'tel',           
            'description',   
            'working_hours',  
            'type',         
            'created_at',     
        ]
        read_only_fields = [
            'user', 'created_at', 'type', 'username'
        ]