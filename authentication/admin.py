from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from authentication.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Configure custom user model in Django admin."""

    model = User

    list_display = (
        'email',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
    )

    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'groups',
    )

    search_fields = ('email',)

    ordering = ('email',)

    fieldsets = (
        (None, {
            'fields': ('email', 'password'),
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )

    readonly_fields = ('last_login', 'date_joined')