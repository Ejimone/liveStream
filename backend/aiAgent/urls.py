from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tasks', views.AgentTaskViewSet, basename='agent-task')
router.register(r'email-drafts', views.EmailDraftViewSet, basename='email-draft')

urlpatterns = [
    path('', include(router.urls)),
]