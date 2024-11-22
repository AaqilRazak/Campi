import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthService from '../services/auth.service';
import '../styles/LoginPage.css';

const LoadingSpinner = () => (
    <div className="spinner"></div>
);

const LoginPage = () => {
    const [credentials, setCredentials] = useState({
        username: '',
        password: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { login: authLogin } = useAuth();

    const handleChange = (e) => {
        setCredentials({
            ...credentials,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const response = await AuthService.login(credentials.username, credentials.password);
            console.log('Login response:', response);
            
            if (response.success) {
                const userData = {
                    id: response.debug?.received_data?.username || 0,
                    username: credentials.username,
                    role: credentials.username === 'admin' ? 'admin' : 'student',
                    firstName: response.debug?.received_data?.username || 'Test',
                    lastName: 'User'
                };
                authLogin(userData);
                navigate(userData.role === 'admin' ? '/admin' : '/chat');
            } else {
                setError(response.message || 'Login failed');
            }
        } catch (err) {
            console.error('Login error:', err);
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleGuestLogin = () => {
        authLogin({ 
            id: 0,
            username: 'guest',
            role: 'guest',
            firstName: 'Guest',
            lastName: 'User'
        });
        navigate('/chat');
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

                <button type="submit" className="login-button" disabled={isLoading}>
                    {isLoading ? <LoadingSpinner /> : 'Login'}
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
