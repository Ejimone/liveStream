from django.contrib import admin
from .models import AgentTask, EmailDraft, SearchResult

class EmailDraftInline(admin.StackedInline):
    model = EmailDraft
    can_delete = False
    verbose_name_plural = 'Email Draft'
    
    fieldsets = (
        ('Email Info', {
            'fields': ('subject', 'to_recipients', 'cc_recipients', 'bcc_recipients')
        }),
        ('Content', {
            'fields': ('ai_generated_content', 'user_edited_content', 'final_content'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'gmail_message_id')
        })
    )
    
    readonly_fields = ('sent_at',)

class SearchResultInline(admin.TabularInline):
    model = SearchResult
    extra = 0
    fields = ('title', 'url', 'position', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(AgentTask)
class AgentTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_type', 'user', 'status', 'created_at', 'completed_at')
    list_filter = ('task_type', 'status', 'created_at')
    search_fields = ('prompt', 'response', 'user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Task Information', {
            'fields': ('user', 'task_type', 'prompt', 'status')
        }),
        ('Response', {
            'fields': ('response',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [EmailDraftInline, SearchResultInline]
    
    def get_inline_instances(self, request, obj=None):
        """Show only relevant inlines based on task type."""
        inlines = []
        if not obj:
            return inlines
            
        if obj.task_type == 'email_draft':
            inlines.append(type('EmailDraftInline', (EmailDraftInline,), {})(self.model, self.admin_site))
        elif obj.task_type == 'web_search':
            inlines.append(type('SearchResultInline', (SearchResultInline,), {})(self.model, self.admin_site))
            
        return inlines

@admin.register(EmailDraft)
class EmailDraftAdmin(admin.ModelAdmin):
    list_display = ('subject', 'get_user', 'status', 'recipient_count', 'created_at', 'sent_at')
    list_filter = ('status', 'created_at', 'sent_at')
    search_fields = ('subject', 'to_recipients', 'cc_recipients', 'ai_generated_content', 'user_edited_content')
    readonly_fields = ('created_at', 'updated_at', 'sent_at', 'agent_task')
    
    fieldsets = (
        ('Email Information', {
            'fields': ('agent_task', 'subject', 'status')
        }),
        ('Recipients', {
            'fields': ('to_recipients', 'cc_recipients', 'bcc_recipients')
        }),
        ('Content', {
            'fields': ('ai_generated_content', 'user_edited_content', 'final_content'),
            'classes': ('collapse',)
        }),
        ('Delivery Information', {
            'fields': ('sent_at', 'gmail_message_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user(self, obj):
        return obj.agent_task.user.email
    
    get_user.short_description = 'User'
    get_user.admin_order_field = 'agent_task__user__email'

@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'position', 'get_user', 'created_at')
    list_filter = ('created_at', 'position')
    search_fields = ('title', 'snippet', 'url', 'agent_task__prompt')
    readonly_fields = ('created_at', 'agent_task')
    
    def get_user(self, obj):
        return obj.agent_task.user.email
    
    get_user.short_description = 'User'
    get_user.admin_order_field = 'agent_task__user__email'
