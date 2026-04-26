from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone', 'is_staff')
    list_filter = ('user_type', 'is_staff')

    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('user_type', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile', {'fields': ('user_type', 'phone')}),
    )
