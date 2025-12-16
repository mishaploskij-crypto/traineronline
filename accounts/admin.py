from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar', 'bio')
        }),
        ('Роль и права', {
            'fields': ('role', 'groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser')
        }),
        ('Для тренеров', {
            'fields': ('specialization', 'experience_years', 'education'),
            'classes': ('collapse',)
        }),
        ('Для тренирующихся', {
            'fields': ('birth_date', 'fitness_level'),
            'classes': ('collapse',)
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )