from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import Role

User = get_user_model()

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display  = ('name', 'display_name')
    search_fields = ('name', 'display_name')

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (
            'first_name', 'last_name', 'email', 'phone_number',
            'address', 'village', 'state', 'district', 'taluka',
            'profile_picture'
        )}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Hierarchy', {'fields': ('created_by',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'role', 'created_by',
                'password1', 'password2',
                'is_active', 'is_staff', 'is_superuser'
            ),
        }),
    )
    list_display    = (
        'username', 'email', 'role', 'get_created_by_email',
        'is_active', 'is_staff', 'is_superuser', 'date_joined'
    )
    list_filter     = ('role', 'is_active', 'is_staff', 'is_superuser', 'created_by')
    search_fields   = ('username', 'email', 'created_by__username', 'created_by__email')
    ordering        = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    def get_created_by_email(self, obj):
        """Display the email of the user who created this user"""
        if obj.created_by:
            return obj.created_by.email
        return "No creator"
    get_created_by_email.short_description = 'Created By (Email)'
    get_created_by_email.admin_order_field = 'created_by__email'
    
    def save_model(self, request, obj, form, change):
        """Automatically set created_by to the current user when creating new users"""
        if not change:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
