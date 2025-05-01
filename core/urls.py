from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

api_urlpatterns = [
    path('', include('profile_app.api.urls')),
    path('', include('user_auth_app.api.urls')),
    path('', include('offers_app.api.urls')),
    path('', include('orders_app.api.urls')),
    path('', include('reviews_app.api.urls')),
    path('', include('base_info_app.api.urls')),   
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)