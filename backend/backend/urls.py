"""
URL patterns for the main project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # User management URLs - includes auth and profile endpoints
    path('api/users/', include('users.urls')),
    # Authentication-specific endpoints (Google OAuth)
    path('api/auth/', include('users.urls')),
    # Classroom integration APIs
    path('api/classroom/', include('classroom_integration.urls')),
    # AI processing APIs
    path('api/ai/', include('ai_processing.urls')),
    # Agent services
    path('api/agent/', include('aiAgent.urls')),
]
