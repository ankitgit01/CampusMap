/**
 * NavigationBar Component
 */
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';

export const NavBar = () => {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const isAuthenticated = authService.isAuthenticated();
  const isAdmin = authService.isAdmin();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const navLinkClass = 'rounded-md px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 hover:text-slate-950';

  return (
    <nav className="border-b border-slate-200 bg-white/95 text-slate-950 shadow-sm">
      <div className="mx-auto max-w-7xl px-4">
        <div className="flex h-16 items-center justify-between">
          <Link to="/" className="text-2xl font-bold tracking-tight">
            CampusMap
          </Link>

          <div className="hidden items-center gap-1 md:flex">
            <Link to="/" className={navLinkClass}>Home</Link>
            <Link to="/navigation" className={navLinkClass}>Navigate</Link>
            {isAuthenticated && <Link to="/history" className={navLinkClass}>History</Link>}
            {isAdmin && <Link to="/admin" className={navLinkClass}>Admin</Link>}
            {isAuthenticated ? (
              <button onClick={handleLogout} className="ml-2 rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700">
                Logout
              </button>
            ) : (
              <>
                <Link to="/login" className={navLinkClass}>Login</Link>
                <Link to="/register" className="ml-2 rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800">
                  Register
                </Link>
              </>
            )}
          </div>

          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="rounded-md px-3 py-2 text-sm font-semibold hover:bg-slate-100 md:hidden"
          >
            Menu
          </button>
        </div>

        {isMenuOpen && (
          <div className="space-y-1 pb-4 md:hidden">
            <Link to="/" className="block rounded-md px-3 py-2 hover:bg-slate-100">Home</Link>
            <Link to="/navigation" className="block rounded-md px-3 py-2 hover:bg-slate-100">Navigate</Link>
            {isAuthenticated && <Link to="/history" className="block rounded-md px-3 py-2 hover:bg-slate-100">History</Link>}
            {isAdmin && <Link to="/admin" className="block rounded-md px-3 py-2 hover:bg-slate-100">Admin</Link>}
            {isAuthenticated ? (
              <button onClick={handleLogout} className="block w-full rounded-md bg-red-600 px-3 py-2 text-left text-white hover:bg-red-700">
                Logout
              </button>
            ) : (
              <>
                <Link to="/login" className="block rounded-md px-3 py-2 hover:bg-slate-100">Login</Link>
                <Link to="/register" className="block rounded-md bg-slate-950 px-3 py-2 font-semibold text-white">Register</Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default NavBar;
