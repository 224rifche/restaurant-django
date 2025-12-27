from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('login', 'role', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('login',)
    ordering = ('login',)
    
    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        ('Informations personnelles', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'role', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )
    
    readonly_fields = ('created_at', 'last_login')
