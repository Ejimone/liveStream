from rest_framework import serializers
from .models import Course, Assignment, Material

class MaterialSerializer(serializers.ModelSerializer):
    """Serializer for Material model."""
    
    class Meta:
        model = Material
        fields = [
            'id', 'google_id', 'title', 'file_type', 
            'google_link', 'google_drive_file_id',
            'processing_status', 'created_at', 'updated_at'
        ]
        read_only_fields = fields

class AssignmentListSerializer(serializers.ModelSerializer):
    """
    Serializer for Assignment model in list views.
    Includes summary information about materials.
    """
    materials_count = serializers.SerializerMethodField()
    processed_materials_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'google_id', 'title', 'description', 
            'due_date', 'status', 'google_link',
            'materials_count', 'processed_materials_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_materials_count(self, obj):
        """Return the count of materials for this assignment."""
        return obj.materials.count()
    
    def get_processed_materials_count(self, obj):
        """Return the count of materials that have been fully processed."""
        return obj.materials.filter(processing_status='Processed').count()

class AssignmentDetailSerializer(AssignmentListSerializer):
    """
    Detailed serializer for Assignment including related materials.
    """
    materials = MaterialSerializer(many=True, read_only=True)
    
    class Meta(AssignmentListSerializer.Meta):
        fields = AssignmentListSerializer.Meta.fields + ['materials']

class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializer for Course model in list views.
    Includes summary information about assignments.
    """
    assignments_count = serializers.SerializerMethodField()
    unsubmitted_assignments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'google_id', 'name', 'description', 
            'last_synced', 'assignments_count', 
            'unsubmitted_assignments_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_assignments_count(self, obj):
        """Return the count of assignments for this course."""
        return obj.assignments.count()
    
    def get_unsubmitted_assignments_count(self, obj):
        """Return the count of assignments that haven't been submitted yet."""
        return obj.assignments.exclude(status='Submitted').count()

class CourseDetailSerializer(CourseListSerializer):
    """
    Detailed serializer for Course including related assignments.
    """
    assignments = AssignmentListSerializer(many=True, read_only=True)
    
    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ['assignments']