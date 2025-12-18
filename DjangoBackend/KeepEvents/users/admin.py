# accounts/admin.py (or wherever your user admin is)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

User = get_user_model()

@admin.register(User)   # use your actual model class, not `users` string
class UsersAdmin(UserAdmin):
    list_display = ("userid",'username', 'email', 'dept', 'batch', 'thumbnail', 'is_active')
    readonly_fields = ("userid", "date_joined", 'thumbnail')

    fieldsets = (
        (None, {'fields': ('userid', 'username', 'password')}),
        ('Personal', {'fields': ('email', 'userProfile', 'thumbnail', 'userbio', 'enrollmentNo')}),
        ('Academic', {'fields': ('dept', 'batch')}),
        # IMPORTANT: include groups & permissions here
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                
                'username',
                'email',
                'password1', 'password2',  # use password1/password2 for add form
                'userProfile',
                'userbio',
                'dept',
                'batch',
                'enrollmentNo',
                'is_staff',
                'is_superuser',
                'is_active',
                'groups',
            ),
        }),
    )

    def thumbnail(self, obj):
        if obj.userProfile:
            return mark_safe(f'<img src="{obj.userProfile.url}" style="height:60px;border-radius:4px;" />')
        return "-"
    thumbnail.short_description = 'Profile'
