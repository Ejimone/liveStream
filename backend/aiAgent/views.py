from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import AgentTask, EmailDraft, SearchResult
from .serializers import AgentTaskSerializer, EmailDraftSerializer, SearchResultSerializer
from .agent import process_agent_task, send_email

class AgentTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing agent tasks including creating, listing, and retrieving task details.
    """
    serializer_class = AgentTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AgentTask.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        # Process the agent task asynchronously
        # In a production environment, this would be a Celery task
        process_agent_task(task.id)
        
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a pending or processing task
        """
        task = self.get_object()
        if task.status in ['pending', 'processing']:
            task.status = 'failed'
            task.metadata['cancelled'] = True
            task.metadata['cancellation_reason'] = 'User cancelled the task'
            task.save()
            return Response({'status': 'task cancelled'})
        return Response({'error': 'Cannot cancel a task that is already completed or failed'}, 
                        status=status.HTTP_400_BAD_REQUEST)


class EmailDraftViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing email drafts including creating, editing, and sending emails.
    """
    serializer_class = EmailDraftSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return EmailDraft.objects.filter(agent_task__user=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Mark the email as approved by the user and ready to send
        """
        email_draft = self.get_object()
        if email_draft.status != 'draft':
            return Response({'error': 'Can only approve drafts'}, 
                            status=status.HTTP_400_BAD_REQUEST)
            
        # Update with user's edited content if provided
        if 'user_edited_content' in request.data:
            email_draft.user_edited_content = request.data['user_edited_content']
            
        # The final content is either the user's edited version or the AI version
        email_draft.final_content = email_draft.user_edited_content or email_draft.ai_generated_content
        email_draft.status = 'ready'
        email_draft.save()
        
        return Response({'status': 'email draft approved'})
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """
        Send the approved email
        """
        email_draft = self.get_object()
        if email_draft.status != 'ready':
            return Response({'error': 'Can only send approved drafts'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Send email using Gmail API
            message_id = send_email(email_draft, request.user)
            
            # Update email status
            email_draft.status = 'sent'
            email_draft.sent_at = timezone.now()
            email_draft.gmail_message_id = message_id
            email_draft.save()
            
            return Response({'status': 'email sent', 'message_id': message_id})
        except Exception as e:
            email_draft.status = 'failed'
            email_draft.metadata = {
                'error': str(e),
                'error_time': timezone.now().isoformat()
            }
            email_draft.save()
            return Response({'error': f'Failed to send email: {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
