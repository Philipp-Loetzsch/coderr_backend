# base_app/api/urls.py
from django.urls import path
from .views import BaseInfoView

app_name = 'base_app_api'

urlpatterns = [
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]