# user_auth_app/views.py

from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
# Importiere das Token-Modell für AuthToken
from rest_framework.authtoken.models import Token
# Importiere deine Serializer
from .serializers import RegistrationSerializer, LoginSerializer

# User = get_user_model() # Nur wenn du es direkt brauchst

class RegistrationView(APIView):
    """
    API-View zur Behandlung von Benutzerregistrierungen via POST.
    Verwendet RegistrationSerializer zur Validierung und Erstellung.
    """
    permission_classes = [AllowAny] # Jeder darf sich registrieren

    def post(self, request):
        """
        Verarbeitet POST-Anfragen zur Registrierung eines neuen Benutzers.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                data = {
                    'token': token.key,
                    'username': user.username,
                    'email': user.email,
                    'user_id': user.pk,
                }
                return Response(data, status=status.HTTP_201_CREATED)
            except serializer.ValidationError as e:
                 # Fängt Validierungsfehler aus serializer.create() auf
                 return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                 # Fängt andere unerwartete Fehler auf
                 print(f"Unerwarteter Fehler bei Registrierung: {e}") # Logging!
                 return Response({"detail": "Ein interner Fehler ist aufgetreten."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Wenn die initiale Validierung (serializer.is_valid()) fehlschlägt
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API-Endpunkt für den Benutzer-Login.
    Nimmt Username/Passwort entgegen, gibt bei Erfolg Token (AuthToken) und User-Infos zurück.
    """
    permission_classes = [AllowAny] # Jeder darf versuchen sich einzuloggen

    def post(self, request, *args, **kwargs):
        # Verwende LoginSerializer primär zur Doku/Struktur, Validierung ist einfach
        serializer = LoginSerializer(data=request.data)
        # raise_exception=True gibt bei fehlenden Feldern direkt 400 zurück
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        # Authentifiziere den Benutzer mit Djangos Auth-Backend
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                token = Token.objects.get(user=user)
                data = {
                    "token": token.key,
                    "username": user.username,
                    "email": user.email,
                    "user_id": user.pk,
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                
                return Response({
                    "detail": "Benutzerkonto ist deaktiviert."
                }, status=status.HTTP_401_UNAUTHORIZED) 
        else:
            return Response({
                 "detail": "Login fehlgeschlagen. Benutzername oder Passwort ungültig."
                 }, status=status.HTTP_401_UNAUTHORIZED)