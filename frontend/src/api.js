/**
 * BLACKBOX API Service
 * Handles all communication with backend
 */

import axios from 'axios';

// Production backend URL on Render
const API_BASE_URL = 'https://blackbox-33n9.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const blackboxAPI = {
  // Incidents
  getIncidents: async (params = {}) => {
    const response = await api.get('/incidents', { params });
    return response.data;
  },

  getIncident: async (id) => {
    const response = await api.get(`/incidents/${id}`);
    return response.data;
  },

  resolveIncident: async (id) => {
    const response = await api.patch(`/incidents/${id}/resolve`);
    return response.data;
  },

  // Events
  getEvents: async (params = {}) => {
    const response = await api.get('/events', { params });
    return response.data;
  },

  createEvent: async (event) => {
    const response = await api.post('/events', event);
    return response.data;
  },
};

export default blackboxAPI;
