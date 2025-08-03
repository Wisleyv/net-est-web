/**
 * Cliente API centralizado
 * Integração completa com todos os endpoints do backend
 */

import axios from 'axios';
import config from './config';

// Criar instância do axios
const api = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: config.API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para requests
api.interceptors.request.use(
  config => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.log(
        `🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`
      );
    }
    return config;
  },
  error => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Interceptor para responses
api.interceptors.response.use(
  response => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    }
    return response;
  },
  error => {
    console.error(
      '❌ API Response Error:',
      error.response?.data || error.message
    );
    return Promise.reject(error);
  }
);

// Health API
export const healthAPI = {
  check: () => api.get('/health'),
  status: () => api.get('/health/status'),
};

// Text Input API
export const textInputAPI = {
  processTyped: (data) => api.post('/api/v1/text-input/process-typed', data),
  processFile: (formData) => api.post('/api/v1/text-input/process-file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  validate: (data) => api.post('/api/v1/text-input/validate', data),
  getHistory: () => api.get('/api/v1/text-input/history'),
  getById: (id) => api.get(`/api/v1/text-input/${id}`),
  update: (id, data) => api.put(`/api/v1/text-input/${id}`, data),
  delete: (id) => api.delete(`/api/v1/text-input/${id}`),
};

// Semantic Alignment API
export const semanticAlignmentAPI = {
  // Core alignment processing
  processAlignment: (data) => api.post('/api/v1/semantic-alignment/process', data),
  processBatch: (data) => api.post('/api/v1/semantic-alignment/process-batch', data),
  
  // Analysis and validation
  analyze: (data) => api.post('/api/v1/semantic-alignment/analyze', data),
  validateComplexity: (data) => api.post('/api/v1/semantic-alignment/validate-complexity', data),
  
  // Results and data retrieval
  getResults: (analysisId) => api.get(`/api/v1/semantic-alignment/results/${analysisId}`),
  getAlignment: (analysisId) => api.get(`/api/v1/semantic-alignment/alignment/${analysisId}`),
  getMetrics: (analysisId) => api.get(`/api/v1/semantic-alignment/metrics/${analysisId}`),
  getConfidence: (analysisId) => api.get(`/api/v1/semantic-alignment/confidence/${analysisId}`),
  getHistory: (options = {}) => api.get('/api/v1/semantic-alignment/history', { params: options }),
  
  // Configuration and metadata
  getEducationLevels: () => api.get('/api/v1/semantic-alignment/education-levels'),
  
  // Updates and management
  updateAlignment: (analysisId, data) => api.put(`/api/v1/semantic-alignment/alignment/${analysisId}`, data),
  deleteAnalysis: (analysisId) => api.delete(`/api/v1/semantic-alignment/${analysisId}`),
};

// Analytics API
export const analyticsAPI = {
  createSession: (data) => api.post('/api/v1/analytics/sessions', data),
  getSession: (sessionId) => api.get(`/api/v1/analytics/sessions/${sessionId}`),
  updateSession: (sessionId, data) => api.put(`/api/v1/analytics/sessions/${sessionId}`, data),
  deleteSession: (sessionId) => api.delete(`/api/v1/analytics/sessions/${sessionId}`),
  recordAnalysis: (data) => api.post('/api/v1/analytics/analyses', data),
  getAnalyses: (params = {}) => api.get('/api/v1/analytics/analyses', { params }),
  submitFeedback: (data) => api.post('/api/v1/analytics/feedback', data),
  getMetrics: (params = {}) => api.get('/api/v1/analytics/metrics', { params }),
  exportData: (sessionId) => api.get(`/api/v1/analytics/export/${sessionId}`),
};

export default api;
