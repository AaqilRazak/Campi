import axios from 'axios';

const API_URL = 'http://localhost/campi-api/api';

export const login = async (username, password) => {
    try {
        const response = await axios.post(`${API_URL}/login.php`, {
            username,
            password
        });

        if (response.data.success) {
            // Store complete user data and session info
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('sessionId', response.data.sessionId);
            localStorage.setItem('user', JSON.stringify(response.data.user));
            return response.data;
        } else {
            throw new Error(response.data.message);
        }
    } catch (error) {
        if (error.response) {
            throw new Error(error.response.data.message || 'Login failed');
        }
        throw new Error('Network error');
    }
};

export const logout = async () => {
    try {
        const sessionId = localStorage.getItem('sessionId');
        if (sessionId) {
            // Call logout endpoint to update SessionEndTime
            await axios.post(`${API_URL}/logout.php`, {
                sessionId: sessionId
            });
        }
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        // Clear local storage regardless of logout API success
        localStorage.removeItem('token');
        localStorage.removeItem('sessionId');
        localStorage.removeItem('user');
    }
};
