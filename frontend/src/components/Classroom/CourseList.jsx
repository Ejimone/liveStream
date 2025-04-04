import React, { useState, useEffect } from 'react';
import apiClient from '../../services/apiClient'; // Assuming apiClient is set up
import CourseListItem from './CourseListItem';
import LoadingSpinner from '../Common/LoadingSpinner';
import ErrorMessage from '../Common/ErrorMessage';

const CourseList = ({ onCourseSelect }) => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        setError(null);
        // Placeholder: Replace with actual API call to fetch courses
        // const response = await apiClient.get('/api/classroom/courses/');
        // Simulating API call
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
        const mockCourses = [
          { id: 1, google_id: 'course123', name: 'Introduction to AI', assignments_count: 5, unsubmitted_assignments_count: 2 },
          { id: 2, google_id: 'course456', name: 'Web Development Basics', assignments_count: 10, unsubmitted_assignments_count: 1 },
          { id: 3, google_id: 'course789', name: 'Data Structures', assignments_count: 8, unsubmitted_assignments_count: 0 },
        ];
        setCourses(mockCourses);
        // setCourses(response.data); // Use this line with actual API
      } catch (err) {
        console.error("Error fetching courses:", err);
        setError('Failed to load courses. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, []);

  if (loading) {
    return <LoadingSpinner text="Loading courses..." />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="course-list-container">
      <h2>Your Google Classroom Courses</h2>
      {courses.length === 0 ? (
        <p>No courses found or you haven't synced yet.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {courses.map((course) => (
            <CourseListItem 
              key={course.id} 
              course={course} 
              onSelect={() => onCourseSelect(course.id)} // Pass course ID up
            />
          ))}
        </ul>
      )}
      {/* Placeholder for a sync button */}
      <button onClick={() => alert('Sync functionality not implemented yet.')}>Sync Courses</button>
    </div>
  );
};

export default CourseList;
