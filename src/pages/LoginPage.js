import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { login } from '../api/auth';
import '../styles/LoginPage.css';

const LoadingSpinner = () => (
    <div className="spinner"></div>
);

const LoginPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [rememberMe, setRememberMe] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { login: authLogin } = useAuth();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const response = await login(username, password);
            
            // Handle remember me
            if (rememberMe) {
                localStorage.setItem('rememberMe', 'true');
                localStorage.setItem('savedUsername', username);
            } else {
                localStorage.removeItem('rememberMe');
                localStorage.removeItem('savedUsername');
            }

            authLogin(response.user);

            // Navigate based on user role
            switch (response.user.role) {
                case 'admin':
                    navigate('/admin');
                    break;
                case 'student':
                    navigate('/chat');
                    break;
                default:
                    navigate('/chat');
            }
        } catch (err) {
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
            <form onSubmit={handleLogin}>
                <div className="form-group">
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Username"
                        disabled={isLoading}
                    />
                </div>

                <div className="form-group">
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                        disabled={isLoading}
                    />
                </div>

                <div className="remember-me">
                    <input
                        type="checkbox"
                        id="rememberMe"
                        checked={rememberMe}
                        onChange={(e) => setRememberMe(e.target.checked)}
                        disabled={isLoading}
                    />
                    <label htmlFor="rememberMe">Remember me</label>
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
