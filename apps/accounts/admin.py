from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ['email', 'username', 'account_type', 'role', 'is_verified', 'is_active', 'date_joined']
    list_filter   = ['account_type', 'is_verified', 'is_active', 'groups']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering      = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('EventNest', {'fields': ('account_type', 'phone', 'bio', 'is_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('EventNest', {'fields': ('email', 'account_type', 'phone')}),
    )
