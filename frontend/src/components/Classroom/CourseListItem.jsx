import React from 'react';

const CourseListItem = ({ course, onSelect }) => {
  // Basic styling for the list item
  const itemStyle = {
    border: '1px solid #ccc',
    borderRadius: '4px',
    padding: '15px',
    marginBottom: '10px',
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
  };

  const handleMouseEnter = (e) => {
    e.currentTarget.style.backgroundColor = '#f0f0f0';
  };

  const handleMouseLeave = (e) => {
    e.currentTarget.style.backgroundColor = 'transparent';
  };

  return (
    <li 
      style={itemStyle} 
      onClick={onSelect} 
      onMouseEnter={handleMouseEnter} 
      onMouseLeave={handleMouseLeave}
      title={`Click to view assignments for ${course.name}`}
    >
      <h3>{course.name}</h3>
      <p>
        Assignments: {course.assignments_count} 
        (Unsubmitted: {course.unsubmitted_assignments_count})
      </p>
      {/* Placeholder for last synced time */}
      {/* <p><small>Last Synced: {course.last_synced ? new Date(course.last_synced).toLocaleString() : 'Never'}</small></p> */}
    </li>
  );
};

export default CourseListItem;
