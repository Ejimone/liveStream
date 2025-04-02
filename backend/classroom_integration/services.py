import logging
import io
from django.conf import settings
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from users.models import User # Assuming User model is in 'users' app

logger = logging.getLogger(__name__)

def get_google_credentials(user: User) -> Credentials | None:
    """
    Retrieves and potentially refreshes Google OAuth credentials for a user.
    Returns valid Credentials object or None if invalid/missing.
    """
    creds_data = user.google_oauth_mocked_credentials
    if not creds_data:
        logger.warning(f"No Google credentials found for user {user.email}")
        return None

    try:
        # Reconstruct credentials from stored JSON data
        credentials = Credentials(
            token=creds_data.get('token'),
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=creds_data.get('client_id', settings.GOOGLE_CLIENT_ID),
            client_secret=creds_data.get('client_secret', settings.GOOGLE_CLIENT_SECRET),
            scopes=creds_data.get('scopes', settings.GOOGLE_SCOPES)
            # expiry is handled automatically by the Credentials object
        )

        # Check if credentials are valid and refresh if necessary
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                try:
                    logger.info(f"Refreshing Google token for user {user.email}")
                    credentials.refresh(GoogleRequest())
                    logger.info(f"Token refreshed successfully for user {user.email}")
                    # Update stored credentials with the new token (and potentially new refresh token)
                    user.google_oauth_mocked_credentials['token'] = credentials.token
                    # Sometimes refresh token is re-issued, update if present
                    if hasattr(credentials, 'refresh_token') and credentials.refresh_token:
                         user.google_oauth_mocked_credentials['refresh_token'] = credentials.refresh_token
                    user.google_oauth_mocked_credentials['expiry'] = credentials.expiry.isoformat() if credentials.expiry else None
                    user.save(update_fields=['google_oauth_mocked_credentials'])
                except Exception as e:
                    logger.exception(f"Failed to refresh Google token for user {user.email}. Clearing credentials.")
                    # Clear invalid credentials if refresh fails
                    user.google_oauth_mocked_credentials = None
                    user.save(update_fields=['google_oauth_mocked_credentials'])
                    return None
            else:
                # Invalid credentials without a refresh token
                logger.error(f"Invalid Google credentials and no refresh token for user {user.email}. Cannot proceed.")
                return None

        return credentials

    except Exception as e:
        logger.exception(f"Error reconstructing or validating Google credentials for user {user.email}")
        return None


def get_google_service(user: User, service_name: str, version: str):
    """
    Builds and returns an authenticated Google API service client.
    Handles credential retrieval and refresh.
    Returns the service object or None on failure.
    """
    credentials = get_google_credentials(user)
    if not credentials:
        return None

    try:
        service = build(service_name, version, credentials=credentials, cache_discovery=False)
        logger.debug(f"Successfully built Google service '{service_name} v{version}' for user {user.email}")
        return service
    except HttpError as error:
        logger.error(f"An API error occurred building service {service_name}: {error}")
        # Handle specific errors like insufficient permissions if needed
        return None
    except Exception as e:
        logger.exception(f"Unexpected error building Google service {service_name} for user {user.email}")
        return None

# --- Placeholder Functions for Classroom/Drive API Calls ---

def fetch_classroom_courses(user: User):
    """Placeholder: Fetches courses from Google Classroom API."""
    service = get_google_service(user, 'classroom', 'v1')
    if not service:
        return None # Indicate failure

    try:
        logger.info(f"Fetching courses for user {user.email}")
        results = service.courses().list(studentId='me').execute()
        courses = results.get('courses', [])
        logger.info(f"Found {len(courses)} courses for user {user.email}")
        return courses
    except HttpError as error:
        logger.error(f"API error fetching courses for {user.email}: {error}")
        return None
    except Exception as e:
        logger.exception(f"Error fetching courses for {user.email}")
        return None


def fetch_course_assignments(user: User, course_id: str):
    """Placeholder: Fetches assignments for a specific course."""
    service = get_google_service(user, 'classroom', 'v1')
    if not service:
        return None

    try:
        logger.info(f"Fetching assignments for course {course_id} for user {user.email}")
        results = service.courses().courseWork().list(
            courseId=course_id,
            courseWorkStates=['PUBLISHED'] # Fetch only published assignments
        ).execute()
        assignments = results.get('courseWork', [])
        logger.info(f"Found {len(assignments)} assignments for course {course_id}")
        return assignments
    except HttpError as error:
        logger.error(f"API error fetching assignments for course {course_id}: {error}")
        return None
    except Exception as e:
        logger.exception(f"Error fetching assignments for course {course_id}")
        return None


def download_drive_file(user: User, file_id: str) -> io.BytesIO | None:
    """Placeholder: Downloads a file from Google Drive by its ID."""
    service = get_google_service(user, 'drive', 'v3')
    if not service:
        return None

    try:
        logger.info(f"Downloading Drive file {file_id} for user {user.email}")
        request = service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.debug(f"Download {int(status.progress() * 100)}%.")
        logger.info(f"Successfully downloaded Drive file {file_id}")
        file_stream.seek(0) # Reset stream position to the beginning
        return file_stream
    except HttpError as error:
        # Handle specific errors like file not found (404) or permission denied (403)
        logger.error(f"API error downloading Drive file {file_id}: {error}")
        return None
    except Exception as e:
        logger.exception(f"Error downloading Drive file {file_id}")
        return None

def submit_assignment_work(user: User, course_id: str, assignment_id: str, file_path: str):
    """Placeholder: Submits a file as student work for an assignment."""
    # This requires more complex logic:
    # 1. Get the user's submission ID for the assignment.
    # 2. Upload the file (likely to Drive first, then attach).
    # 3. Modify the submission to attach the file.
    # 4. Turn in the submission.
    # Needs careful implementation using Classroom API's courses.courseWork.studentSubmissions methods.
    logger.warning(f"Placeholder: Submission logic for assignment {assignment_id} not fully implemented.")
    # Example structure:
    # classroom_service = get_google_service(user, 'classroom', 'v1')
    # drive_service = get_google_service(user, 'drive', 'v3')
    # if not classroom_service or not drive_service: return False
    # try:
    #     # Get submission ID
    #     submission = classroom_service.courses().courseWork().studentSubmissions().list(...).execute()
    #     submission_id = submission['studentSubmissions'][0]['id'] # Simplified
    #     # Upload file to Drive (consider a specific folder)
    #     # file_metadata = {'name': os.path.basename(file_path), 'parents': ['folder_id']}
    #     # media = MediaFileUpload(file_path, mimetype='application/pdf') # Determine mimetype
    #     # drive_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    #     # drive_file_id = drive_file.get('id')
    #     # Modify submission to add Drive file
    #     # modify_request = { 'addAttachments': [{'driveFile': {'id': drive_file_id}}] }
    #     # classroom_service.courses().courseWork().studentSubmissions().modifyAttachments(
    #     #     courseId=course_id, courseWorkId=assignment_id, id=submission_id, body=modify_request
    #     # ).execute()
    #     # Turn in the submission
    #     # classroom_service.courses().courseWork().studentSubmissions().turnIn(
    #     #     courseId=course_id, courseWorkId=assignment_id, id=submission_id, body={}
    #     # ).execute()
    #     logger.info(f"Placeholder: Successfully submitted work for assignment {assignment_id}")
    #     return True
    # except HttpError as error:
    #     logger.error(f"API error submitting assignment {assignment_id}: {error}")
    #     return False
    # except Exception as e:
    #     logger.exception(f"Error submitting assignment {assignment_id}")
    #     return False
    return True # Placeholder success
