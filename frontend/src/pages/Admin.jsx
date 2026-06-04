/**
 * Admin Page
 */
import React from 'react';
import { Link, Navigate } from 'react-router-dom';
import NavBar from '../components/NavBar';
import AdminPanel from '../components/AdminPanel';
import { authService } from '../services/auth';

const Admin = () => {
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" state={{ from: '/admin', admin: true }} replace />;
  }

  if (!authService.isAdmin()) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NavBar />
        <main className="mx-auto max-w-xl px-4 py-10">
          <div className="rounded border border-amber-200 bg-white p-6 shadow-sm">
            <h1 className="text-2xl font-bold text-gray-950">Admin access required</h1>
            <p className="mt-2 text-gray-600">
              Sign in with an admin account to manage IIT Roorkee locations and live route status.
            </p>
            <Link
              to="/login"
              state={{ from: '/admin', admin: true }}
              className="mt-5 inline-block rounded bg-blue-600 px-4 py-3 font-semibold text-white hover:bg-blue-700"
            >
              Admin login
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <AdminPanel />
      </div>
    </div>
  );
};

export default Admin;
