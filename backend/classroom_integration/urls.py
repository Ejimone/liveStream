from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'assignments', views.AssignmentViewSet)
router.register(r'materials', views.MaterialViewSet)

urlpatterns = [
    path('', include(router.urls)),
]