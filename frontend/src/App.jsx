/**
 * Main App Component with Routing
 */
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { authService } from './services/auth';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Admin from './pages/Admin';
import History from './pages/History';
import Navigation from './pages/Navigation';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" />;
  }
  return children;
};

function App() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Check if user is still authenticated
    if (authService.isAuthenticated()) {
      // Could verify token with backend here
      setIsReady(true);
    } else {
      setIsReady(true);
    }
  }, []);

  if (!isReady) {
    return (
      <div className="flex items-center justify-center h-screen bg-blue-600">
        <div className="text-white text-2xl">Loading CampusMap...</div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Navigation is public so map features remain available offline */}
        <Route path="/navigation" element={<Navigation />} />
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <History />
            </ProtectedRoute>
          }
        />
        <Route path="/admin" element={<Admin />} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
