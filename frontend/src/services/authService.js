import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const authService = {
  /**
   * Get Google OAuth URL
   * @returns {Promise<string>} The Google OAuth URL
   */
  getGoogleAuthUrl: async () => {
    try {
      const response = await axios.get(`${API_URL}/users/google-login/`);
      return response.data.authorization_url;
    } catch (error) {
      console.error('Error getting Google auth URL:', error);
      throw error;
    }
  },

  /**
   * Exchange code for tokens
   * @param {string} code - Authorization code from Google
   * @param {string} state - State parameter for CSRF protection
   * @returns {Promise<Object>} User data and tokens
   */
  handleGoogleCallback: async (code, state) => {
    try {
      const response = await axios.post(`${API_URL}/users/google-callback/`, {
        code,
        state,
      });
      
      // Store token in localStorage
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      return response.data;
    } catch (error) {
      console.error('Error during Google callback:', error);
      throw error;
    }
  },

  /**
   * Check if user is authenticated
   * @returns {boolean} True if authenticated
   */
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    return !!token;
  },

  /**
   * Get current user
   * @returns {Object|null} User object or null
   */
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Get authentication token
   * @returns {string|null} Token or null
   */
  getToken: () => {
    return localStorage.getItem('token');
  },

  /**
   * Logout user
   */
  logout: async () => {
    try {
      const token = authService.getToken();
      if (token) {
        await axios.post(
          `${API_URL}/users/logout/`, 
          {}, 
          { headers: { Authorization: `Token ${token}` } }
        );
      }
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      // Clear local storage regardless of server response
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }
};

// Add axios interceptor to handle token in requests
axios.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default authService;