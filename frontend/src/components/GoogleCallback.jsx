import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import authService from '../services/authService';

/**
 * Component to handle the Google OAuth callback
 * This component processes the code and state parameters from Google's redirect
 */
const GoogleCallback = () => {
  const [status, setStatus] = useState('Processing login...');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const processCallback = async () => {
      // Get URL search params
      const params = new URLSearchParams(location.search);
      const code = params.get('code');
      const state = params.get('state');
      
      // Validate params
      if (!code || !state) {
        setStatus('Error: Missing authentication parameters');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }
      
      try {
        // Process the callback with our backend
        await authService.handleGoogleCallback(code, state);
        
        setStatus('Login successful! Redirecting to dashboard...');
        setTimeout(() => navigate('/dashboard'), 1500);
      } catch (error) {
        console.error('Authentication error:', error);
        setStatus('Authentication failed. Redirecting to login...');
        setTimeout(() => navigate('/login'), 3000);
      }
    };
    
    processCallback();
  }, [location, navigate]);
  
  return (
    <div className="callback-container">
      <div className="callback-card">
        <h2>{status}</h2>
        <div className="loading-spinner"></div>
      </div>
    </div>
  );
};

export default GoogleCallback;