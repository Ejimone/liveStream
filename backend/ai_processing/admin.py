from django.contrib import admin
from .models import Document, Chunk, AssignmentDraft

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'material', 'processed_at', 'page_count', 'language')
    list_filter = ('processed_at', 'language')
    search_fields = ('material__title', 'raw_text')
    readonly_fields = ('processed_at', 'updated_at')
    date_hierarchy = 'processed_at'
    
    def get_material_title(self, obj):
        return obj.material.title
    
    get_material_title.short_description = 'Material Title'
    get_material_title.admin_order_field = 'material__title'

@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'chunk_index', 'text_preview')
    list_filter = ('document__material__assignment__course',)
    search_fields = ('text', 'document__material__title')
    
    def text_preview(self, obj):
        """Display a preview of the chunk text."""
        if len(obj.text) > 50:
            return obj.text[:50] + "..."
        return obj.text
    
    text_preview.short_description = 'Text Preview'

@admin.register(AssignmentDraft)
class AssignmentDraftAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'created_at', 'is_final', 'submitted')
    list_filter = ('created_at', 'is_final', 'submitted', 'assignment__course')
    search_fields = ('assignment__title', 'ai_generated_content', 'user_edited_content')
    readonly_fields = ('created_at', 'updated_at', 'submission_timestamp')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('assignment', 'is_final', 'submitted', 'submission_timestamp')
        }),
        ('Content', {
            'fields': ('ai_generated_content', 'user_edited_content', 'final_content_for_submission'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'prompt_used'),
            'classes': ('collapse',),
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make more fields readonly if the draft was already submitted."""
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.submitted:
            return readonly_fields + ('assignment', 'is_final', 'submitted', 
                                     'ai_generated_content', 'user_edited_content', 
                                     'final_content_for_submission')
        return readonly_fields
