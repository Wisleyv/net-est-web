
import api from './api';
import config from './config';

const { API_BASE_URL } = config;

export class ComparativeAnalysisService {
  /**
   * Upload and extract text from file
   * @param {File} file - File to upload (TXT, PDF, DOCX, ODT, MD)
   * @returns {Promise<Object>} Extracted text and validation results
   */
  static async uploadTextFile(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/api/v1/comparative-analysis/upload-text', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('File upload error:', error);
      throw new Error(
        error.response?.data?.detail || 
        `Erro ao fazer upload do arquivo: ${error.message}`
      );
    }
  }

  /**
   * Validate comparative texts
   * @param {string} sourceText - Source (complex) text
   * @param {string} targetText - Target (simplified) text
   * @returns {Promise<Object>} Validation results and metrics
   */
  static async validateTexts(sourceText, targetText) {
    try {
      const formData = new FormData();
      formData.append('source_text', sourceText);
      formData.append('target_text', targetText);

      const response = await api.post('/api/v1/comparative-analysis/validate-texts', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('Text validation error:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Erro ao validar textos comparativos'
      );
    }
  }

  /**
   * Helper: Validate file type before upload
   * @param {File} file - File to validate
   * @returns {boolean} Whether file type is supported
   */
  static isFileTypeSupported(file) {
    const supportedTypes = [
      'text/plain',              // .txt
      'text/markdown',           // .md
      'application/pdf',         // .pdf
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
      'application/vnd.oasis.opendocument.text', // .odt
    ];

    const supportedExtensions = ['.txt', '.md', '.pdf', '.docx', '.odt'];
    
    return supportedTypes.includes(file.type) || 
           supportedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
  }

  /**
   * Helper: Format file size for display
   * @param {number} bytes - File size in bytes
   * @returns {string} Formatted file size
   */
  static formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

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

      // Add success field + normalize strategies (Phase 2a additive)
      const data = response.data || {};
      const strategies = (data.simplification_strategies || []).map((s, idx) => ({
        ...s,
        strategy_id: s.strategy_id || s.id || `strategy_${idx}`,
        target_offsets: s.target_offsets || s.targetOffsets || [],
      }));
      return { success: true, ...data, simplification_strategies: strategies };
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
      const response = await api.post('/api/v1/lexical-comparison', {
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
      const response = await api.post('/api/v1/syntactic-comparison', {
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
   * Identify simplification strategies used (via comparative analysis)
   */
  static async identifySimplificationStrategies(sourceText, targetText) {
    try {
      // Use the main comparative analysis endpoint which includes strategies
      const response = await api.post('/api/v1/comparative-analysis', {
        source_text: sourceText,
        target_text: targetText,
        analysis_options: {
          include_lexical_analysis: true,
          include_syntactic_analysis: true,
          include_semantic_analysis: true,
          include_readability_metrics: true,
          include_strategy_detection: true
        }
      });

      return {
        success: true,
        simplification_strategies: response.data.simplification_strategies || [],
        strategies_count: response.data.strategies_count || 0
      };
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
      const response = await api.post('/api/v1/readability-comparison', {
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
      const response = await api.get(`/api/v1/comparative-analysis/${analysisId}/export`, {
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
      const response = await api.get('/api/v1/comparative-analysis/history', {
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
      const response = await api.get(`/api/v1/comparative-analysis/${analysisId}`);
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
