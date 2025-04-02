from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserPreference

User = get_user_model()

class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user preferences."""
    
    class Meta:
        model = UserPreference
        fields = ['theme', 'dashboard_layout', 'enable_email_agent', 'enable_coursera', 'advanced_settings']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information."""
    preferences = UserPreferenceSerializer(read_only=True)
    has_valid_google_auth = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'profile_picture', 'notification_email', 'notification_app',
                  'auto_download_materials', 'auto_generate_drafts',
                  'last_google_sync', 'has_valid_google_auth', 'preferences']
        read_only_fields = ['id', 'username', 'email', 'last_google_sync', 
                           'has_valid_google_auth']


class UserPreferenceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user notification and automation preferences."""
    
    class Meta:
        model = User
        fields = ['notification_email', 'notification_app', 
                 'auto_download_materials', 'auto_generate_drafts']


class UserPersonalInfoUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user personal information."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_picture']