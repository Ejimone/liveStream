from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Add any additional user fields if needed later
    google_oauth_mocked_credentials = models.JSONField(null=True, blank=True, help_text="Store Google OAuth access and refresh tokens securely")

    def __str__(self):
        return self.username

# Optional: Profile model if more user details are needed separate from Auth User
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     # Add profile specific fields, e.g., selected theme, preferences
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)