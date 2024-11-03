import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/LoginPage.css';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = (e) => {
    if (e) e.preventDefault();
    
    if (username === 'student' && password === 'password') {
      login({ username, role: 'student' });
      navigate('/chat', { replace: true });
    } else if (username === 'admin' && password === 'adminpass') {
      login({ username, role: 'admin' });
      navigate('/admin', { replace: true });
    } else {
      setError('Invalid username or password');
    }
  };

  return (
    <form onSubmit={handleLogin} className="login-page">
      <h1>Login to Campi</h1>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">Login</button>
      {error && <p className="error">{error}</p>}
    </form>
  );
};

export default LoginPage;
