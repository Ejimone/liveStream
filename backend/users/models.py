from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    """
    Extended User model with additional fields for OAuth tokens and user preferences.
    """
    # Store Google OAuth credentials as JSON (encrypted in production)
    # Contains access_token, refresh_token, token_uri, client_id, client_secret, scopes
    google_oauth_mocked_credentials = models.JSONField(null=True, blank=True)
    
    # Additional user profile information
    profile_picture = models.URLField(max_length=500, null=True, blank=True)
    
    # User preferences
    notification_email = models.BooleanField(default=True)
    notification_app = models.BooleanField(default=True)
    auto_download_materials = models.BooleanField(default=True)
    auto_generate_drafts = models.BooleanField(default=False)
    
    # Timestamps
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_google_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email or self.username
    
    @property
    def has_valid_google_auth(self):
        """Check if user has Google credentials stored."""
        return self.google_oauth_mocked_credentials is not None

class UserPreference(models.Model):
    """
    Additional user preferences and settings.
    Separated from User model to allow more flexible expansion.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    
    # UI preferences
    theme = models.CharField(max_length=20, default='system')  # 'light', 'dark', 'system'
    dashboard_layout = models.CharField(max_length=20, default='list')  # 'list', 'grid', 'calendar'
    
    # Feature preferences
    enable_email_agent = models.BooleanField(default=True)
    enable_coursera = models.BooleanField(default=True)
    
    # Advanced settings as JSON for flexibility
    advanced_settings = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Preferences for {self.user}"