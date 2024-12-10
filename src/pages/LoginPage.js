import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/LoginPage.css';

const LoginPage = () => {
    const [credentials, setCredentials] = useState({
        username: '',
        password: '',
        rememberMe: false
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { login: authLogin } = useAuth();

    const handleChange = (e) => {
        const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
        setCredentials({
            ...credentials,
            [e.target.name]: value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            console.log('Login attempt with:', {
                username: credentials.username,
                password: credentials.password
            });

            const response = await fetch('http://localhost:8000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: credentials.username,
                    password: credentials.password
                })
            });

            console.log('Response status:', response.status);
            
            // Get the response body as text first
            const responseText = await response.text();
            console.log('Raw response:', responseText);

            let userData;
            try {
                userData = JSON.parse(responseText);
            } catch (parseError) {
                console.error('Error parsing response:', parseError);
                throw new Error('Invalid server response');
            }

            if (!response.ok) {
                console.error('Login failed:', userData);
                throw new Error(userData.detail || 'Login failed');
            }

            console.log('Login successful:', userData);
            authLogin(userData);
            navigate(userData.role === 'admin' ? '/admin' : '/chat');
        } catch (err) {
            console.error('Login error:', err);
            setError(err.message || 'Invalid username or password');
        } finally {
            setIsLoading(false);
        }
    };

    const handleGuestLogin = async () => {
        try {
            const response = await fetch('http://localhost:8000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: 'guest',
                    password: 'pass'
                })
            });

            if (!response.ok) {
                throw new Error('Guest login failed');
            }

            const userData = await response.json();
            authLogin(userData);
            navigate('/chat');
        } catch (err) {
            setError('Guest login failed');
        }
    };

    return (
        <div className="login-container">
            <h1>Login to Campi</h1>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <input
                        type="text"
                        name="username"
                        value={credentials.username}
                        onChange={handleChange}
                        placeholder="Username"
                        disabled={isLoading}
                    />
                </div>

                <div className="form-group">
                    <input
                        type="password"
                        name="password"
                        value={credentials.password}
                        onChange={handleChange}
                        placeholder="Password"
                        disabled={isLoading}
                    />
                </div>

                {error && <div className="error-message">{error}</div>}

                <div className="remember-me">
                    <input
                        type="checkbox"
                        name="rememberMe"
                        checked={credentials.rememberMe}
                        onChange={handleChange}
                        disabled={isLoading}
                    />
                    <label>Remember me</label>
                </div>

                <button 
                    type="submit" 
                    className="login-button"
                    disabled={isLoading}
                >
                    {isLoading ? 'Logging in...' : 'Login'}
                </button>

                <div className="divider">
                    <span>or</span>
                </div>

                <button
                    type="button"
                    onClick={handleGuestLogin}
                    className="guest-button"
                    disabled={isLoading}
                >
                    Continue as Guest
                </button>
            </form>
        </div>
    );
};

export default LoginPage;