from rest_framework import serializers
from .models import Course, Assignment, Material

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'google_id', 'name', 'description', 'owner', 'last_synced']
        read_only_fields = ['owner', 'google_id', 'last_synced']

class MaterialSerializer(serializers.ModelSerializer):
     class Meta:
        model = Material
        fields = ['id', 'google_id', 'title', 'google_link', 'file_type', 'processing_status']
        read_only_fields = ['google_id', 'processing_status']

class AssignmentSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True, read_only=True) # Nested materials

    class Meta:
        model = Assignment
        fields = ['id', 'google_id', 'course', 'title', 'description', 'due_date', 'google_link', 'status', 'materials', 'last_synced']
        read_only_fields = ['google_id', 'status', 'materials', 'last_synced']