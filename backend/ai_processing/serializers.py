from rest_framework import serializers
from .models import AssignmentDraft

class AssignmentDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentDraft
        fields = ['id', 'assignment', 'generated_content', 'status', 'user_edits', 'final_content_for_submission', 'created_at']
        read_only_fields = ['status', 'generated_content', 'created_at'] # User mainly updates edits/final_content