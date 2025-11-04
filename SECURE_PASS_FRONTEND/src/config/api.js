// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API endpoints
export const API_ENDPOINTS = {
  LOGIN: '/token',
  REGISTER: '/users/register', 
  USERS: '/users',
  VEHICLES: '/vehicles',
  LOGS: '/logs',
  PHOTOS: '/photos',
  DETECTION: '/detection',
  OCR: '/ocr',
  UPDATE_USER: '/users',
  DELETE_USER: '/users'
};

// Helper function to construct full API URLs
export const getApiUrl = (endpoint) => `${API_BASE_URL}${endpoint}`;