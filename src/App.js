import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import ChatPage from './pages/ChatPage';
import AdminPage from './pages/AdminPage';

// Create a wrapper component to handle navigation blocking
const NavigationHandler = ({ children }) => {
  const navigate = useNavigate();

  useEffect(() => {
    // Prevent using browser back/forward buttons
    window.history.pushState(null, null, window.location.pathname);
    window.addEventListener('popstate', () => {
      window.history.pushState(null, null, window.location.pathname);
    });

    return () => {
      window.removeEventListener('popstate', () => {
        window.history.pushState(null, null, window.location.pathname);
      });
    };
  }, [navigate]);

  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <NavigationHandler>
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/chat"
              element={
                <ProtectedRoute>
                  <ChatPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminPage />
                </ProtectedRoute>
              }
            />
            {/* Catch all other routes and redirect to login */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </NavigationHandler>
      </Router>
    </AuthProvider>
  );
}

export default App;