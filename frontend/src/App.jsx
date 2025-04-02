import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import NavBar from './components/Common/NavBar';
import LoginPage from './pages/LoginPage';
import DashboardPage from "./pages/DashboardPage";
import CourseDetailPage from './pages/CourseDetailPage';
import AssignmentPage from './pages/AssignmentPage';
import CallbackPage from './pages/CallbackPage'; // Handles OAuth redirect
// import { AuthProvider, useAuth } from './contexts/AuthContext'; // Example using Context

// Placeholder for authentication check
const isAuthenticated = () => {
    // Replace with actual logic (e.g., check context, local storage for token)
    return localStorage.getItem('authToken') !== null;
};

// Wrapper for protected routes
const ProtectedRoute = ({ children }) => {
    if (!isAuthenticated()) {
        // Redirect them to the /login page, but save the current location they were
        // trying to go to when they were redirected. This allows us to send them
        // along to that page after they login, which is a nicer user experience
        // than dropping them off on the home page.
        return <Navigate to="/login" replace />;
    }
    return children;
};


function App() {
    return (
        // <AuthProvider> {/* Wrap with AuthProvider if using Context */}
            <Router>
                <NavBar />
                <div style={{ padding: '20px' }}> {/* Basic layout padding */}
                    <Routes>
                        {/* Public Routes */}
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/auth/google/callback" element={<CallbackPage />} /> {/* Handle callback */}

                        {/* Protected Routes */}
                        <Route
                            path="/dashboard"
                            element={<ProtectedRoute><DashboardPage /></ProtectedRoute>}
                        />
                        <Route
                            path="/courses/:courseId"
                            element={<ProtectedRoute><CourseDetailPage /></ProtectedRoute>}
                        />
                        <Route
                            path="/assignments/:assignmentId" // Maybe nest under course? /courses/:courseId/assignments/:assignmentId
                            element={<ProtectedRoute><AssignmentPage /></ProtectedRoute>}
                        />

                        {/* Default Route */}
                        <Route
                            path="/"
                            element={isAuthenticated() ? <Navigate to="/dashboard" /> : <Navigate to="/login" />}
                        />

                         {/* Add 404 Not Found Route */}
                         <Route path="*" element={<div>404 Not Found</div>} />
                    </Routes>
                </div>
            </Router>
        // </AuthProvider>
    );
}

export default App;