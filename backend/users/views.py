import os
import logging
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework.authtoken.models import Token # Import DRF Token model
from rest_framework.decorators import action
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from .models import User, UserPreference
from .serializers import (
    UserProfileSerializer,
    UserPreferenceUpdateSerializer,
    UserPersonalInfoUpdateSerializer,
    UserPreferenceSerializer
)

logger = logging.getLogger(__name__)

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Initiates the Google OAuth 2.0 Authorization Code Flow.
        Redirects the user to Google's consent screen.
        """
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
             logger.error("Google OAuth Client ID or Secret not configured.")
             return Response({"error": "OAuth is not configured correctly."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Create Google OAuth Flow instance using settings
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        # Redirect URI must match exactly what's registered in Google Cloud Console
                        "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    }
                },
                scopes=settings.GOOGLE_SCOPES,
                redirect_uri=settings.GOOGLE_REDIRECT_URI
            )

            # Generate the authorization URL
            authorization_url, state = flow.authorization_url(
                access_type='offline',  # Request refresh token
                include_granted_scopes='true',
                prompt='consent' # Force consent screen for refresh token
            )

            # Store the state in the session to verify in the callback
            request.session['oauth_state'] = state
            logger.info(f"Redirecting user to Google for authentication. State: {state}")

            # Redirect user to Google's authorization URL
            # Instead of redirecting directly, return the URL for the frontend to handle
            # return redirect(authorization_url)
            return Response({"authorization_url": authorization_url}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Error initiating Google OAuth flow.")
            return Response({"error": "Failed to initiate Google login."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Handles the callback from Google after user authorization.
        Exchanges the authorization code for tokens, gets user info,
        creates/updates the user, stores tokens, generates a DRF token,
        and returns it to the frontend.
        """
        # 1. Verify state to prevent CSRF attacks
        state = request.GET.get('state')
        if not state or state != request.session.get('oauth_state'):
            logger.warning("OAuth state mismatch. Potential CSRF attack.")
            return Response({"error": "Invalid state parameter."}, status=status.HTTP_400_BAD_REQUEST)

        # Clear state from session
        request.session.pop('oauth_state', None)

        # 2. Get authorization code from request query params
        code = request.GET.get('code')
        if not code:
            logger.error("Authorization code not found in callback request.")
            return Response({"error": "Authorization code missing."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 3. Exchange authorization code for tokens using the Flow instance
            flow = Flow.from_client_config(
                 client_config={
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    }
                },
                scopes=settings.GOOGLE_SCOPES,
                redirect_uri=settings.GOOGLE_REDIRECT_URI
            )
            flow.fetch_token(code=code)
            google_credentials = flow.credentials # Contains access_token, refresh_token, etc.

            # 4. Get user info from Google using the credentials
            user_info = self.get_google_user_info(google_credentials)
            if not user_info or 'email' not in user_info:
                logger.error("Failed to fetch user info from Google.")
                return Response({"error": "Could not retrieve user information from Google."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            email = user_info['email']
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
            profile_picture = user_info.get('picture', '')
            # Use email prefix as username if username doesn't exist, ensure uniqueness
            username = email.split('@')[0]
            counter = 1
            while User.objects.filter(username=username).exists():
                 username = f"{email.split('@')[0]}{counter}"
                 counter += 1


            # 5. Find or create a User in your Django database
            user, created = User.objects.update_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'profile_picture': profile_picture,
                    'is_active': True, # Ensure user is active
                    # Store Google tokens securely (JSON serializable format)
                    'google_oauth_mocked_credentials': {
                        'token': google_credentials.token,
                        'refresh_token': google_credentials.refresh_token,
                        'token_uri': google_credentials.token_uri,
                        'client_id': google_credentials.client_id,
                        'client_secret': google_credentials.client_secret,
                        'scopes': google_credentials.scopes,
                        'expiry': google_credentials.expiry.isoformat() if google_credentials.expiry else None,
                    }
                }
            )
            logger.info(f"User {'created' if created else 'updated'}: {user.email}")
            
            # Create UserPreference if it doesn't exist
            if created:
                UserPreference.objects.create(user=user)

            # 6. Generate or retrieve DRF Auth Token for the user
            token, _ = Token.objects.get_or_create(user=user)
            logger.info(f"Generated DRF token for user {user.email}")

            # 7. Return the DRF token to the frontend
            # The frontend CallbackPage should handle this response
            return Response({
                "token": token.key,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profile_picture": user.profile_picture
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Error handling Google OAuth callback.")
            return Response({"error": "An error occurred during Google authentication."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_google_user_info(self, credentials):
        """Helper function to get user profile info from Google."""
        try:
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            return user_info
        except Exception as e:
            logger.exception("Error fetching user info from Google API.")
            return None

class LogoutView(APIView):
     permission_classes = [permissions.IsAuthenticated] # Must be logged in to log out

     def post(self, request, *args, **kwargs):
         """
         Logs the user out by deleting their DRF token.
         Optionally revokes the Google refresh token.
         """
         user = request.user
         try:
             # Delete the DRF token
             if hasattr(user, 'auth_token'):
                 user.auth_token.delete()
                 logger.info(f"Deleted DRF token for user {user.email}")

             # Optional: Revoke Google refresh token
             # This prevents the app from accessing Google data offline indefinitely
             # Consider if this is desired UX - user will need to re-authenticate next time
             # if user.google_oauth_mocked_credentials and 'refresh_token' in user.google_oauth_mocked_credentials:
             #     try:
             #         # Reconstruct credentials object (simplified)
             #         creds_data = user.google_oauth_mocked_credentials
             #         google_credentials = Credentials(
             #             token=creds_data.get('token'),
             #             refresh_token=creds_data.get('refresh_token'),
             #             token_uri=creds_data.get('token_uri'),
             #             client_id=creds_data.get('client_id'),
             #             client_secret=creds_data.get('client_secret'),
             #             scopes=creds_data.get('scopes')
             #         )
             #         revoke_request = GoogleRequest()
             #         google_credentials.revoke(revoke_request)
             #         logger.info(f"Revoked Google refresh token for user {user.email}")
             #         # Clear stored credentials after revocation
             #         user.google_oauth_mocked_credentials = None
             #         user.save(update_fields=['google_oauth_mocked_credentials'])
             #     except Exception as revoke_error:
             #         logger.error(f"Failed to revoke Google token for user {user.email}: {revoke_error}")
             #         # Don't fail logout if revocation fails, just log it

             return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
         except Exception as e:
             logger.exception(f"Error during logout for user {user.email}")
             return Response({"error": "Logout failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """API view to retrieve and update the user's profile."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        """Return the authenticated user."""
        # Ensure the UserPreference object exists
        UserPreference.objects.get_or_create(user=self.request.user)
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Override update to use more specific serializers based on the context."""
        update_type = request.data.get('update_type', 'personal')
        
        if update_type == 'preferences':
            serializer = UserPreferenceUpdateSerializer(request.user, data=request.data, partial=True)
        else:  # Default to personal info update
            serializer = UserPersonalInfoUpdateSerializer(request.user, data=request.data, partial=True)
            
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return full profile with updates
        return Response(UserProfileSerializer(request.user).data)

class UserPreferenceView(generics.RetrieveUpdateAPIView):
    """API view to retrieve and update the user's UI and feature preferences."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPreferenceSerializer
    
    def get_object(self):
        """Return the authenticated user's preference object."""
        obj, created = UserPreference.objects.get_or_create(user=self.request.user)
        return obj