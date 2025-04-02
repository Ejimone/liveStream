import logging
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document, Chunk, AssignmentDraft
from .serializers import (
    DocumentSerializer, 
    DocumentDetailSerializer,
    AssignmentDraftSerializer,
    AssignmentDraftDetailSerializer,
    DraftUpdateSerializer,
    GenerateDraftSerializer,
    SubmitDraftSerializer
)
from classroom_integration.models import Assignment
from .tasks import generate_assignment_draft_task, finalize_and_submit_draft_task

logger = logging.getLogger(__name__)

class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing processed documents.
    Read-only since documents should only be created/modified through the
    material processing pipeline.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Document.objects.all().order_by('-updated_at')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DocumentDetailSerializer
        return DocumentSerializer
    
    def get_queryset(self):
        """Filter documents to those owned by the current user."""
        user = self.request.user
        return Document.objects.filter(
            material__assignment__course__owner=user
        ).order_by('-updated_at')

class AssignmentDraftViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Assignment drafts.
    Allows viewing all drafts and updating specific ones.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = AssignmentDraft.objects.all().order_by('-updated_at')
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return DraftUpdateSerializer
        if self.action == 'retrieve':
            return AssignmentDraftDetailSerializer
        return AssignmentDraftSerializer
    
    def get_queryset(self):
        """Filter drafts to those owned by the current user."""
        user = self.request.user
        return AssignmentDraft.objects.filter(
            assignment__course__owner=user
        ).order_by('-updated_at')
    
    @action(detail=True, methods=['post'])
    def approve_for_submission(self, request, pk=None):
        """
        Mark a draft as final and ready for submission.
        This endpoint requires that user_edited_content or final_content_for_submission 
        is already populated.
        """
        draft = self.get_object()
        
        # Check if there's content to submit
        if not draft.user_edited_content and not draft.final_content_for_submission:
            return Response(
                {"error": "Draft must have user edited content or final content before approval."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # If final_content_for_submission is not set, use user_edited_content
        if not draft.final_content_for_submission and draft.user_edited_content:
            draft.final_content_for_submission = draft.user_edited_content
        
        # Mark as final
        draft.is_final = True
        draft.save(update_fields=['is_final', 'final_content_for_submission'])
        
        # Update assignment status to reflect user review completed
        draft.assignment.status = 'UserReviewing'
        draft.assignment.save(update_fields=['status'])
        
        return Response({"message": "Draft approved for submission."})

class GenerateDraftView(generics.CreateAPIView):
    """
    API view for requesting generation of a new draft for an assignment.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GenerateDraftSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        assignment_id = serializer.validated_data['assignment_id']
        
        # Verify current user owns this assignment
        try:
            assignment = Assignment.objects.get(
                pk=assignment_id,
                course__owner=request.user
            )
        except Assignment.DoesNotExist:
            return Response(
                {"error": "Assignment not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update status
        assignment.status = 'GeneratingDraft'
        assignment.save(update_fields=['status'])
        
        # Trigger celery task
        task = generate_assignment_draft_task.delay(assignment_id)
        
        return Response({
            "message": "Draft generation started",
            "task_id": task.id,
            "assignment_id": assignment_id
        })

class SubmitDraftView(generics.CreateAPIView):
    """
    API view for requesting submission of a finalized draft.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmitDraftSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        draft_id = serializer.validated_data['draft_id']
        
        # Verify current user owns this draft
        try:
            draft = AssignmentDraft.objects.select_related('assignment__course').get(
                pk=draft_id,
                assignment__course__owner=request.user
            )
        except AssignmentDraft.DoesNotExist:
            return Response(
                {"error": "Draft not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update assignment status
        draft.assignment.status = 'GeneratingPDF'
        draft.assignment.save(update_fields=['status'])
        
        # Trigger celery task
        task = finalize_and_submit_draft_task.delay(draft_id)
        
        return Response({
            "message": "Draft submission started",
            "task_id": task.id,
            "draft_id": draft_id,
            "assignment_id": draft.assignment.id
        })