/**
 * comparativeAnalysisService.js - Phase 2.B.5 Implementation
 * Service for comparative analysis between source and target texts
 */

import api from './api';

export class ComparativeAnalysisService {
  /**
   * Perform comparative analysis between source and target texts
   */
  static async performComparativeAnalysis(analysisData) {
    try {
      const response = await api.post('/api/v1/comparative-analysis/', {
        source_text: analysisData.sourceText,
        target_text: analysisData.targetText,
        metadata: analysisData.metadata,
        analysis_options: {
          include_lexical_analysis: true,
          include_syntactic_analysis: true,
          include_semantic_analysis: true,
          include_readability_metrics: true,
          include_strategy_identification: true,
        }
      });

      return response.data;
    } catch (error) {
      console.error('Comparative analysis error:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Erro ao realizar análise comparativa'
      );
    }
  }

  /**
   * Get detailed lexical comparison
   */
  static async getLexicalComparison(sourceText, targetText) {
    try {
      const response = await api.post('/v1/lexical-comparison', {
        source_text: sourceText,
        target_text: targetText,
      });

      return response.data;
    } catch (error) {
      console.error('Lexical comparison error:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Erro ao realizar comparação lexical'
      );
    }
  }

  /**
   * Get syntactic analysis comparison
   */
  static async getSyntacticComparison(sourceText, targetText) {
    try {
      const response = await api.post('/v1/syntactic-comparison', {
        source_text: sourceText,
        target_text: targetText,
      });

      return response.data;
    } catch (error) {
      console.error('Syntactic comparison error:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Erro ao realizar análise sintática'
      );
    }
  }

  /**
   * Identify simplification strategies used
   */
  static async identifySimplificationStrategies(sourceText, targetText) {
    try {
      const response = await api.post('/v1/simplification-strategies', {
        source_text: sourceText,
        target_text: targetText,
      });

      return response.data;
    } catch (error) {
      console.error('Strategy identification error:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Erro ao identificar estratégias de simplificação'
      );
    }
  }

  /**
   * Get readability metrics comparison
   */
  static async getReadabilityComparison(sourceText, targetText) {
    try {
      const response = await api.post('/v1/readability-comparison', {
        source_text: sourceText,
        target_text: targetText,
      });

      return response.data;
    } catch (error) {
      console.error('Readability comparison error:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Erro ao calcular métricas de legibilidade'
      );
    }
  }

  /**
   * Export comparative analysis results
   */
  static async exportAnalysis(analysisId, format = 'pdf') {
    try {
      const response = await api.get(`/v1/comparative-analysis/${analysisId}/export`, {
        params: { format },
        responseType: 'blob',
      });

      // Create download link
      const blob = new Blob([response.data], { 
        type: format === 'pdf' ? 'application/pdf' : 'text/csv' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `comparative-analysis-${analysisId}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      return { success: true, message: 'Análise exportada com sucesso!' };
    } catch (error) {
      console.error('Export analysis error:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Erro ao exportar análise'
      );
    }
  }

  /**
   * Get analysis history
   */
  static async getAnalysisHistory(limit = 20, offset = 0) {
    try {
      const response = await api.get('/v1/comparative-analysis/history', {
        params: { limit, offset },
      });

      return response.data;
    } catch (error) {
      console.error('Analysis history error:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Erro ao buscar histórico de análises'
      );
    }
  }

  /**
   * Get specific analysis by ID
   */
  static async getAnalysisById(analysisId) {
    try {
      const response = await api.get(`/v1/comparative-analysis/${analysisId}`);
      return response.data;
    } catch (error) {
      console.error('Get analysis error:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Erro ao buscar análise'
      );
    }
  }
}

export default ComparativeAnalysisService;
