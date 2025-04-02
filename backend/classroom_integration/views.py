from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Assignment
from .serializers import CourseSerializer, AssignmentSerializer
# from .services import get_google_service # Service to get authenticated Google API client
# from .tasks import sync_course_assignments_task, download_assignment_materials_task, submit_assignment_task

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Courses.
    Provides 'list' and 'retrieve' actions.
    Includes custom action to sync courses from Google Classroom.
    """
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return courses owned by the currently authenticated user
        return Course.objects.filter(owner=self.request.user)

    @action(detail=False, methods=['post'], url_path='sync')
    def sync_courses(self, request):
        """
        Trigger background task to sync courses from Google Classroom for the user.
        """
        user = request.user
        # Placeholder: Initiate Celery task to fetch courses
        # sync_courses_task.delay(user.id)
        print(f"Placeholder: Triggering course sync for user {user.id}")
        return Response({"message": "Course synchronization initiated."}, status=status.HTTP_202_ACCEPTED)


class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Assignments.
    Provides 'list' and 'retrieve' actions based on course.
    Includes custom action to sync assignments for a specific course.
    """
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter assignments based on the course_pk from the URL
        # Assumes URL pattern like /api/classroom/courses/{course_pk}/assignments/
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            return Assignment.objects.filter(course__owner=self.request.user, course__pk=course_pk)
        return Assignment.objects.none() # Or return all user's assignments if needed

    @action(detail=True, methods=['post'], url_path='sync-materials')
    def sync_and_download_materials(self, request, pk=None):
        """
        Trigger background task to fetch assignment details, download materials.
        This corresponds to parts of 'Workspace_assignments' and 'download_material'.
        """
        try:
            assignment = self.get_object()
            if assignment.course.owner != request.user:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

            # Placeholder: Initiate Celery task
            # download_assignment_materials_task.delay(assignment.id)
            print(f"Placeholder: Triggering material download/processing for assignment {assignment.id}")
            assignment.status = 'Processing' # Update status
            assignment.save()
            return Response({"message": "Assignment material processing initiated."}, status=status.HTTP_202_ACCEPTED)
        except Assignment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Log the error
            print(f"Error initiating material processing: {e}")
            return Response({"error": "Failed to start processing."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_generated_assignment(self, request, pk=None):
        """
        Trigger submission of a *user-reviewed* assignment draft.
        Corresponds to 'upload_submission'.
        Requires draft_id or similar identifier in request data.
        """
        try:
            assignment = self.get_object()
            if assignment.course.owner != request.user:
                 return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

            draft_id = request.data.get('draft_id')
            if not draft_id:
                return Response({"error": "Draft ID is required for submission."}, status=status.HTTP_400_BAD_REQUEST)

            # 1. Fetch the specific AssignmentDraft by draft_id
            # draft = AssignmentDraft.objects.get(pk=draft_id, assignment=assignment)

            # 2. **** CRITICAL: Verify user has reviewed/approved the draft ****
            #    This check MUST exist based on the draft's status or a separate approval flag.
            # if draft.status != 'UserReviewed' and draft.status != 'ReadyToSubmit': # Example status check
            #     return Response({"error": "Draft must be reviewed and approved before submission."}, status=status.HTTP_400_BAD_REQUEST)

            # 3. Placeholder: Initiate Celery task for actual submission
            #    Pass the necessary content (draft.final_content_for_submission)
            # submit_assignment_task.delay(assignment.id, draft_id)
            print(f"Placeholder: Triggering submission for assignment {assignment.id} using draft {draft_id}")
            assignment.status = 'Submitting' # Update status
            assignment.save()
            return Response({"message": "Assignment submission initiated."}, status=status.HTTP_202_ACCEPTED)

        except Assignment.DoesNotExist:
             return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        # except AssignmentDraft.DoesNotExist:
        #     return Response({"error": "Specified draft not found for this assignment."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Log the error
            print(f"Error initiating submission: {e}")
            return Response({"error": "Failed to start submission."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)