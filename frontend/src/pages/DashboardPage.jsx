import React, { useState, useEffect } from 'react';
import apiClient from '../services/apiClient';
import CourseList from '../components/Classroom/CourseList';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import ErrorMessage from '../components/Common/ErrorMessage';

const DashboardPage = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCourses = async () => {
            setLoading(true);
            setError(null);
            try {
                // Placeholder: Fetch courses from backend API
                console.log("Placeholder: Fetching courses from /api/classroom/courses/");
                // const response = await apiClient.get('/classroom/courses/');
                // setCourses(response.data.results || response.data); // Adjust based on pagination
                setCourses([
                    { id: 1, name: "Sample Course 101", description: "Intro course" },
                    { id: 2, name: "Advanced Topics 404", description: "Deep dive" }
                ]); // Dummy data
                await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay

            } catch (err) {
                console.error("Error fetching courses:", err);
                setError("Failed to load courses. Please try again later.");
            } finally {
                setLoading(false);
            }
        };

        fetchCourses();
    }, []);

    const handleSyncCourses = async () => {
        try {
             console.log("Placeholder: Calling POST /api/classroom/courses/sync/");
             // await apiClient.post('/classroom/courses/sync/');
             alert("Course sync initiated! Refresh the page in a moment.");
             // TODO: Implement better feedback mechanism (e.g., polling, websockets)
         } catch (err) {
             console.error("Error syncing courses:", err);
             alert("Failed to initiate course sync.");
         }
    };

    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorMessage message={error} />;

    return (
        <div>
            <h2>Your Courses</h2>
            <button onClick={handleSyncCourses} style={{marginBottom: '1rem'}}>Sync Courses from Google</button>
            <CourseList courses={courses} />
        </div>
    );
};

export default DashboardPage;