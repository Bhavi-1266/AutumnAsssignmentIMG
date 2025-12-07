from django.contrib import admin
from django.utils.html import mark_safe
from .models import users

@admin.register(users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'dept', 'batch', 'thumbnail', 'is_active')
    readonly_fields = ('date_joined', 'thumbnail')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal', {'fields': ('email', 'userProfile', 'thumbnail', 'userbio', 'enrollmentNo')}),
        ('Academic', {'fields': ('dept', 'batch')}),
        ('Permissions', {'fields': ('is_active',)}),
        ('Dates', {'fields': ('date_joined',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email','password','userProfile','userbio','dept','batch','enrollmentNo'),
        }),
    )

    def thumbnail(self, obj):
        if obj.userProfile:
            return mark_safe(f'<img src="{obj.userProfile.url}" style="height:60px;border-radius:4px;" />')
        return "-"
    thumbnail.short_description = 'Profile'
