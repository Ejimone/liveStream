frontend/
|-- public/
|   |-- vite.svg
|   |-- ... (other static assets)
|
|-- src/
|   |-- assets/
|   |   |-- react.svg
|   |
|   |-- components/
|   |   |-- Auth/
|   |   |   |-- GoogleLoginButton.jsx
|   |   |
|   |   |-- Classroom/
|   |   |   |-- CourseList.jsx
|   |   |   |-- CourseListItem.jsx
|   |   |   |-- AssignmentList.jsx
|   |   |   |-- AssignmentListItem.jsx
|   |   |   |-- AssignmentDetail.jsx
|   |   |   |-- AssignmentDraftReview.jsx
|   |   |
|   |   |-- Common/
|   |   |   |-- LoadingSpinner.jsx
|   |   |   |-- ErrorMessage.jsx
|   |   |   |-- NavBar.jsx
|   |
|   |-- contexts/ # Optional: For global state (Auth, User)
|   |   |-- AuthContext.jsx
|   |
|   |-- hooks/ # Optional: For custom hooks
|   |   |-- useAuth.js
|   |   |-- useApi.js
|   |
|   |-- pages/ # Top-level views corresponding to routes
|   |   |-- LoginPage.jsx
|   |   |-- DashboardPage.jsx
|   |   |-- CourseDetailPage.jsx
|   |   |-- AssignmentPage.jsx
|   |   |-- CallbackPage.jsx # Handles OAuth redirect
|   |
|   |-- services/
|   |   |-- apiClient.js # Axios instance and API call functions
|   |
|   |-- App.jsx # Main application component with routing
|   |-- index.css # Global styles
|   |-- main.jsx # Entry point, renders App
|
|-- .env.example # Frontend specific env vars (like API URL)
|-- .gitignore
|-- Dockerfile # Frontend Dockerfile
|-- index.html # Root HTML file
|-- package.json