from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    # Google OAuth 2.0 login flow
    path('google/login/', views.GoogleLoginView.as_view(), name='google-login'),
    path('google/callback/', views.GoogleCallbackView.as_view(), name='google-callback'),
    
    # Session management
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User profile management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('preferences/', views.UserPreferenceView.as_view(), name='user-preferences'),
]