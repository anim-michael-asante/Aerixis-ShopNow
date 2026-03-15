from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('phone', 'city', 'address', 'bio', 'avatar')


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'full_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    def full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name or format_html('<span style="color:#9CA3AF">—</span>')
    full_name.short_description = 'Full Name'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
