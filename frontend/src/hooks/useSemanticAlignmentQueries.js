/**
 * React Query Hooks for Semantic Alignment Operations
 * Handles text simplification and adaptation to different education levels
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { semanticAlignmentAPI } from '../services/api';
import useAnalysisStore from '../stores/useAnalysisStore';

/**
 * Hook for semantic alignment processing
 */
export const useSemanticAlignment = () => {
  const queryClient = useQueryClient();
  const { setProcessingStep, setProcessingError } = useAnalysisStore();

  return useMutation({
    mutationFn: async (alignmentRequest) => {
      try {
        setProcessingStep('analyzing');
        
        // Validate input
        if (!alignmentRequest.text?.trim()) {
          throw new Error('Texto é obrigatório para alinhamento semântico');
        }

        if (alignmentRequest.text.trim().length < 10) {
          throw new Error('Texto deve ter pelo menos 10 caracteres');
        }

        // Call API
        const response = await semanticAlignmentAPI.processAlignment(alignmentRequest);

        setProcessingStep('formatting');
        
        // Validate response
        if (!response.alignedText) {
          throw new Error('Resposta inválida do servidor: texto alinhado não encontrado');
        }

        return {
          id: response.id || Date.now().toString(),
          originalText: alignmentRequest.text,
          alignedText: response.alignedText,
          targetLevel: alignmentRequest.targetLevel,
          statistics: {
            originalWordCount: alignmentRequest.text.trim().split(/\s+/).length,
            alignedWordCount: response.alignedText.trim().split(/\s+/).length,
            simplificationRatio: response.statistics?.simplificationRatio || 0,
            readabilityScore: response.statistics?.readabilityScore || 0,
            complexityReduction: response.statistics?.complexityReduction || 0,
          },
          changes: response.changes || [],
          explanations: response.explanations || [],
          summary: response.summary || '',
          processedAt: new Date().toISOString(),
          processingTime: response.processingTime || 0,
        };

      } catch (error) {
        setProcessingError(error.message);
        throw error;
      } finally {
        setProcessingStep(null);
      }
    },
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['alignments'] });
      queryClient.invalidateQueries({ queryKey: ['analysis-history'] });
      
      // Cache the result
      queryClient.setQueryData(['alignment', data.id], data);
    },
    onError: (error) => {
      console.error('Semantic alignment error:', error);
      setProcessingError(error.message);
    },
  });
};

/**
 * Hook for batch semantic alignment (multiple texts)
 */
export const useBatchSemanticAlignment = () => {
  const queryClient = useQueryClient();
  const { setProcessingStep, setProcessingError } = useAnalysisStore();

  return useMutation({
    mutationFn: async (batchRequest) => {
      try {
        setProcessingStep('analyzing');

        if (!batchRequest.texts?.length) {
          throw new Error('Lista de textos é obrigatória para processamento em lote');
        }

        if (batchRequest.texts.length > 10) {
          throw new Error('Máximo de 10 textos por lote');
        }

        const response = await semanticAlignmentAPI.processBatch(batchRequest);

        setProcessingStep('formatting');

        return {
          batchId: response.batchId || Date.now().toString(),
          results: response.results || [],
          targetLevel: batchRequest.targetLevel,
          totalProcessed: response.results?.length || 0,
          successCount: response.results?.filter(r => r.success).length || 0,
          errorCount: response.results?.filter(r => !r.success).length || 0,
          processedAt: new Date().toISOString(),
          processingTime: response.processingTime || 0,
        };

      } catch (error) {
        setProcessingError(error.message);
        throw error;
      } finally {
        setProcessingStep(null);
      }
    },
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['alignments'] });
      queryClient.invalidateQueries({ queryKey: ['batch-alignments'] });
      
      // Cache individual results
      data.results?.forEach((result) => {
        if (result.success && result.id) {
          queryClient.setQueryData(['alignment', result.id], result.data);
        }
      });
    },
    onError: (error) => {
      console.error('Batch semantic alignment error:', error);
      setProcessingError(error.message);
    },
  });
};

/**
 * Hook for retrieving alignment history
 */
export const useAlignmentHistory = (options = {}) => {
  return useQuery({
    queryKey: ['alignment-history', options],
    queryFn: async () => {
      const response = await semanticAlignmentAPI.getHistory(options);
      return response.data || [];
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
    enabled: options.enabled !== false,
  });
};

/**
 * Hook for validating text complexity
 */
export const useTextComplexityValidation = () => {
  return useMutation({
    mutationFn: async (text) => {
      if (!text?.trim()) {
        throw new Error('Texto é obrigatório para validação');
      }

      const response = await semanticAlignmentAPI.validateComplexity({ text });
      
      return {
        isValid: response.isValid || false,
        complexityScore: response.complexityScore || 0,
        readabilityScore: response.readabilityScore || 0,
        recommendations: response.recommendations || [],
        estimatedLevel: response.estimatedLevel || 'unknown',
        wordCount: text.trim().split(/\s+/).length,
        sentenceCount: text.split(/[.!?]+/).filter(s => s.trim()).length,
      };
    },
  });
};

/**
 * Hook for getting available education levels
 */
export const useEducationLevels = () => {
  return useQuery({
    queryKey: ['education-levels'],
    queryFn: async () => {
      const response = await semanticAlignmentAPI.getEducationLevels();
      return response.data || {};
    },
    staleTime: 30 * 60 * 1000, // 30 minutes
    retry: 1,
  });
};

export default {
  useSemanticAlignment,
  useBatchSemanticAlignment,
  useAlignmentHistory,
  useTextComplexityValidation,
  useEducationLevels,
};
