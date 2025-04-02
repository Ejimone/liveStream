Project Title: mrAssistant

Version: 1.0

Date: April 2, 2025

1. Introduction & Vision

Vision: To create a personal AI assistant ("Classroom Copilot") that significantly reduces the manual effort involved in managing Google Classroom assignments while providing helpful agent capabilities, always keeping the student (user) in control of the final output.
Goal: Develop a web application using Django (backend) and React (frontend) that integrates with Google Classroom, leverages the Gemini API for content generation/processing, and provides agent features like email and web search, all within a modular architecture.
Target User: Students using Google Classroom who want assistance with organizing, drafting, and managing assignment workflows and related tasks.
Core Principle: User Control. The AI assists by generating drafts and automating uploads/downloads, but the user must review, edit, and approve all AI-generated content (assignment solutions, emails) before submission or sending. The tool is for assistance and efficiency, not academic dishonesty.
2. Functional Requirements

2.1 User Authentication & Authorization:
Secure user registration and login system (Django's built-in auth).
OAuth 2.0 flow for securely connecting the user's Google Account (specifically requesting scopes for Google Classroom, Google Drive, and Gmail API access).
Store Google API tokens securely, associated with the user account, handling token refresh.
2.2 Google Classroom Integration Module:
Course Listing: Display a list of the user's Google Classroom courses.
Assignment Fetching: Periodically (or on-demand) check for new assignments in selected courses using the Google Classroom API.
Material Downloading: Automatically download assignment instructions and attached materials (PDFs, Google Docs, Slides etc.) using Google Drive API (if materials are stored there) or Classroom API links. Store locally or reference cloud storage.
Material Processing: Extract text content from downloaded materials (PDFs, Docs). Handle different file types gracefully.
AI-Powered Solution Drafting (Gemini API):
Send processed assignment instructions and relevant material content to the Gemini API (e.g., gemini-pro).
Use carefully crafted prompts to instruct Gemini to generate a draft solution, outline, summary, or answer based on the requirements. Prompts should emphasize generating helpful starting points, not final submissions.
Handle Gemini API responses, including potential errors or refusals based on safety settings.
User Review & Editing Interface:
Present the fetched assignment details and the AI-generated draft solution in a user-friendly text editor within the React frontend.
Allow the user to extensively modify, rewrite, or completely replace the AI draft.
Finalization & PDF Conversion:
Once the user approves the final solution, convert the edited text content into a PDF document. Use a reliable Python library (e.g., xhtml2pdf, ReportLab).
Automated Submission: Upload the generated PDF to the correct Google Classroom assignment as student work using the Classroom API.
2.3 Agent Module:
Real-time Notifications:
In-app notifications for newly detected assignments, successful submissions, or errors.
(Optional) Email notifications for critical events.
Email Assistant:
Interface to draft emails (e.g., to teachers, project partners).
Use Gemini API to help draft email content based on user prompts (e.g., "Draft an email asking the teacher for clarification on assignment X").
Mandatory User Review: Display the AI-drafted email in an editor for user review, modification, and explicit approval before sending.
Send emails using the Gmail API via the user's connected account.
Web Search Integration:
Provide an interface to perform web searches (using an API like Google Custom Search JSON API or scraping responsibly).
(Optional) Use Gemini to summarize search results relevant to an assignment topic.
Information Retrieval (Weather):
Fetch and display current weather updates based on user's location (requires location permission or manual input) using a Weather API (e.g., OpenWeatherMap).
2.4 User Settings:
Manage connected Google Account.
Select courses to monitor.
Configure notification preferences.
Manage API Keys (if applicable, though OAuth is preferred for Google services).
3. Non-Functional Requirements

3.1 Security:
Secure handling of Google API OAuth tokens (encryption at rest, secure transmission).
Secure storage of Gemini API key (if applicable, ideally configured via environment variables, not stored in DB).
Protection against common web vulnerabilities (XSS, CSRF - Django provides built-in protection).
Input validation for all user-provided data and API interactions.
Rate limiting for API calls (Google APIs, Gemini, Weather, Search).
3.2 Performance:
Responsive UI.
Efficient background processing for checking assignments and processing materials (using Celery or Django-Q).
Optimize database queries.
3.3 Scalability:
Modular architecture allows for independent scaling of components if needed later (though initially likely a modular monolith).
Consider database connection pooling.
3.4 Usability:
Intuitive user interface, especially for the review/edit steps.
Clear feedback on background processes (downloading, generating, uploading).
Robust error handling and informative error messages.
3.5 Maintainability:
Clean, well-commented code.
Adherence to Django and React best practices.
Modular design (separate Django apps, distinct React components).
Unit and integration tests.
4. Technology Stack

Backend Framework: Python 3.x / Django 4.x or later
Frontend Library: JavaScript / React.js 18.x or later (with Create React App or Vite)
Database: PostgreSQL (Reliable, works well with Django)
AI Model API: Google Gemini API (e.g., gemini-pro via Python client library)
Background Tasks: Celery with Redis or RabbitMQ (for asynchronous tasks like API polling, processing)
PDF Generation: xhtml2pdf or ReportLab (Python libraries)
API Clients:
google-api-python-client (for Classroom, Drive, Gmail)
google-generativeai (for Gemini)
Requests library (for Weather/Search APIs if needed)
Deployment: Docker / Docker Compose
CSS Framework (Optional): Tailwind CSS, Material UI, or Bootstrap for faster UI development.
5. Architecture

Style: Modular Monolith (initially). A single Django project containing multiple specialized apps. Frontend is a separate React SPA.
Backend (Django Apps):
users: Manages user accounts, profiles, Google OAuth tokens.
classroom_integration: Handles Classroom API interactions, fetching courses/assignments, managing materials.
ai_processing: Interfaces with Gemini API, manages prompts, processes AI responses, handles PDF generation.
agent_services: Implements email drafting/sending (Gmail API), web search, weather updates.
core: Common utilities, base models, settings.
Frontend (React Components):
Auth: Login/Registration pages, Google Sign-in button.
Dashboard: Main view after login.
CourseList: Displays Classroom courses.
AssignmentView: Displays assignments for a course, shows status (New, Processing, Draft Ready, Submitted).
AssignmentDetail: Shows assignment instructions, materials, AI draft editor, final review, submit button.
EmailAssistant: UI for drafting, reviewing, sending emails.
AgentWidgets: Components for Weather, Search.
Notifications: Displays system messages.
Settings: User settings management.
API Layer: Django Rest Framework (DRF) to create RESTful APIs for communication between the React frontend and Django backend.
Data Flow (Classroom Automation Example):
Celery Task (scheduled/triggered) -> classroom_integration polls Classroom API for new assignments.
If new assignment found -> classroom_integration downloads materials (using Drive/Classroom API).
Task triggers ai_processing -> Sends content to Gemini API.
Gemini Response received -> Stored, associated with the assignment (DB update). Status changes to "Draft Ready".
Frontend polls backend API or receives WebSocket notification -> AssignmentView updates status.
User clicks assignment -> AssignmentDetail fetches data via API -> Displays instructions, AI draft in editor.
User edits/approves -> Frontend sends final content to backend API.
ai_processing receives final content -> Generates PDF.
classroom_integration uploads PDF to Classroom API.
DB status updated to "Submitted". Frontend notified.
6. Data Model (Simplified PostgreSQL Schema)

User: Django's built-in User model.
UserProfile: OneToOneField to User, stores Google OAuth tokens (encrypted), settings.
Course: Stores Classroom course ID, name, user association.
Assignment: Stores Classroom assignment ID, course link, title, description, due date, status (new, processing, draft_ready, reviewing, generating_pdf, uploading, submitted, error).
AssignmentMaterial: Links to Assignment, stores material details (name, type, download link/ID).
AssignmentDraft: Links to Assignment, stores AI-generated draft content, final user-edited content.
EmailDraft: Stores user prompt, AI draft, final content, recipient, status (draft, reviewing, sent, error).
7. API Integration Details

Google APIs (Classroom, Drive, Gmail): Use OAuth 2.0 (Authorization Code Flow). Store refresh tokens securely. Handle scope approvals. Use official Google Python client libraries. Implement error handling for API limits, permission issues.
Gemini API: Use the official google-generativeai Python library. Securely manage the API key (Environment Variable). Design robust prompts. Implement content safety handling. Be mindful of input/output token limits.
Weather/Search APIs: Use standard REST API calls with API keys (securely managed). Handle rate limits.
8. UI/UX Considerations

Clear visual distinction between AI-generated drafts and user edits.
Prominent "Review and Edit" steps are mandatory before any submission or sending.
Status indicators for background tasks (e.g., "Downloading materials...", "Generating draft...", "Uploading...").
Easy access to original assignment instructions and materials within the review interface.
Non-blocking UI during background operations.
9. Development & Deployment

Methodology: Agile approach recommended (iterative development).
Testing: Unit tests (Django test framework, Jest/React Testing Library), Integration tests (testing API flows, module interactions).
Version Control: Git (e.g., GitHub, GitLab).
Containerization: Dockerfile for backend, Dockerfile for frontend, Docker Compose to orchestrate services (Django, React, PostgreSQL, Redis).
Environment Variables: Manage sensitive keys (API keys, SECRET_KEY, DB credentials) and settings.
10. Security Plan

Regularly update dependencies.
Implement CSRF protection (Django default).
Use HTTPS.
Validate all inputs (frontend and backend).
Secure file uploads (if applicable beyond Google Drive).
Principle of Least Privilege for API scopes.
Sanitize outputs to prevent XSS.
Store sensitive data (OAuth tokens) encrypted at rest.
11. Future Enhancements

Support for more Google Workspace tools (Calendar, Tasks).
More sophisticated AI features (e.g., comparing draft to rubric, plagiarism checking hints - ethically).
Team/collaboration features.
Mobile application.
Advanced analytics on study habits (with user permission).