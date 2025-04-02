from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserPreference

User = get_user_model()

class UserPreferenceInline(admin.StackedInline):
    model = UserPreference
    can_delete = False
    verbose_name_plural = 'Preferences'
    fk_name = 'user'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'has_google_auth')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'notification_email')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    inlines = (UserPreferenceInline,)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'profile_picture')}),
        ('Google Authentication', {'fields': ('google_oauth_mocked_credentials', 'last_google_sync')}),
        ('Notifications & Preferences', {'fields': ('notification_email', 'notification_app', 
                                                   'auto_download_materials', 'auto_generate_drafts')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'last_login_ip')}),
    )
    
    def has_google_auth(self, obj):
        """Check if user has Google credentials stored."""
        return obj.has_valid_google_auth
    
    has_google_auth.boolean = True
    has_google_auth.short_description = 'Google Auth'

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'dashboard_layout', 'enable_email_agent', 'enable_coursera')
    list_filter = ('theme', 'dashboard_layout', 'enable_email_agent', 'enable_coursera')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)
