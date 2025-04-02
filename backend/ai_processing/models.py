from django.db import models
from apps.classroom_integration.models import Assignment, Material

# Represents a generated draft answer for an assignment part/question
class AssignmentDraft(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='drafts')
    # If assignment has multiple parts/questions, link to that part
    # question_text = models.TextField(blank=True, null=True) # The specific question being answered
    generated_content = models.TextField()
    # Store the relevant context chunks used for generation for traceability
    retrieved_context = models.JSONField(null=True, blank=True)
    # Status: 'Generated', 'UserReviewed', 'ReadyToSubmit'
    status = models.CharField(max_length=50, default='Generated')
    # Store feedback or edits from user review
    user_edits = models.TextField(blank=True, null=True)
    final_content_for_submission = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Draft for {self.assignment.title}"

# Represents chunks of text extracted from materials for RAG
class TextChunk(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='chunks')
    chunk_text = models.TextField()
    chunk_order = models.IntegerField() # Order within the material
    # vector_embedding = models.BinaryField(null=True, blank=True) # Store embedding directly if not using external DB
    # Or reference an ID in an external vector store
    vector_store_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chunk {self.chunk_order} from {self.material.title}"