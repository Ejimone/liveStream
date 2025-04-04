from django.contrib import admin
from .models import Course, Assignment, AssignmentMaterial

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'classroom_id', 'user', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at', 'updated_at')
    search_fields = ('name', 'classroom_id', 'user__email')
    readonly_fields = ('classroom_id', 'created_at', 'updated_at')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'course', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'classroom_id', 'course__name')
    readonly_fields = ('classroom_id', 'created_at', 'updated_at')

    class MaterialInline(admin.TabularInline):
        model = AssignmentMaterial
        extra = 0
        readonly_fields = ('created_at', 'updated_at')
        fields = ('name', 'material_type', 'download_link')

    inlines = [MaterialInline]

@admin.register(AssignmentMaterial)
class AssignmentMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'material_type', 'assignment', 'created_at')
    list_filter = ('material_type', 'created_at')
    search_fields = ('name', 'assignment__title')
    readonly_fields = ('created_at', 'updated_at')
