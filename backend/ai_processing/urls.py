from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet)
router.register(r'drafts', views.AssignmentDraftViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-draft/', views.GenerateDraftView.as_view(), name='generate-draft'),
    path('submit-draft/', views.SubmitDraftView.as_view(), name='submit-draft'),
]