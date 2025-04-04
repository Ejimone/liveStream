import React from 'react';

const AssignmentListItem = ({ assignment, onSelect }) => {
  // Basic styling for the list item
  const itemStyle = {
    border: '1px solid #eee',
    borderRadius: '4px',
    padding: '10px 15px',
    marginBottom: '8px',
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const statusStyle = {
    padding: '3px 8px',
    borderRadius: '10px',
    fontSize: '12px',
    fontWeight: 'bold',
    color: 'white',
    backgroundColor: '#6c757d' // Default gray
  };

  // Determine status color (example)
  switch (assignment.status) {
    case 'New':
      statusStyle.backgroundColor = '#0d6efd'; // Blue
      break;
    case 'Processing':
    case 'Syncing':
    case 'GeneratingDraft':
      statusStyle.backgroundColor = '#ffc107'; // Yellow
      statusStyle.color = 'black';
      break;
    case 'DraftReady':
      statusStyle.backgroundColor = '#198754'; // Green
      break;
    case 'Submitted':
      statusStyle.backgroundColor = '#6c757d'; // Gray
      break;
    case 'Error':
      statusStyle.backgroundColor = '#dc3545'; // Red
      break;
    default:
      break;
  }

  const handleMouseEnter = (e) => {
    e.currentTarget.style.backgroundColor = '#f8f9fa';
  };

  const handleMouseLeave = (e) => {
    e.currentTarget.style.backgroundColor = 'transparent';
  };

  const dueDate = assignment.due_date ? new Date(assignment.due_date).toLocaleDateString() : 'No due date';

  return (
    <li 
      style={itemStyle} 
      onClick={onSelect} 
      onMouseEnter={handleMouseEnter} 
      onMouseLeave={handleMouseLeave}
      title={`Click to view details for ${assignment.title}`}
    >
      <div>
        <strong>{assignment.title}</strong>
        <p style={{ fontSize: '14px', color: '#555', margin: '5px 0 0 0' }}>
          Due: {dueDate} | Materials: {assignment.materials_count} ({assignment.processed_materials_count} processed)
        </p>
      </div>
      <span style={statusStyle}>{assignment.status}</span>
    </li>
  );
};

export default AssignmentListItem;
