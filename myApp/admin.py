from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Driver, CustomUser, Trip, ChatMessage


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        (('Personal info'), {'fields': ('firstName', 'lastName')}),
        (('User type'), {'fields': ('isClient', 'isDriver')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'firstName', 'lastName', 'email', 'password1', 'password2', 'isClient', 'isDriver'),
        }),
    )
    list_display = ('username', 'email', 'firstName', 'lastName', 'is_staff')
    search_fields = ('username', 'email', 'firstName', 'lastName')
    ordering = ('username',)

# Register your models here.
admin.site.register(Driver)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Trip)
admin.site.register(ChatMessage)