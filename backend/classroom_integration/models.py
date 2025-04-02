from django.db import models
from django.conf import settings

# Represents a course imported from Google Classroom
class Course(models.Model):
    google_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    # Add other relevant fields from Classroom API if needed (e.g., enrollment_code)
    last_synced = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Represents an assignment imported from Google Classroom
class Assignment(models.Model):
    google_id = models.CharField(max_length=100, unique=True, db_index=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(null=True, blank=True)
    google_link = models.URLField(max_length=500, null=True, blank=True)
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Syncing', 'Syncing Materials'),
        ('Processing', 'Processing Materials'),
        ('MaterialsReady', 'Materials Ready for AI'),
        ('GeneratingDraft', 'Generating AI Draft'),
        ('DraftReady', 'Draft Ready for Review'),
        ('UserReviewing', 'User Reviewing'),
        ('GeneratingPDF', 'Generating PDF'), # If PDF step is needed
        ('Submitting', 'Submitting to Classroom'),
        ('Submitted', 'Submitted'),
        ('Error', 'Error'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='New')
    last_synced = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name} - {self.title}"

# Represents a material file attached to an assignment
class Material(models.Model):
    google_id = models.CharField(max_length=100, unique=True, db_index=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    google_drive_file_id = models.CharField(max_length=100, null=True, blank=True) # Drive ID if applicable
    google_link = models.URLField(max_length=500)
    file_type = models.CharField(max_length=50) # e.g., 'PDF', 'DOCX', 'GOOGLE_DOC'
    local_path = models.CharField(max_length=500, null=True, blank=True) # Path where downloaded/processed
    PROCESSING_STATUS_CHOICES = [
        ('Pending', 'Pending Download'),
        ('Downloading', 'Downloading'),
        ('Downloaded', 'Downloaded'),
        ('Processing', 'Extracting Text'),
        ('Chunking', 'Chunking Text'),
        ('Embedding', 'Generating Embeddings'),
        ('Processed', 'Processed & Indexed'),
        ('Error', 'Error'),
    ]
    processing_status = models.CharField(max_length=50, choices=PROCESSING_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title