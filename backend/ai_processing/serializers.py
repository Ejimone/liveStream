from rest_framework import serializers
from .models import Document, Chunk, AssignmentDraft
from classroom_integration.models import Assignment
from classroom_integration.serializers import AssignmentListSerializer

class ChunkSerializer(serializers.ModelSerializer):
    """Serializer for text chunks."""
    
    class Meta:
        model = Chunk
        fields = ['id', 'text', 'chunk_index', 'metadata']
        read_only_fields = fields

class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for processed documents."""
    
    class Meta:
        model = Document
        fields = ['id', 'material', 'processed_at', 'updated_at', 'page_count', 'language']
        read_only_fields = fields

class DocumentDetailSerializer(DocumentSerializer):
    """Detailed document serializer with text content and chunks."""
    chunks = ChunkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = DocumentSerializer.Meta.fields + ['raw_text', 'chunks']
        read_only_fields = fields

class AssignmentDraftSerializer(serializers.ModelSerializer):
    """Serializer for AI-generated assignment drafts."""
    
    class Meta:
        model = AssignmentDraft
        fields = [
            'id', 'assignment', 'created_at', 'updated_at',
            'is_final', 'submitted', 'submission_timestamp',
        ]
        read_only_fields = ['id', 'assignment', 'created_at', 'updated_at', 'submitted', 'submission_timestamp']

class AssignmentDraftDetailSerializer(AssignmentDraftSerializer):
    """Detailed serializer for drafts including content."""
    assignment_details = AssignmentListSerializer(source='assignment', read_only=True)
    relevant_chunk_texts = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentDraft
        fields = AssignmentDraftSerializer.Meta.fields + [
            'ai_generated_content', 'user_edited_content', 
            'final_content_for_submission', 'assignment_details',
            'relevant_chunk_texts'
        ]
        read_only_fields = ['id', 'assignment', 'created_at', 'updated_at', 
                          'ai_generated_content', 'submitted', 'submission_timestamp',
                          'assignment_details', 'relevant_chunk_texts']
    
    def get_relevant_chunk_texts(self, obj):
        """Return text from the relevant chunks used for this draft."""
        chunks = obj.relevant_chunks.all().order_by('document', 'chunk_index')
        return [chunk.text for chunk in chunks]

class DraftUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating drafts with user edits."""
    
    class Meta:
        model = AssignmentDraft
        fields = ['user_edited_content', 'final_content_for_submission', 'is_final']

class GenerateDraftSerializer(serializers.Serializer):
    """Serializer for requesting draft generation for an assignment."""
    assignment_id = serializers.IntegerField()
    
    def validate_assignment_id(self, value):
        """Validate the assignment exists and is ready for draft generation."""
        try:
            assignment = Assignment.objects.get(pk=value)
            valid_statuses = ['MaterialsReady', 'DraftReady', 'Error']
            if assignment.status not in valid_statuses:
                raise serializers.ValidationError(
                    f"Assignment must be in one of these statuses: {', '.join(valid_statuses)}. "
                    f"Current status: {assignment.status}"
                )
        except Assignment.DoesNotExist:
            raise serializers.ValidationError("Assignment not found")
        return value

class SubmitDraftSerializer(serializers.Serializer):
    """Serializer for requesting submission of a finalized draft."""
    draft_id = serializers.IntegerField()
    
    def validate_draft_id(self, value):
        """Validate the draft exists and is ready for submission."""
        try:
            draft = AssignmentDraft.objects.get(pk=value)
            if not draft.is_final:
                raise serializers.ValidationError("Draft must be marked as final before submission")
            if not draft.final_content_for_submission:
                raise serializers.ValidationError("Draft has no final content for submission")
            if draft.submitted:
                raise serializers.ValidationError("Draft has already been submitted")
        except AssignmentDraft.DoesNotExist:
            raise serializers.ValidationError("Draft not found")
        return value