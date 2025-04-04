import React, { useState, useEffect } from 'react';
import apiClient from '../../services/apiClient'; // Assuming apiClient is set up
import AssignmentListItem from './AssignmentListItem';
import LoadingSpinner from '../Common/LoadingSpinner';
import ErrorMessage from '../Common/ErrorMessage';

const AssignmentList = ({ courseId, onAssignmentSelect }) => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(false); // Start as false, load when courseId is valid
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!courseId) {
      setAssignments([]); // Clear assignments if no course is selected
      setLoading(false);
      return;
    }

    const fetchAssignments = async () => {
      try {
        setLoading(true);
        setError(null);
        // Placeholder: Replace with actual API call to fetch assignments for the course
        // const response = await apiClient.get(`/api/classroom/assignments/?course_id=${courseId}`);
        // Simulating API call
        await new Promise(resolve => setTimeout(resolve, 800)); // Simulate network delay
        const mockAssignments = [
          { id: 101, google_id: 'assign1', title: 'Essay on AI Ethics', status: 'DraftReady', materials_count: 2, processed_materials_count: 2, due_date: '2025-04-10T23:59:00Z' },
          { id: 102, google_id: 'assign2', title: 'React Component Design', status: 'New', materials_count: 1, processed_materials_count: 0, due_date: '2025-04-15T23:59:00Z' },
          { id: 103, google_id: 'assign3', title: 'Database Schema Design', status: 'Submitted', materials_count: 3, processed_materials_count: 3, due_date: '2025-04-05T23:59:00Z' },
        ].filter(a => a.status !== 'Submitted'); // Example: Filter out submitted
        
        setAssignments(mockAssignments);
        // setAssignments(response.data); // Use this line with actual API
      } catch (err) {
        console.error(`Error fetching assignments for course ${courseId}:`, err);
        setError('Failed to load assignments. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchAssignments();
  }, [courseId]); // Re-run effect when courseId changes

  if (loading) {
    return <LoadingSpinner text="Loading assignments..." />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!courseId) {
    return <p>Select a course to view assignments.</p>;
  }

  return (
    <div className="assignment-list-container">
      <h3>Assignments</h3>
      {assignments.length === 0 ? (
        <p>No unsubmitted assignments found for this course.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {assignments.map((assignment) => (
            <AssignmentListItem 
              key={assignment.id} 
              assignment={assignment} 
              onSelect={() => onAssignmentSelect(assignment.id)} // Pass assignment ID up
            />
          ))}
        </ul>
      )}
      {/* Placeholder for a sync button for this specific course */}
      <button onClick={() => alert(`Sync assignments for course ${courseId} - not implemented yet.`)}>Sync Assignments</button>
    </div>
  );
};

export default AssignmentList;
