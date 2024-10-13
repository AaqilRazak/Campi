import React from 'react';

const ErrorMessage = ({ message }) => {
  return <div className="error-message" role="alert">{message}</div>;
};

export default ErrorMessage;
