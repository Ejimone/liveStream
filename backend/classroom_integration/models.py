from django.db import models
from django.conf import settings

class Course(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    classroom_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    classroom_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('new', 'New'),
            ('processing', 'Processing'),
            ('draft_ready', 'Draft Ready'),
            ('reviewing', 'Reviewing'),
            ('generating_pdf', 'Generating PDF'),
            ('uploading', 'Uploading'),
            ('submitted', 'Submitted'),
            ('error', 'Error'),
        ],
        default='new'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class AssignmentMaterial(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='materials')
    name = models.CharField(max_length=255)
    material_type = models.CharField(max_length=50, choices=[('pdf', 'PDF'), ('doc', 'Document'), ('slide', 'Slide')])
    download_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AssignmentDraft(models.Model):
    assignment = models.OneToOneField(Assignment, on_delete=models.CASCADE, related_name='draft')
    ai_generated_content = models.TextField(blank=True, null=True)
    user_edited_content = models.TextField(blank=True, null=True)
    final_content_for_submission = models.TextField(blank=True, null=True)
    is_final = models.BooleanField(default=False)
    submitted = models.BooleanField(default=False)
    submission_timestamp = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Draft for {self.assignment.title}"