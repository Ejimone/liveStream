import logging
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Course, Assignment, AssignmentMaterial
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    AssignmentListSerializer,
    AssignmentDetailSerializer,
    MaterialSerializer
)
from .tasks import (
    sync_user_courses_task,
    sync_course_assignments_task, 
    sync_assignment_materials_task
)

logger = logging.getLogger(__name__)

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing courses imported from Google Classroom.
    Read-only since courses should only be modified via the Google Classroom API.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.all()
    
    def get_queryset(self):
        """Filter courses to those owned by the current user."""
        return Course.objects.filter(owner=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views."""
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer
    
    @action(detail=False, methods=['post'])
    def sync_all(self, request):
        """
        Trigger Celery task to sync all courses for the current user.
        """
        # Start the background task
        task = sync_user_courses_task.delay(request.user.id)
        
        # Return a success response with the task ID
        return Response({
            'message': 'Course synchronization started.',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def sync_assignments(self, request, pk=None):
        """
        Trigger Celery task to sync all assignments for a specific course.
        """
        course = self.get_object()
        
        # Start the background task
        task = sync_course_assignments_task.delay(course.id)
        
        # Update last_synced timestamp
        course.last_synced = timezone.now()
        course.save(update_fields=['last_synced'])
        
        return Response({
            'message': f'Assignment synchronization started for course: {course.name}.',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)

class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing assignments imported from Google Classroom.
    Read-only since assignments should only be modified via the Google Classroom API.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Assignment.objects.all()
    
    def get_queryset(self):
        """Filter assignments to those owned by the current user."""
        return Assignment.objects.filter(
            course__owner=self.request.user
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views."""
        if self.action == 'retrieve':
            return AssignmentDetailSerializer
        return AssignmentListSerializer
    
    @action(detail=True, methods=['post'])
    def sync_materials(self, request, pk=None):
        """
        Trigger Celery task to sync all materials for a specific assignment.
        """
        assignment = self.get_object()
        
        # Start the background task
        task = sync_assignment_materials_task.delay(assignment.id)
        
        # Update last_synced timestamp
        assignment.last_synced = timezone.now()
        assignment.save(update_fields=['last_synced'])
        
        return Response({
            'message': f'Material synchronization started for assignment: {assignment.title}.',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'])
    def by_course(self, request):
        """
        Filter assignments by course ID from query parameters.
        """
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {"error": "course_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ensure the course exists and belongs to the current user
        try:
            Course.objects.get(id=course_id, owner=request.user)
        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found or access denied"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Filter assignments
        assignments = self.get_queryset().filter(course_id=course_id)
        serializer = self.get_serializer_class()(assignments, many=True)
        return Response(serializer.data)

class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing materials imported from Google Classroom.
    Read-only since materials should only be modified via the Google Classroom API.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = AssignmentMaterial.objects.all()
    serializer_class = MaterialSerializer
    
    def get_queryset(self):
        """Filter materials to those owned by the current user."""
        return AssignmentMaterial.objects.filter(
            assignment__course__owner=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def by_assignment(self, request):
        """
        Filter materials by assignment ID from query parameters.
        """
        assignment_id = request.query_params.get('assignment_id')
        if not assignment_id:
            return Response(
                {"error": "assignment_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ensure the assignment exists and belongs to the current user
        try:
            Assignment.objects.get(id=assignment_id, course__owner=request.user)
        except Assignment.DoesNotExist:
            return Response(
                {"error": "Assignment not found or access denied"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Filter materials
        materials = self.get_queryset().filter(assignment_id=assignment_id)
        serializer = self.serializer_class(materials, many=True)
        return Response(serializer.data)