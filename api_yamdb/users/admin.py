from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'bio',
        'role'
    )
    list_editable = ('role',)
    search_fields = (
        'email',
        'first_name',
        'last_name',
        'username',
    )
    list_filter = ('role', 'is_staff')
    empty_value_display = '-пусто-'


admin.site.register(User, CustomUserAdmin)
