import React from 'react';

const GoogleLoginButton = ({ onLoginClick }) => {
  // Basic button styling (can be replaced with a proper UI library button)
  const buttonStyle = {
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer',
    backgroundColor: '#4285F4', // Google blue
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  };

  // Placeholder for Google icon (replace with actual SVG or icon component)
  const googleIcon = (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M17.64 9.20455C17.64 8.56636 17.5827 7.95273 17.4764 7.36364H9V10.845H13.8436C13.635 11.97 13.0009 12.9232 12.0477 13.5614V15.8195H14.9564C16.6582 14.2527 17.64 11.9455 17.64 9.20455Z" fill="#4285F4"/>
      <path d="M9 18C11.43 18 13.4673 17.1941 14.9564 15.8195L12.0477 13.5614C11.2418 14.1014 10.2109 14.4205 9 14.4205C6.96273 14.4205 5.22091 13.0177 4.52182 11.1805H1.51773V13.5077C3.00682 16.2486 5.79773 18 9 18Z" fill="#34A853"/>
      <path d="M4.52182 11.1805C4.33636 10.6405 4.23 10.0614 4.23 9.45C4.23 8.83864 4.33636 8.25955 4.52182 7.71955V5.39227H1.51773C0.949091 6.48682 0.6 7.71136 0.6 9.00045C0.6 10.2895 0.949091 11.5141 1.51773 12.6086L4.52182 11.1805Z" fill="#FBBC05"/>
      <path d="M9 3.57955C10.3214 3.57955 11.5077 4.03364 12.4786 4.95818L15.0218 2.415C13.4673 0.925909 11.43 0 9 0C5.79773 0 3.00682 1.75136 1.51773 4.49227L4.52182 6.81955C5.22091 4.98227 6.96273 3.57955 9 3.57955Z" fill="#EA4335"/>
    </svg>
  );

  return (
    <button style={buttonStyle} onClick={onLoginClick}>
      {googleIcon}
      Sign in with Google
    </button>
  );
};

export default GoogleLoginButton;