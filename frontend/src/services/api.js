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

// Analytics API (Fixed to match backend implementation)
export const analyticsAPI = {
  // Session Management
  createSession: (data) => api.post('/analytics/session', data),
  getSession: (sessionId) => api.get(`/analytics/session/${sessionId}`),
  getSessionAnalyses: (sessionId) => api.get(`/analytics/session/${sessionId}/analyses`),
  getSessionFeedback: (sessionId) => api.get(`/analytics/session/${sessionId}/feedback`),
  clearSession: (sessionId) => api.delete(`/analytics/session/${sessionId}`),
  
  // Analysis Recording
  recordAnalysis: (data) => api.post('/analytics/analysis', data),
  
  // Feedback Collection (Phase 4 Implementation)
  submitFeedback: (data) => api.post('/analytics/feedback', data),
  
  // System Metrics
  getSystemMetrics: () => api.get('/analytics/system/metrics'),
  getSystemSummary: () => api.get('/analytics/system/summary'),
  
  // Data Export
  exportAnalytics: (data) => api.post('/analytics/export', data),
  
  // Health Check
  healthCheck: () => api.get('/analytics/health'),
};

export default api;

/*
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
*/
