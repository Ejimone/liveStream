import axios from 'axios';

// Determine the API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor to add the auth token to requests if available
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authToken'); // Or get from context/state management
        if (token) {
            config.headers['Authorization'] = `Token ${token}`; // Adjust if using JWT (Bearer)
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor to handle common responses/errors (e.g., 401 Unauthorized)
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response && error.response.status === 401) {
            // Handle unauthorized access, e.g., redirect to login
            console.error("Unauthorized access - Redirecting to login");
            localStorage.removeItem('authToken'); // Clear invalid token
            // Avoid infinite loop if login page itself causes 401
            if (window.location.pathname !== '/login') {
                 window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);


// Placeholder functions for specific API calls:

// Auth
export const googleLogin = () => apiClient.get('/auth/google/login/'); // Backend handles redirect
// Handle callback logic will likely be in CallbackPage.jsx, exchanging code for token
export const logoutUser = () => apiClient.post('/auth/logout/');

// Classroom
export const fetchCourses = () => apiClient.get('/classroom/courses/');
export const syncCourses = () => apiClient.post('/classroom/courses/sync/');
export const fetchAssignments = (courseId) => apiClient.get(`/classroom/courses/${courseId}/assignments/`);
export const fetchAssignmentDetails = (assignmentId) => apiClient.get(`/classroom/assignments/${assignmentId}/`); // Assuming separate endpoint
export const syncAssignmentMaterials = (assignmentId) => apiClient.post(`/classroom/assignments/${assignmentId}/sync-materials/`);
export const submitAssignment = (assignmentId, draftId) => apiClient.post(`/classroom/assignments/${assignmentId}/submit/`, { draft_id: draftId });

// AI Processing
export const generateDraft = (assignmentId) => apiClient.post(`/ai/assignments/${assignmentId}/generate-draft/`);
export const fetchDraft = (draftId) => apiClient.get(`/ai/drafts/${draftId}/review/`); // Endpoint TBD
export const reviewDraft = (draftId, edits) => apiClient.patch(`/ai/drafts/${draftId}/review/`, edits ); // Endpoint TBD


export default apiClient;