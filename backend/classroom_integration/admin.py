from django.contrib import admin
from .models import Course, Assignment, Material

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'google_id', 'owner', 'created_at', 'last_synced')
    list_filter = ('owner', 'created_at', 'last_synced')
    search_fields = ('name', 'google_id', 'owner__email')
    readonly_fields = ('google_id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'course', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'google_id', 'course__name')
    readonly_fields = ('google_id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    # Nested material inline for viewing materials within an assignment
    class MaterialInline(admin.TabularInline):
        model = Material
        extra = 0
        readonly_fields = ('google_id', 'created_at', 'updated_at')
        fields = ('title', 'file_type', 'processing_status', 'google_link')
        
    inlines = [MaterialInline]

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'assignment', 'processing_status', 'created_at')
    list_filter = ('file_type', 'processing_status', 'created_at')
    search_fields = ('title', 'google_id', 'assignment__title')
    readonly_fields = ('google_id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def assignment_course(self, obj):
        return obj.assignment.course
    
    assignment_course.short_description = 'Course'
    assignment_course.admin_order_field = 'assignment__course'
