import React from 'react';
import apiClient from '../../services/apiClient'; // Assuming apiClient handles base URL etc.

const GoogleLoginButton = () => {
    const handleLogin = async () => {
        try {
            // Option 1: Redirect based on backend response
            // const response = await apiClient.get('/auth/google/login/');
            // if (response.data.authorization_url) {
            //     window.location.href = response.data.authorization_url;
            // }

            // Option 2: Directly construct the URL (less secure for client_id)
            // Better to get it from backend to hide client_id if possible
            console.log("Placeholder: Redirecting to backend /api/auth/google/login/ which handles OAuth flow");
            window.location.href = `${apiClient.defaults.baseURL}/auth/google/login/`; // Adjust if baseURL isn't set right

        } catch (error) {
            console.error("Error initiating Google Login:", error);
            // TODO: Show error message to user
        }
    };

    return (
        <button onClick={handleLogin}>
            Login with Google
        </button>
    );
};

export default GoogleLoginButton;