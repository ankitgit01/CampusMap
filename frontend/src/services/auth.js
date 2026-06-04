/**
 * Authentication Service
 */
import api from './api';

export const authService = {
  register: async (email, username, password, fullName) => {
    const response = await api.post('/auth/register', {
      email,
      username,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', {
      email,
      password,
    });
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user_id', response.data.user_id);
      localStorage.setItem('is_admin', response.data.is_admin);
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('is_admin');
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  refreshToken: async () => {
    const response = await api.post('/auth/refresh-token');
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }
    return response.data;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  isAdmin: () => {
    return localStorage.getItem('is_admin') === 'true';
  },
};
