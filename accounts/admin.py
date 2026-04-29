from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CoachProfile, CustomUser


class CoachProfileInline(admin.TabularInline):
    model = CoachProfile
    extra = 0
    fields = ('languages', 'speciality', 'about_me', 'years_of_experience')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = [CoachProfileInline]
    list_display = ('username', 'email', 'user_type', 'phone', 'picture', 'is_staff')
    list_filter = ('user_type', 'is_staff')

    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('user_type', 'phone', 'picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile', {'fields': ('user_type', 'phone', 'picture')}),
    )


@admin.register(CoachProfile)
class CoachProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'speciality', 'years_of_experience']
    list_filter = ['speciality']
    list_select_related = ['user']
    raw_id_fields = ['user']
