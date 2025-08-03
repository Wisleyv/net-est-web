/**
 * React Query Configuration
 * Central configuration for server state management
 */

import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: how long data is considered fresh
      staleTime: 5 * 60 * 1000, // 5 minutes

      // Cache time: how long data stays in cache after becoming unused
      cacheTime: 10 * 60 * 1000, // 10 minutes

      // Retry configuration
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors (client errors)
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        // Retry up to 3 times for other errors
        return failureCount < 3;
      },

      // Retry delay with exponential backoff
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

      // Refetch configuration
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      refetchOnMount: true,
    },
    mutations: {
      // Retry mutations once
      retry: 1,
      
      // Retry delay for mutations
      retryDelay: 1000,
    },
  },
});

// Query Keys Factory
export const queryKeys = {
  // Health endpoints
  health: ['health'],
  healthStatus: ['health', 'status'],

  // Text Input endpoints
  textInput: ['text-input'],
  textInputProcess: (method) => ['text-input', 'process', method],
  textInputValidate: ['text-input', 'validate'],
  textInputHistory: ['text-input', 'history'],

  // Semantic Alignment endpoints
  semanticAlignment: ['semantic-alignment'],
  alignmentAnalyze: (analysisId) => ['semantic-alignment', 'analyze', analysisId],
  alignmentResults: (analysisId) => ['semantic-alignment', 'results', analysisId],
  alignmentHistory: ['semantic-alignment', 'history'],

  // Analytics endpoints
  analytics: ['analytics'],
  analyticsSession: (sessionId) => ['analytics', 'session', sessionId],
  analyticsResults: ['analytics', 'results'],
  analyticsMetrics: ['analytics', 'metrics'],
  analyticsExport: (sessionId) => ['analytics', 'export', sessionId],
};

// Error handling utilities
export const handleQueryError = (error, fallbackMessage = 'Ocorreu um erro inesperado') => {
  console.error('Query Error:', error);
  
  if (error?.response?.data?.detail) {
    return error.response.data.detail;
  }
  
  if (error?.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error?.message) {
    return error.message;
  }
  
  return fallbackMessage;
};

// Success notification utility
export const handleQuerySuccess = (data, message) => {
  // Log success in development only
  if (import.meta.env.DEV) {
    // eslint-disable-next-line no-console
    console.log('Query Success:', message, data);
  }
  return data;
};
