from django.db import models
from django.conf import settings

class Course(models.Model):
    """
    Represents a Google Classroom course.
    """
    google_id = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        unique_together = ('google_id', 'owner')
    
    def __str__(self):
        return f"{self.name} ({self.google_id})"

class Assignment(models.Model):
    """
    Represents a Google Classroom assignment.
    """
    ASSIGNMENT_STATUS_CHOICES = [
        ('New', 'New'),  # Just fetched, not processed yet
        ('Syncing', 'Syncing'),  # Currently syncing materials
        ('Processing', 'Processing'),  # Materials being processed
        ('MaterialsReady', 'Materials Ready'),  # Materials processed, ready for draft generation
        ('GeneratingDraft', 'Generating Draft'),  # AI is generating draft
        ('DraftReady', 'Draft Ready'),  # AI draft is ready for user review
        ('UserReviewing', 'User Reviewing'),  # User is reviewing/editing the draft
        ('GeneratingPDF', 'Generating PDF'),  # Generating PDF for submission
        ('Submitting', 'Submitting'),  # Submitting to Google Classroom
        ('Submitted', 'Submitted'),  # Successfully submitted
        ('Error', 'Error'),  # Error occurred during processing
    ]
    
    google_id = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    google_link = models.URLField(max_length=500, null=True, blank=True)  # Link to assignment in Google Classroom
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default='New')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        unique_together = ('google_id', 'course')
    
    def __str__(self):
        return f"{self.title} ({self.google_id})"

class Material(models.Model):
    """
    Represents a material attached to a Google Classroom assignment.
    """
    MATERIAL_TYPE_CHOICES = [
        ('GOOGLE_DRIVE', 'Google Drive'),
        ('LINK', 'Web Link'),
        ('YOUTUBE', 'YouTube Video'),
        ('FORM', 'Google Form'),
        ('Unknown', 'Unknown')
    ]
    
    PROCESSING_STATUS_CHOICES = [
        ('Pending', 'Pending'),  # Not yet processed
        ('Downloading', 'Downloading'),  # Currently being downloaded
        ('Downloaded', 'Downloaded'),  # Downloaded but not processed
        ('Processing', 'Processing'),  # Text being extracted
        ('Chunking', 'Chunking'),  # Text is being chunked
        ('Embedding', 'Embedding'),  # Generating embeddings
        ('Processed', 'Processed'),  # Fully processed and ready to use
        ('Error', 'Error'),  # Processing error
    ]
    
    google_id = models.CharField(max_length=255)  # Could be Drive file ID, URL for links, etc.
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES, default='Unknown')
    google_link = models.URLField(max_length=500, null=True, blank=True)  # Link to file in Google Drive
    google_drive_file_id = models.CharField(max_length=255, null=True, blank=True)  # For Drive files only
    local_path = models.CharField(max_length=500, null=True, blank=True)  # Path to local copy if downloaded
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
        unique_together = ('google_id', 'assignment')
    
    def __str__(self):
        return f"{self.title} ({self.file_type})"