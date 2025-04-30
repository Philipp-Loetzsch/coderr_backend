from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegistrationSerializer, LoginSerializer

CustomUser = get_user_model()

class RegistrationView(generics.CreateAPIView):
    """
    API View für die Benutzerregistrierung.
    """
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    """
    API View für den Benutzer-Login.
    Nimmt Username/Passwort entgegen und gibt Token/Username/UserID zurück.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer 

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({
                'token': serializer.validated_data['token'],
                'username': serializer.validated_data['user'].username,
                'email': user.email,
                'user_id': serializer.validated_data['user_id']
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)