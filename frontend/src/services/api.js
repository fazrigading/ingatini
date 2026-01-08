import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// User APIs
export const createUser = (userData) =>
  api.post('/users/', userData);

export const getUser = (userId) =>
  api.get(`/users/${userId}`);

export const listUsers = (skip = 0, limit = 10) =>
  api.get('/users/', { params: { skip, limit } });

// Document APIs
export const uploadDocument = (userId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/documents/upload?user_id=${userId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getDocuments = (userId) =>
  api.get(`/documents/${userId}`);

export const getDocument = (docId) =>
  api.get(`/documents/${docId}`);

export const deleteDocument = (docId) =>
  api.delete(`/documents/${docId}`);

// Query & RAG APIs
export const queryDocuments = (queryData) =>
  api.post('/query/', queryData);

export const getQueryHistory = (userId) =>
  api.get(`/query/history/${userId}`);

// Health check
export const healthCheck = () =>
  api.get('/health');

export default api;
