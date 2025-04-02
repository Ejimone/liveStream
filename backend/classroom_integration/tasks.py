import logging
from celery import shared_task
from django.utils import timezone
from users.models import User
from .models import Course, Assignment, Material
from .services import fetch_classroom_courses, fetch_course_assignments, download_drive_file
# Import the task from ai_processing to trigger it after download
from ai_processing.tasks import process_material_task

logger = logging.getLogger(__name__)

@shared_task
def sync_user_courses_task(user_id):
    """
    Celery task to fetch courses from Google Classroom for a user
    and update the database.
    """
    try:
        user = User.objects.get(pk=user_id)
        logger.info(f"Starting course sync for user {user.email} (ID: {user_id})")
        
        google_courses = fetch_classroom_courses(user)
        if google_courses is None:
            logger.error(f"Failed to fetch courses from Google for user {user.email}")
            return f"Failed to fetch courses for user {user_id}"

        synced_count = 0
        created_count = 0
        existing_google_ids = set(Course.objects.filter(owner=user).values_list('google_id', flat=True))
        fetched_google_ids = set()

        for gc in google_courses:
            google_id = gc.get('id')
            if not google_id:
                continue
            
            fetched_google_ids.add(google_id)
            defaults = {
                'name': gc.get('name', 'Untitled Course'),
                'description': gc.get('description', ''),
                'last_synced': timezone.now()
            }
            course, created = Course.objects.update_or_create(
                google_id=google_id,
                owner=user,
                defaults=defaults
            )
            synced_count += 1
            if created:
                created_count += 1
                logger.info(f"Created new course: {course.name} (ID: {google_id}) for user {user.email}")
            else:
                logger.debug(f"Updated existing course: {course.name} (ID: {google_id}) for user {user.email}")

        # Optional: Handle courses removed from Google Classroom (if needed)
        # removed_ids = existing_google_ids - fetched_google_ids
        # if removed_ids:
        #     Course.objects.filter(owner=user, google_id__in=removed_ids).delete()
        #     logger.info(f"Removed {len(removed_ids)} courses no longer found in Google Classroom for user {user.email}")

        logger.info(f"Course sync completed for user {user.email}. Synced: {synced_count}, Created: {created_count}")
        return f"Course sync completed for user {user_id}. Synced: {synced_count}, Created: {created_count}"

    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found for course sync.")
        return f"User {user_id} not found."
    except Exception as e:
        logger.exception(f"Error during course sync for user {user_id}: {e}")
        # Consider adding error status to user profile or notification system
        raise # Re-raise for Celery monitoring


@shared_task
def sync_course_assignments_task(course_id):
    """
    Celery task to fetch assignments for a specific course from Google Classroom
    and update the database.
    """
    try:
        course = Course.objects.select_related('owner').get(pk=course_id)
        user = course.owner
        logger.info(f"Starting assignment sync for course '{course.name}' (ID: {course.google_id}) for user {user.email}")

        google_assignments = fetch_course_assignments(user, course.google_id)
        if google_assignments is None:
            logger.error(f"Failed to fetch assignments from Google for course {course.google_id}")
            return f"Failed to fetch assignments for course {course_id}"

        synced_count = 0
        created_count = 0
        material_tasks_triggered = 0

        for ga in google_assignments:
            google_id = ga.get('id')
            if not google_id:
                continue

            defaults = {
                'title': ga.get('title', 'Untitled Assignment'),
                'description': ga.get('description', ''),
                'google_link': ga.get('alternateLink'),
                'last_synced': timezone.now(),
                # Update due date if present
                'due_date': ga.get('dueDate') # Needs parsing from Google format
            }
            assignment, created = Assignment.objects.update_or_create(
                google_id=google_id,
                course=course,
                defaults=defaults
            )
            synced_count += 1
            if created:
                created_count += 1
                logger.info(f"Created new assignment: {assignment.title} (ID: {google_id}) in course {course.name}")
                # Trigger material sync for newly created assignments
                sync_assignment_materials_task.delay(assignment.id)
                material_tasks_triggered += 1
            else:
                logger.debug(f"Updated existing assignment: {assignment.title} (ID: {google_id}) in course {course.name}")
                # Optionally re-sync materials if assignment updated recently?

        course.last_synced = timezone.now() # Mark course as synced
        course.save(update_fields=['last_synced'])

        logger.info(f"Assignment sync completed for course '{course.name}'. Synced: {synced_count}, Created: {created_count}, Material Syncs Triggered: {material_tasks_triggered}")
        return f"Assignment sync completed for course {course_id}. Synced: {synced_count}, Created: {created_count}"

    except Course.DoesNotExist:
        logger.error(f"Course with ID {course_id} not found for assignment sync.")
        return f"Course {course_id} not found."
    except Exception as e:
        logger.exception(f"Error during assignment sync for course {course_id}: {e}")
        raise


@shared_task
def sync_assignment_materials_task(assignment_id):
    """
    Celery task to fetch materials for a specific assignment from Google Classroom,
    download them (if from Drive), and trigger processing.
    """
    try:
        assignment = Assignment.objects.select_related('course__owner').get(pk=assignment_id)
        user = assignment.course.owner
        logger.info(f"Starting material sync for assignment '{assignment.title}' (ID: {assignment.google_id})")
        assignment.status = 'Syncing'
        assignment.save(update_fields=['status'])

        # Fetch assignment details again to get materials (Classroom API structure)
        classroom_service = get_google_service(user, 'classroom', 'v1')
        if not classroom_service:
            raise Exception("Failed to get Classroom service")

        ga_details = classroom_service.courses().courseWork().get(
            courseId=assignment.course.google_id,
            id=assignment.google_id
        ).execute()

        google_materials = ga_details.get('materials', [])
        logger.info(f"Found {len(google_materials)} materials for assignment {assignment.google_id}")

        materials_processed_count = 0
        materials_to_process = []

        for gm in google_materials:
            drive_file = gm.get('driveFile')
            link = gm.get('link')
            youtube_video = gm.get('youtubeVideo') # Add handling if needed
            form = gm.get('form') # Add handling if needed

            material_google_id = None
            material_title = "Untitled Material"
            material_link = None
            material_type = "Unknown"
            drive_file_id = None

            if drive_file:
                df = drive_file.get('driveFile', {})
                material_google_id = df.get('id')
                material_title = df.get('title', 'Drive File')
                material_link = df.get('alternateLink')
                drive_file_id = material_google_id # Store Drive ID for download
                # Determine file type from Drive API later if needed, or use title extension
                material_type = "GOOGLE_DRIVE"
            elif link:
                material_google_id = link.get('url') # Use URL as ID for links
                material_title = link.get('title', 'Link')
                material_link = link.get('url')
                material_type = "LINK"
            # Add elif for youtube_video, form etc.

            if material_google_id:
                mat, created = Material.objects.update_or_create(
                    google_id=material_google_id,
                    assignment=assignment,
                    defaults={
                        'title': material_title,
                        'google_link': material_link,
                        'file_type': material_type,
                        'google_drive_file_id': drive_file_id,
                        'processing_status': 'Pending' # Reset status on sync
                    }
                )
                if created:
                    logger.info(f"Created new material record: {mat.title} (ID: {material_google_id})")
                else:
                    logger.debug(f"Updated material record: {mat.title} (ID: {material_google_id})")
                
                # If it's a Drive file, trigger download and processing
                if drive_file_id:
                    materials_to_process.append(mat.id)
            else:
                logger.warning(f"Could not identify Google ID for material: {gm}")

        # Trigger download/processing tasks for Drive files
        if materials_to_process:
            assignment.status = 'Processing'
            logger.info(f"Triggering processing for {len(materials_to_process)} materials.")
            for mat_id in materials_to_process:
                download_and_process_material_task.delay(mat_id)
        else:
            # If no Drive materials, mark as ready (or handle links differently)
            assignment.status = 'MaterialsReady' 
            logger.info(f"No Drive materials found to process for assignment {assignment.google_id}. Marked as MaterialsReady.")
            
        assignment.save(update_fields=['status'])
        return f"Material sync completed for assignment {assignment_id}. Triggered processing for {len(materials_to_process)} items."

    except Assignment.DoesNotExist:
        logger.error(f"Assignment with ID {assignment_id} not found for material sync.")
        return f"Assignment {assignment_id} not found."
    except HttpError as error:
        logger.error(f"API error during material sync for assignment {assignment_id}: {error}")
        if assignment:
            assignment.status = 'Error'
            assignment.save(update_fields=['status'])
        raise
    except Exception as e:
        logger.exception(f"Error during material sync for assignment {assignment_id}: {e}")
        if assignment:
            assignment.status = 'Error'
            assignment.save(update_fields=['status'])
        raise

@shared_task
def download_and_process_material_task(material_id):
    """
    Celery task to download a specific material file from Google Drive
    and trigger the AI processing pipeline.
    """
    try:
        material = Material.objects.select_related('assignment__course__owner').get(pk=material_id)
        user = material.assignment.course.owner
        drive_file_id = material.google_drive_file_id

        if not drive_file_id:
            logger.warning(f"Material {material_id} ('{material.title}') has no Google Drive file ID. Skipping download.")
            material.processing_status = 'Error' # Or a different status like 'NotApplicable'
            material.save(update_fields=['processing_status'])
            return f"Material {material_id} is not a Drive file."

        logger.info(f"Starting download for material {material_id} ('{material.title}') - Drive ID: {drive_file_id}")
        material.processing_status = 'Downloading'
        material.save(update_fields=['processing_status'])

        file_stream = download_drive_file(user, drive_file_id)

        if file_stream:
            logger.info(f"Successfully downloaded material {material_id}. Triggering AI processing.")
            material.processing_status = 'Downloaded'
            material.save(update_fields=['processing_status'])
            
            # Trigger the AI processing task (text extraction, chunking, embedding)
            # Pass the content directly if small enough, or save temporarily and pass path
            # For simplicity, let's assume process_material_task handles the stream
            process_material_task.delay(material_id, file_stream.getvalue()) # Pass file content as bytes
            
            return f"Material {material_id} downloaded. Processing triggered."
        else:
            logger.error(f"Failed to download material {material_id} from Google Drive.")
            material.processing_status = 'Error'
            material.save(update_fields=['processing_status'])
            return f"Failed to download material {material_id}."

    except Material.DoesNotExist:
        logger.error(f"Material with ID {material_id} not found for download.")
        return f"Material {material_id} not found."
    except Exception as e:
        logger.exception(f"Error during material download/process trigger for material {material_id}: {e}")
        try:
            # Try to mark material as error if possible
            material = Material.objects.get(pk=material_id)
            material.processing_status = 'Error'
            material.save(update_fields=['processing_status'])
        except Material.DoesNotExist:
            pass # Material already gone?
        raise

# Placeholder for submission task
@shared_task
def submit_assignment_task(assignment_id, draft_id):
    """
    Celery task to submit the final, user-approved assignment draft.
    Requires PDF generation and Classroom API submission.
    """
    # 1. Fetch Assignment and the specific approved AssignmentDraft
    # 2. Get final_content_for_submission from the draft
    # 3. Generate PDF from final_content_for_submission (using xhtml2pdf or similar)
    #    - Save PDF temporarily
    # 4. Use classroom_integration.services.submit_assignment_work to upload/submit
    # 5. Update Assignment status to 'Submitted' or 'Error'
    # 6. Clean up temporary PDF file
    logger.warning(f"Placeholder: Submission task for assignment {assignment_id} using draft {draft_id} needs implementation.")
    # Simulate work
    import time
    time.sleep(5)
    # Update status (example)
    # assignment = Assignment.objects.get(pk=assignment_id)
    # assignment.status = 'Submitted'
    # assignment.save()
    return f"Placeholder: Submission complete for assignment {assignment_id}"
