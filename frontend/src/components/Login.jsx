import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';

/**
 * Login component handling Google OAuth authentication
 */
const Login = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get authorization URL from backend
      const authUrl = await authService.initiateGoogleLogin();
      
      // Redirect to Google's OAuth page
      window.location.href = authUrl;
    } catch (error) {
      console.error('Login error:', error);
      setError('Failed to initiate login. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Welcome to Classroom Copilot</h2>
        <p>Your AI assistant for Google Classroom</p>
        
        <button 
          onClick={handleGoogleLogin}
          disabled={loading}
          className="google-login-button"
        >
          {loading ? 'Loading...' : 'Login with Google'}
        </button>
        
        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
};

export default Login;