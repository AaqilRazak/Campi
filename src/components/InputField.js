import React from 'react';

const InputField = ({ type, name, value, onChange, placeholder, error }) => {
  return (
    <div className="input-field">
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={`${name}-error`}
      />
      {error && <span id={`${name}-error`} className="error-message">{error}</span>}
    </div>
  );
};

export default InputField;
