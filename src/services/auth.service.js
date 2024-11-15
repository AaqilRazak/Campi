// Direct URL to teammate's API
const API_URL = 'http://69.215.107.194/campi-api/api';

// Handles all authentication-related API calls
class AuthService {
    // Login method that communicates with backend
    async login(username, password) {
        try {
            // Send POST request to backend
            const response = await fetch(`${API_URL}/auth.php?action=login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Store user data locally if login successful
                localStorage.setItem('user', JSON.stringify(data.user));
                localStorage.setItem('sessionId', data.sessionId);
                return data;
            }
            throw new Error(data.message || 'Login failed');
        } catch (error) {
            console.error('Login error:', error);
            throw new Error(error.message || 'Login failed');
        }
    }

    // Helper methods for user state
    getCurrentUser() {
        return JSON.parse(localStorage.getItem('user'));
    }

    isLoggedIn() {
        return !!localStorage.getItem('user');
    }
}

export default new AuthService();