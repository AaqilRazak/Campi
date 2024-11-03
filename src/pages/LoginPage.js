import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/LoginPage.css';

const LoadingSpinner = () => (
  <div className="spinner"></div>
);

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
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

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    setIsLoading(true);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (username === 'student' && password === 'password') {
        login({ username, role: 'student', rememberMe });
        navigate('/chat', { replace: true });
      } else if (username === 'admin' && password === 'adminpass') {
        login({ username, role: 'admin', rememberMe });
        navigate('/admin', { replace: true });
      } else {
        setErrors({ auth: 'Invalid username or password' });
      }
    } catch (error) {
      setErrors({ auth: 'Login failed. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGuestLogin = () => {
    login({ username: 'Guest', role: 'guest' });
    navigate('/chat', { replace: true });
  };

  return (
    <div className="login-page">
      <h1>Login to Campi</h1>
      <form onSubmit={handleLogin} className="login-form">
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
            disabled={isLoading}
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
            disabled={isLoading}
          />
          {errors.password && <span className="error-message">{errors.password}</span>}
        </div>

        <div className="remember-me">
          <label>
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              disabled={isLoading}
            />
            <span>Remember me</span>
          </label>
        </div>
        
        <button 
          type="submit" 
          className="login-button"
          disabled={isLoading}
        >
          {isLoading ? <LoadingSpinner /> : 'Login'}
        </button>
        {errors.auth && <p className="error-message">{errors.auth}</p>}
      </form>

      <div className="guest-section">
        <p className="or-divider">or</p>
        <button 
          onClick={handleGuestLogin} 
          className="guest-button"
          disabled={isLoading}
        >
          Continue as Guest
        </button>
      </div>
    </div>
  );
};

export default LoginPage;
