from rest_framework import serializers
from .models import AgentTask, EmailDraft, SearchResult

class AgentTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying agent task details.
    """
    class Meta:
        model = AgentTask
        fields = [
            'id', 'user', 'task_type', 'prompt', 'status', 
            'response', 'metadata', 'created_at', 'updated_at', 
            'completed_at'
        ]
        read_only_fields = ['user', 'status', 'response', 'created_at', 'updated_at', 'completed_at']

class AgentTaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new agent tasks.
    """
    class Meta:
        model = AgentTask
        fields = ['task_type', 'prompt', 'metadata']

class EmailDraftSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying email draft details.
    """
    class Meta:
        model = EmailDraft
        fields = [
            'id', 'agent_task', 'subject', 'to_recipients', 
            'cc_recipients', 'bcc_recipients', 'ai_generated_content',
            'user_edited_content', 'final_content', 'status',
            'created_at', 'updated_at', 'sent_at', 'gmail_message_id'
        ]
        read_only_fields = [
            'agent_task', 'ai_generated_content', 'final_content', 
            'created_at', 'updated_at', 'sent_at', 'gmail_message_id'
        ]

class EmailDraftUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating email drafts (primarily for user edits).
    """
    class Meta:
        model = EmailDraft
        fields = ['subject', 'to_recipients', 'cc_recipients', 'bcc_recipients', 'user_edited_content']

class SearchResultSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying search results.
    """
    class Meta:
        model = SearchResult
        fields = ['id', 'agent_task', 'title', 'snippet', 'url', 'position']
        read_only_fields = ['agent_task']