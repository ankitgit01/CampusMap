/**
 * Map and Navigation Service
 */
import api from './api';

export const mapService = {
  findRoute: async (source, destination, mode = 'fastest', algorithm = 'dijkstra') => {
    const response = await api.post('/navigation/find-route', null, {
      params: {
        source_location: source,
        destination_location: destination,
        mode,
        algorithm,
      },
    });
    return response.data;
  },

  compareRoutes: async (source, destination) => {
    const response = await api.post('/navigation/compare-routes', null, {
      params: {
        source_location: source,
        destination_location: destination,
      },
    });
    return response.data;
  },

  getRouteDetails: async (routeId) => {
    const response = await api.get(`/navigation/route-details/${routeId}`);
    return response.data;
  },

  getAccessibilityIndex: async (locationId) => {
    const response = await api.get(`/navigation/accessibility-index/${locationId}`);
    return response.data;
  },

  getAccessibilityMetrics: async () => {
    const response = await api.get('/navigation/accessibility-metrics');
    return response.data;
  },

  getCrowdedness: async (locationId) => {
    const response = await api.get(`/navigation/crowdedness/${locationId}`);
    return response.data;
  },

  setCurrentLocation: async (sessionId, locationId) => {
    const response = await api.post('/navigation/presence', null, {
      params: {
        session_id: sessionId,
        location_id: locationId,
      },
    });
    return response.data;
  },

  getSignals: async () => {
    const response = await api.get('/navigation/signals');
    return response.data;
  },

  getWeather: async ({ locationId, latitude, longitude }) => {
    const response = await api.get('/navigation/weather', {
      params: {
        location_id: locationId,
        latitude,
        longitude,
      },
    });
    return response.data;
  },

  searchLocations: async (query, category = null, limit = 10) => {
    const response = await api.get('/search/locations', {
      params: {
        query,
        category,
        limit,
      },
    });
    return response.data;
  },

  getCategories: async () => {
    const response = await api.get('/search/categories');
    return response.data;
  },

  getNearby: async (latitude, longitude, category = null, radius = 500) => {
    const response = await api.get('/search/nearby', {
      params: {
        latitude,
        longitude,
        category,
        radius,
      },
    });
    return response.data;
  },

  getTrendingLocations: async (days = 7) => {
    const response = await api.get('/search/trending', {
      params: { days },
    });
    return response.data;
  },

  getAccessibleLocations: async (minScore = 0.6, category = null) => {
    const response = await api.get('/search/accessible', {
      params: {
        min_score: minScore,
        category,
      },
    });
    return response.data;
  },

  getLocationsByCategory: async (category, skip = 0, limit = 50) => {
    const response = await api.get(`/search/by-category/${category}`, {
      params: { skip, limit },
    });
    return response.data;
  },

  getAllLocations: async (skip = 0, limit = 200) => {
    const response = await api.get('/admin/locations', {
      params: { skip, limit },
    });
    return response.data;
  },

  getAllRoutes: async (skip = 0, limit = 200) => {
    const response = await api.get('/admin/routes', {
      params: { skip, limit },
    });
    return response.data;
  },

  updateRoute: async (routeId, payload) => {
    const response = await api.put(`/admin/routes/${routeId}`, payload);
    return response.data;
  },

  createRoute: async (payload) => {
    const response = await api.post('/admin/routes', payload);
    return response.data;
  },

  deleteRoute: async (routeId) => {
    const response = await api.delete(`/admin/routes/${routeId}`);
    return response.data;
  },

  updateLocation: async (locationId, payload) => {
    const response = await api.put(`/admin/locations/${locationId}`, payload);
    return response.data;
  },
};
