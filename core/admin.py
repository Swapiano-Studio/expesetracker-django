from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'job', 'income', 'country', 'city')
    search_fields = ('username', 'email', 'country', 'city')
    list_filter = ('user_type', 'job', 'income', 'country', 'city')

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'job', 'income', 'country', 'city', 'address')
        }),
    )
