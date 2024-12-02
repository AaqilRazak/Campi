import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthService from '../services/auth.service';
import '../styles/LoginPage.css';

const LoginPage = () => {
    const [credentials, setCredentials] = useState({
        username: '',
        password: '',
        rememberMe: false
    });
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { login: authLogin } = useAuth();

    const handleChange = (e) => {
        const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
        setCredentials({
            ...credentials,
            [e.target.name]: value
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        let userData;

        switch (credentials.password) {
            case 'studentpass':
                userData = {
                    id: 1,
                    username: credentials.username || 'student',
                    role: 'student',
                    firstName: 'Student',
                    lastName: 'User'
                };
                break;
            case 'adminpass':
                userData = {
                    id: 2,
                    username: credentials.username || 'admin',
                    role: 'admin',
                    firstName: 'Admin',
                    lastName: 'User'
                };
                break;
            case 'pass':
                userData = {
                    id: 3,
                    username: 'guest',
                    role: 'guest',
                    firstName: 'Guest',
                    lastName: 'User'
                };
                break;
            default:
                setError('Invalid password');
                return;
        }

        authLogin(userData);
        navigate(userData.role === 'admin' ? '/admin' : '/chat');
    };

    const handleGuestLogin = () => {
        authLogin({ 
            id: 3,
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
                    />
                </div>

                <div className="form-group">
                    <input
                        type="password"
                        name="password"
                        value={credentials.password}
                        onChange={handleChange}
                        placeholder="Password"
                    />
                </div>

                {error && <div className="error-message">{error}</div>}

                <div className="remember-me">
                    <input
                        type="checkbox"
                        name="rememberMe"
                        checked={credentials.rememberMe}
                        onChange={handleChange}
                    />
                    <label>Remember me</label>
                </div>

                <button type="submit" className="login-button">
                    Login
                </button>

                <div className="divider">
                    <span>or</span>
                </div>

                <button
                    type="button"
                    onClick={handleGuestLogin}
                    className="guest-button"
                >
                    Continue as Guest
                </button>
            </form>
        </div>
    );
};

export default LoginPage;