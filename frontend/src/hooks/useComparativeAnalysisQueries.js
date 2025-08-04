/**
 * useComparativeAnalysisQueries.js - Phase 2.B.5 Implementation
 * React Query hooks for comparative analysis functionality
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import ComparativeAnalysisService from '../services/comparativeAnalysisService';
import useErrorHandler from './useErrorHandler';

// Query keys
export const COMPARATIVE_ANALYSIS_KEYS = {
  all: ['comparative-analysis'],
  analysis: (id) => [...COMPARATIVE_ANALYSIS_KEYS.all, 'analysis', id],
  history: (params) => [...COMPARATIVE_ANALYSIS_KEYS.all, 'history', params],
  lexical: (sourceText, targetText) => [...COMPARATIVE_ANALYSIS_KEYS.all, 'lexical', sourceText, targetText],
  syntactic: (sourceText, targetText) => [...COMPARATIVE_ANALYSIS_KEYS.all, 'syntactic', sourceText, targetText],
  strategies: (sourceText, targetText) => [...COMPARATIVE_ANALYSIS_KEYS.all, 'strategies', sourceText, targetText],
  readability: (sourceText, targetText) => [...COMPARATIVE_ANALYSIS_KEYS.all, 'readability', sourceText, targetText],
};

/**
 * Hook for performing comparative analysis
 */
export const useComparativeAnalysis = () => {
  const queryClient = useQueryClient();
  const { handleError, handleSuccess } = useErrorHandler();

  return useMutation({
    mutationFn: ComparativeAnalysisService.performComparativeAnalysis,
    onSuccess: (data) => {
      // Invalidate and refetch analysis history
      queryClient.invalidateQueries({ queryKey: COMPARATIVE_ANALYSIS_KEYS.all });
      
      handleSuccess('Análise comparativa realizada com sucesso!');
      return data;
    },
    onError: (error) => {
      handleError(error, {
        component: 'ComparativeAnalysis',
        operation: 'perform analysis',
      });
    },
    meta: {
      errorMessage: 'Erro ao realizar análise comparativa',
    },
  });
};

/**
 * Hook for lexical comparison
 */
export const useLexicalComparison = (sourceText, targetText, options = {}) => {
  const { handleError } = useErrorHandler();

  return useMutation({
    mutationFn: () => ComparativeAnalysisService.getLexicalComparison(sourceText, targetText),
    onError: (error) => {
      handleError(error, {
        component: 'LexicalComparison',
        operation: 'lexical analysis',
      });
    },
    ...options,
  });
};

/**
 * Hook for syntactic comparison
 */
export const useSyntacticComparison = (sourceText, targetText, options = {}) => {
  const { handleError } = useErrorHandler();

  return useMutation({
    mutationFn: () => ComparativeAnalysisService.getSyntacticComparison(sourceText, targetText),
    onError: (error) => {
      handleError(error, {
        component: 'SyntacticComparison',
        operation: 'syntactic analysis',
      });
    },
    ...options,
  });
};

/**
 * Hook for identifying simplification strategies
 */
export const useSimplificationStrategies = (sourceText, targetText, options = {}) => {
  const { handleError } = useErrorHandler();

  return useMutation({
    mutationFn: () => ComparativeAnalysisService.identifySimplificationStrategies(sourceText, targetText),
    onError: (error) => {
      handleError(error, {
        component: 'SimplificationStrategies',
        operation: 'strategy identification',
      });
    },
    ...options,
  });
};

/**
 * Hook for readability comparison
 */
export const useReadabilityComparison = (sourceText, targetText, options = {}) => {
  const { handleError } = useErrorHandler();

  return useMutation({
    mutationFn: () => ComparativeAnalysisService.getReadabilityComparison(sourceText, targetText),
    onError: (error) => {
      handleError(error, {
        component: 'ReadabilityComparison',
        operation: 'readability analysis',
      });
    },
    ...options,
  });
};

/**
 * Hook for getting analysis history
 */
export const useAnalysisHistory = (limit = 20, offset = 0, options = {}) => {
  const { handleError } = useErrorHandler();

  return useQuery({
    queryKey: COMPARATIVE_ANALYSIS_KEYS.history({ limit, offset }),
    queryFn: () => ComparativeAnalysisService.getAnalysisHistory(limit, offset),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    onError: (error) => {
      handleError(error, {
        component: 'AnalysisHistory',
        operation: 'fetch history',
      });
    },
    ...options,
  });
};

/**
 * Hook for getting specific analysis by ID
 */
export const useAnalysisById = (analysisId, options = {}) => {
  const { handleError } = useErrorHandler();

  return useQuery({
    queryKey: COMPARATIVE_ANALYSIS_KEYS.analysis(analysisId),
    queryFn: () => ComparativeAnalysisService.getAnalysisById(analysisId),
    enabled: !!analysisId,
    staleTime: 10 * 60 * 1000, // 10 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
    onError: (error) => {
      handleError(error, {
        component: 'AnalysisDetails',
        operation: 'fetch analysis',
      });
    },
    ...options,
  });
};

/**
 * Hook for exporting analysis
 */
export const useExportAnalysis = () => {
  const { handleError, handleSuccess } = useErrorHandler();

  return useMutation({
    mutationFn: ({ analysisId, format }) => 
      ComparativeAnalysisService.exportAnalysis(analysisId, format),
    onSuccess: (data) => {
      handleSuccess(data.message || 'Análise exportada com sucesso!');
    },
    onError: (error) => {
      handleError(error, {
        component: 'ExportAnalysis',
        operation: 'export analysis',
      });
    },
  });
};

/**
 * Combined hook for all comparative analysis operations
 */
export const useComparativeAnalysisOperations = () => {
  const performAnalysis = useComparativeAnalysis();
  const lexicalComparison = useLexicalComparison();
  const syntacticComparison = useSyntacticComparison();
  const simplificationStrategies = useSimplificationStrategies();
  const readabilityComparison = useReadabilityComparison();
  const exportAnalysis = useExportAnalysis();

  return {
    // Main analysis
    performAnalysis,
    
    // Detailed comparisons
    lexicalComparison,
    syntacticComparison,
    simplificationStrategies,
    readabilityComparison,
    
    // Export
    exportAnalysis,
    
    // Combined loading state
    isLoading: performAnalysis.isPending ||
               lexicalComparison.isPending ||
               syntacticComparison.isPending ||
               simplificationStrategies.isPending ||
               readabilityComparison.isPending ||
               exportAnalysis.isPending,
    
    // Combined error state
    hasError: performAnalysis.isError ||
              lexicalComparison.isError ||
              syntacticComparison.isError ||
              simplificationStrategies.isError ||
              readabilityComparison.isError ||
              exportAnalysis.isError,
  };
};

export default {
  useComparativeAnalysis,
  useLexicalComparison,
  useSyntacticComparison,
  useSimplificationStrategies,
  useReadabilityComparison,
  useAnalysisHistory,
  useAnalysisById,
  useExportAnalysis,
  useComparativeAnalysisOperations,
};
