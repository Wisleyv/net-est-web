/**
 * Cliente API centralizado
 * Integração completa com todos os endpoints do backend
 */

import axios from 'axios';
import config from './config.js';

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
    const fullUrl = `${config.baseURL}${config.url}`;
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.log(
        `🚀 API Request: ${config.method?.toUpperCase()} ${fullUrl}`
      );
      console.log('🔧 Request config:', { 
        baseURL: config.baseURL, 
        url: config.url, 
        method: config.method,
        headers: config.headers,
        data: config.data 
      });
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
      console.log(`✅ API Response: ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`);
    }
    return response;
  },
  error => {
    const errorDetails = {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      method: error.config?.method,
      isNetworkError: !error.response,
      isTimeout: error.code === 'ECONNABORTED'
    };
    
    console.error('❌ API Response Error:', errorDetails);
    console.error('🔍 Full error object:', error);
    
    if (errorDetails.isNetworkError) {
      console.error('🌐 Network Error Details:', {
        message: 'This could be a CORS issue, server not running, or incorrect URL',
        attemptedUrl: `${error.config?.baseURL}${error.config?.url}`,
        suggestion: 'Check if backend server is running and CORS is properly configured'
      });
    }
    
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

// Comparative Analysis API
export const comparativeAnalysisAPI = {
  // Backend exposes POST /api/v1/comparative-analysis/ for main analysis
  analyze: (data) => api.post('/api/v1/comparative-analysis/', data),
  validateTexts: (data) => api.post('/api/v1/comparative-analysis/validate-texts', data),
  uploadText: (formData) => api.post('/api/v1/comparative-analysis/upload-text', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

export default api;

// Annotations Search API (Phase 4b)
export const annotationsAPI = {
  search: ({ sessionId, statuses, codes }) =>
    api.get('/api/v1/annotations/search', {
      params: {
        session_id: sessionId,
        statuses,
        strategy_codes: codes,
      },
      paramsSerializer: (params) => {
        const usp = new URLSearchParams();
        if (params.session_id) usp.append('session_id', params.session_id);
        (params.statuses || []).forEach((s) => usp.append('statuses', s));
        (params.strategy_codes || []).forEach((c) => usp.append('strategy_codes', c));
        return usp.toString();
      },
    }),
  audit: ({ sessionId, annotationId, actions }) =>
    api.get('/api/v1/annotations/audit', {
      params: {
        session_id: sessionId,
        annotation_id: annotationId || undefined,
        actions,
      },
      paramsSerializer: (params) => {
        const usp = new URLSearchParams();
        if (params.session_id) usp.append('session_id', params.session_id);
        if (params.annotation_id) usp.append('annotation_id', params.annotation_id);
        (params.actions || []).forEach((a) => usp.append('actions', a));
        return usp.toString();
      },
    }),
};

/*
UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
*/
