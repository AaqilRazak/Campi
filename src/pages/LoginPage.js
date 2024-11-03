import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/LoginPage.css';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();
  const { login } = useAuth();

  const validateForm = () => {
    const newErrors = {};
    
    if (!username.trim()) {
      newErrors.username = 'Username is required';
    }
    if (!password.trim()) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    if (username === 'student' && password === 'password') {
      login({ username, role: 'student' });
      navigate('/chat', { replace: true });
    } else if (username === 'admin' && password === 'adminpass') {
      login({ username, role: 'admin' });
      navigate('/admin', { replace: true });
    } else {
      setErrors({ auth: 'Invalid username or password' });
    }
  };

  return (
    <form onSubmit={handleLogin} className="login-page">
      <h1>Login to Campi</h1>
      <div className="input-group">
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => {
            setUsername(e.target.value);
            if (errors.username) {
              setErrors(prev => ({ ...prev, username: '' }));
            }
          }}
          className={errors.username ? 'error-input' : ''}
        />
        {errors.username && <span className="error-message">{errors.username}</span>}
      </div>
      
      <div className="input-group">
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            if (errors.password) {
              setErrors(prev => ({ ...prev, password: '' }));
            }
          }}
          className={errors.password ? 'error-input' : ''}
        />
        {errors.password && <span className="error-message">{errors.password}</span>}
      </div>
      
      <button type="submit">Login</button>
      {errors.auth && <p className="error-message">{errors.auth}</p>}
    </form>
  );
};

export default LoginPage;
