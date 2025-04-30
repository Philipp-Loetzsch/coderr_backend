from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

CustomUser = get_user_model()
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('type',)}),
    )
    list_display = UserAdmin.list_display + ('type',)
    list_filter = UserAdmin.list_filter + ('type',)
admin.site.register(CustomUser, CustomUserAdmin)
