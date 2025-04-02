"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')), # Auth endpoints (login, logout, callback)
    # path('api/', include(router.urls)), # Include DRF router URLs
    path('api/classroom/', include('apps.classroom_integration.urls')),
    path('api/ai/', include('apps.ai_processing.urls')),
    path('api/agent/', include('apps.agent_services.urls')),
]
