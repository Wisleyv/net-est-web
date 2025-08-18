/**
 * Manual Tags Service
 * Service for managing user-created manual tags on sentences
 */

import { manualTagsAPI } from './api';

/**
 * Service class for manual tags operations
 */
export class ManualTagsService {
  
  /**
   * Create a new manual tag for a sentence
   * @param {Object} tagData - Tag creation data
   * @param {string} tagData.tagType - Tag type (e.g., 'AS+', 'SL+')
   * @param {number} tagData.sentenceIndex - Index of the sentence to tag
   * @param {string} tagData.sentenceText - Text of the sentence being tagged
   * @param {string} tagData.analysisId - ID of the analysis session
   * @param {string} [tagData.userNotes] - Optional user notes
   * @returns {Promise<Object>} Created tag data
   */
  static async createTag(tagData) {
    try {
      console.log('Creating manual tag:', tagData);
      
      const request = {
        tag_type: tagData.tagType,
        sentence_index: tagData.sentenceIndex,
        sentence_text: tagData.sentenceText,
        analysis_id: tagData.analysisId,
        user_notes: tagData.userNotes || null
      };
      
      const response = await manualTagsAPI.create(request);
      
      if (response.data.success) {
        console.log('Manual tag created successfully:', response.data.tag);
        return {
          success: true,
          tag: response.data.tag,
          message: response.data.message || 'Tag criada com sucesso!'
        };
      } else {
        return {
          success: false,
          message: response.data.message || 'Erro ao criar tag'
        };
      }
      
    } catch (error) {
      console.error('Failed to create manual tag:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.message ||
        'Erro ao criar tag manual'
      );
    }
  }

  /**
   * Get all manual tags for an analysis session
   * @param {string} analysisId - Analysis session ID
   * @returns {Promise<Array>} Array of manual tags
   */
  static async getTagsForAnalysis(analysisId) {
    try {
      console.log('Getting tags for analysis:', analysisId);
      
      const response = await manualTagsAPI.getForAnalysis(analysisId);
      
      if (response.data.success) {
        console.log(`Retrieved ${response.data.tags.length} tags for analysis ${analysisId}`);
        return response.data.tags;
      } else {
        console.warn('Failed to get tags:', response.data.message);
        return [];
      }
      
    } catch (error) {
      console.error('Failed to get tags for analysis:', error);
      // Return empty array on error instead of throwing, as tags are optional
      return [];
    }
  }

  /**
   * Get manual tags for a specific sentence
   * @param {string} analysisId - Analysis session ID
   * @param {number} sentenceIndex - Sentence index
   * @returns {Promise<Array>} Array of manual tags for the sentence
   */
  static async getTagsForSentence(analysisId, sentenceIndex) {
    try {
      console.log('Getting tags for sentence:', analysisId, sentenceIndex);
      
      const response = await manualTagsAPI.getForSentence(analysisId, sentenceIndex);
      
      if (response.data.success) {
        return response.data.tags;
      } else {
        return [];
      }
      
    } catch (error) {
      console.error('Failed to get tags for sentence:', error);
      return [];
    }
  }

  /**
   * Update an existing manual tag
   * @param {string} tagId - Tag ID to update
   * @param {Object} updates - Updates to apply
   * @param {string} [updates.tagType] - New tag type
   * @param {string} [updates.userNotes] - New user notes
   * @returns {Promise<Object>} Updated tag data
   */
  static async updateTag(tagId, updates) {
    try {
      console.log('Updating manual tag:', tagId, updates);
      
      const request = {
        tag_type: updates.tagType || null,
        user_notes: updates.userNotes || null
      };
      
      const response = await manualTagsAPI.update(tagId, request);
      
      if (response.data.success) {
        console.log('Manual tag updated successfully:', response.data.tag);
        return {
          success: true,
          tag: response.data.tag,
          message: response.data.message || 'Tag atualizada com sucesso!'
        };
      } else {
        return {
          success: false,
          message: response.data.message || 'Erro ao atualizar tag'
        };
      }
      
    } catch (error) {
      console.error('Failed to update manual tag:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.message ||
        'Erro ao atualizar tag manual'
      );
    }
  }

  /**
   * Delete a manual tag
   * @param {string} tagId - Tag ID to delete
   * @returns {Promise<Object>} Deletion result
   */
  static async deleteTag(tagId) {
    try {
      console.log('Deleting manual tag:', tagId);
      
      const response = await manualTagsAPI.delete(tagId);
      
      if (response.data.success) {
        console.log('Manual tag deleted successfully');
        return {
          success: true,
          message: response.data.message || 'Tag excluída com sucesso!',
          deletedTagId: response.data.deleted_tag_id
        };
      } else {
        return {
          success: false,
          message: response.data.message || 'Erro ao excluir tag'
        };
      }
      
    } catch (error) {
      console.error('Failed to delete manual tag:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.message ||
        'Erro ao excluir tag manual'
      );
    }
  }

  /**
   * Get available tag types with descriptions
   * @returns {Promise<Object>} Tag types mapping
   */
  static async getAvailableTagTypes() {
    try {
      const response = await manualTagsAPI.getAvailableTypes();
      return response.data;
    } catch (error) {
      console.error('Failed to get available tag types:', error);
      // Return default tag types if API fails
      return {
        'AS+': 'Alteração de Sentido',
        'DL+': 'Reorganização Posicional',
        'EXP+': 'Explicitação e Detalhamento',
        'IN+': 'Manejo de Inserções',
        'MOD+': 'Reinterpretação Perspectiva',
        'MT+': 'Otimização de Títulos',
        'OM+': 'Supressão Seletiva',
        'PRO+': 'Desvio Semântico',
        'RF+': 'Reescrita Global',
        'RD+': 'Estruturação de Conteúdo e Fluxo',
        'RP+': 'Fragmentação Sintática',
        'SL+': 'Adequação de Vocabulário',
        'TA+': 'Clareza Referencial',
        'MV+': 'Alteração da Voz Verbal'
      };
    }
  }

  /**
   * Get statistics for manual tags in an analysis
   * @param {string} analysisId - Analysis session ID
   * @returns {Promise<Object>} Tag statistics
   */
  static async getTagStats(analysisId) {
    try {
      const response = await manualTagsAPI.getStats(analysisId);
      if (response.data.success) {
        return response.data.stats;
      } else {
        return {
          total_tags: 0,
          tag_type_distribution: {},
          analysis_sessions: 0
        };
      }
    } catch (error) {
      console.error('Failed to get tag stats:', error);
      return {
        total_tags: 0,
        tag_type_distribution: {},
        analysis_sessions: 0
      };
    }
  }

  /**
   * Delete all manual tags for an analysis session
   * @param {string} analysisId - Analysis session ID
   * @returns {Promise<Object>} Deletion result
   */
  static async deleteAllTagsForAnalysis(analysisId) {
    try {
      console.log('Deleting all tags for analysis:', analysisId);
      
      const response = await manualTagsAPI.deleteAllForAnalysis(analysisId);
      
      if (response.data.success) {
        console.log(`Deleted ${response.data.deleted_count} tags for analysis ${analysisId}`);
        return {
          success: true,
          message: response.data.message,
          deletedCount: response.data.deleted_count
        };
      } else {
        return {
          success: false,
          message: 'Erro ao excluir tags da análise'
        };
      }
      
    } catch (error) {
      console.error('Failed to delete tags for analysis:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.message ||
        'Erro ao excluir tags da análise'
      );
    }
  }

  /**
   * Check if a tag already exists for a sentence
   * @param {Array} existingTags - Array of existing tags
   * @param {number} sentenceIndex - Sentence index to check
   * @param {string} tagType - Tag type to check
   * @returns {boolean} True if tag exists
   */
  static tagExistsForSentence(existingTags, sentenceIndex, tagType) {
    return existingTags.some(tag => 
      tag.sentence_index === sentenceIndex && 
      tag.tag_type === tagType
    );
  }

  /**
   * Format tag for display in UI
   * @param {Object} tag - Raw tag object from API
   * @returns {Object} Formatted tag object
   */
  static formatTagForUI(tag) {
    return {
      id: tag.id,
      code: tag.tag_type,
      name: tag.tag_type, // For backward compatibility
      fullName: tag.tag_type, // For backward compatibility
      confidence: tag.confidence || 1.0,
      evidence: tag.evidence || ['Manually added by human validator'],
      sentenceIndex: tag.sentence_index,
      sentenceText: tag.sentence_text,
      analysisId: tag.analysis_id,
      userNotes: tag.user_notes,
      createdAt: tag.created_at,
      updatedAt: tag.updated_at,
      isManual: true // Flag to distinguish from automatic tags
    };
  }

  /**
   * Convert UI format back to API format
   * @param {Object} uiTag - Tag in UI format
   * @returns {Object} Tag in API format
   */
  static formatTagForAPI(uiTag) {
    return {
      tag_type: uiTag.code || uiTag.name,
      sentence_index: uiTag.sentenceIndex,
      sentence_text: uiTag.sentenceText,
      analysis_id: uiTag.analysisId,
      user_notes: uiTag.userNotes || null
    };
  }
}

export default ManualTagsService;