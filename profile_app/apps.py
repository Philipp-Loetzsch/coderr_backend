
from django.apps import AppConfig

class ProfileAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profile_app' 

    def ready(self):
        try:
            import profile_app.models
        except ImportError:
            pass 