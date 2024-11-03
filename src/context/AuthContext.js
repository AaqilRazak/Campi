import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check for stored user data when app loads
    const storedUser = localStorage.getItem('user');
    const sessionUser = sessionStorage.getItem('user');
    
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    } else if (sessionUser) {
      setUser(JSON.parse(sessionUser));
    }
  }, []);

  const login = (userData) => {
    setUser(userData);
    // Store in localStorage if rememberMe is true, otherwise use sessionStorage
    if (userData.rememberMe) {
      localStorage.setItem('user', JSON.stringify(userData));
    } else {
      sessionStorage.setItem('user', JSON.stringify(userData));
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    sessionStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);