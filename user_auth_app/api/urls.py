# user_auth_app/urls.py

from django.urls import path
# Importiere die Views aus der gleichen App
from .views import RegistrationView, LoginView

#app_name = 'user_auth_app' # Optional: Namespace für die URLs

urlpatterns = [
    # URL für die Registrierung
    path('registration/', RegistrationView.as_view(), name='registration'), # Name angepasst an JSON
    # URL für den Login
    path('login/', LoginView.as_view(), name='login'), # Name angepasst an JSON
]