
import api from './api';
import config from './config';

const { API_BASE_URL } = config;

/**
 * Normalize backend API response to a frontend-friendly shape.
 * Ensures both snake_case and camelCase keys are available and
 * provides sensible defaults for missing fields the UI expects.
 */
function normalizeAnalysisResponse(data = {}) {
  if (!data || typeof data !== 'object') return data;

  const normalized = {
    // identity / ids
    id: data.id ?? data.analysis_id ?? data.analysisId ?? null,
    analysisId: data.analysisId ?? data.analysis_id ?? data.id ?? null,
    analysis_id: data.analysis_id ?? data.analysisId ?? data.id ?? null,

    // timestamps / texts
    timestamp: data.timestamp ?? data.created_at ?? data.time ?? null,
    source_text: data.source_text ?? data.sourceText ?? data.source ?? '',
    target_text: data.target_text ?? data.targetText ?? data.target ?? '',
    sourceText: data.sourceText ?? data.source_text ?? data.source ?? '',
    targetText: data.targetText ?? data.target_text ?? data.target ?? '',

    // metrics (keep originals where present)
    semantic_preservation: data.semantic_preservation ?? data.semanticPreservation ?? data.semantic_score ?? data.semantic ?? null,
    readability_improvement: data.readability_improvement ?? data.readabilityImprovement ?? data.readability_delta ?? null,
    overall_score: data.overall_score ?? data.overallScore ?? data.score ?? null,

    // collections and nested structures
    simplification_strategies: data.simplification_strategies ?? data.simplificationStrategies ?? data.strategies ?? data.strategy_list ?? [],
    strategies: data.strategies ?? data.simplification_strategies ?? data.simplificationStrategies ?? [],
    strategies_count: data.strategies_count ?? data.strategiesCount ?? (data.simplification_strategies ? data.simplification_strategies.length : (data.strategies ? data.strategies.length : 0)),

    // detailed structures
    readability_metrics: data.readability_metrics ?? data.readabilityMetrics ?? data.readability ?? {},
    lexical_analysis: data.lexical_analysis ?? data.lexicalAnalysis ?? data.lexical ?? {},
    highlightedDifferences: data.highlightedDifferences ?? data.highlighted_differences ?? data.differences ?? [],
  };

  // Ensure strategies are in a frontend-friendly shape:
  if (Array.isArray(normalized.simplification_strategies)) {
    normalized.simplification_strategies = normalized.simplification_strategies.map((s = {}, idx) => {
      const examples = s.examples ?? s.exemplos ?? s.examples_list ?? [];
      const evidence = Array.isArray(examples)
        ? examples.map(ex => {
            const orig = ex.original ?? ex.before ?? ex.source ?? '';
            const simp = ex.simplified ?? ex.after ?? ex.target ?? '';
            return `${orig}${simp ? ' → ' + simp : ''}`.trim();
          }).filter(Boolean)
        : [];

      return Object.assign({}, s, {
        id: s.id ?? (s.name ? `${(s.name||'strategy').replace(/\s+/g, '_')}_${idx}` : `strategy_${idx}`),
        name: s.name ?? s.nome ?? s.label ?? '',
        confidence: typeof s.confidence === 'number' ? s.confidence : (parseFloat(s.confidence) || 0),
        evidence,
      });
    });
  }

  // Mirror into `strategies` for components that read that key
  if (!Array.isArray(normalized.strategies) || normalized.strategies.length === 0) {
    normalized.strategies = normalized.simplification_strategies || [];
  }

  // Normalize highlighted differences shape (backend may use source/target)
  const rawDiffs = normalized.highlightedDifferences ?? normalized.highlighted_differences ?? [];
  normalized.highlightedDifferences = (Array.isArray(rawDiffs) ? rawDiffs : []).map((d = {}) => {
    const src = d.source ?? d.original ?? d.before ?? '';
    const tgt = d.target ?? d.simplified ?? d.after ?? '';
    return {
      type: d.type ?? d.op ?? 'change',
      description: d.description ?? ((src || tgt) ? `${src}${tgt ? ' → ' + tgt : ''}` : d.text ?? ''),
      // keep raw fields for advanced components if needed
      source: src,
      target: tgt,
    };
  });
  // keep snake_case alias too
  normalized.highlighted_differences = normalized.highlightedDifferences;

  // If hierarchical tree exists, try to extract sentence/paragraph positions and micro evidence
  const tree = data.hierarchical_tree ?? data.hierarchicalTree ?? (data.hierarchical_analysis && data.hierarchical_analysis.hierarchical_tree) ?? [];
  if (Array.isArray(tree) && tree.length > 0) {
    // Build searchable index of sentences with paragraph role and indexes
    const paragraphIndex = tree.map((p, pIdx) => {
      const role = p.role ?? (p.paragraph_id && String(p.paragraph_id).startsWith('p-src') ? 'source' : (p.role || 'source'));
      const sentences = Array.isArray(p.sentences) ? p.sentences : [];
      return { pIdx, role, sentences };
    });

    const normalizeText = (t) => (t || '').toString().replace(/\s+/g, ' ').trim();

    const findMatch = (snippet) => {
      if (!snippet || typeof snippet !== 'string') return null;
      const s = normalizeText(snippet);
      if (!s) return null;
      for (const para of paragraphIndex) {
        for (let i = 0; i < para.sentences.length; i++) {
          const sent = para.sentences[i] || {};
          const text = normalizeText(sent.text || sent.source || sent.target || '');
          if (!text) continue;
          // substring match or reverse (example may be truncated)
          if (text.includes(s) || s.includes(text) || (text.length > 40 && s.length > 40 && text.slice(0,40) === s.slice(0,40))) {
            return { paragraphIndex: para.pIdx, sentence: i, role: para.role };
          }
        }
      }
      return null;
    };

    // Raw strategies array as returned by backend (may contain original examples)
    const rawStrategies = Array.isArray(data.simplification_strategies) ? data.simplification_strategies : (Array.isArray(data.strategies) ? data.strategies : []);

    // Augment each normalized strategy with positions and richer evidence
    normalized.simplification_strategies = (normalized.simplification_strategies || []).map((st, stIdx) => {
      const strat = Object.assign({}, st);
      strat.sourcePosition = strat.sourcePosition ?? null;
      strat.targetPosition = strat.targetPosition ?? null;
      strat.evidence = Array.isArray(strat.evidence) ? strat.evidence.slice() : [];

      // Try to find matching raw strategy entry to extract examples
      const rawMatch = rawStrategies.find(r => {
        const rname = (r && (r.name ?? r.nome ?? r.label ?? '')).toString();
        const sname = (st && st.name ? st.name.toString() : '');
        if (!rname && !sname) return false;
        return rname === sname || (sname && rname.includes(sname)) || (rname && sname.includes(rname));
      }) || {};

      const examples = rawMatch.examples ?? rawMatch.exemplos ?? rawMatch.examples_list ?? [];
      if (Array.isArray(examples) && examples.length > 0) {
        examples.forEach(ex => {
          const orig = normalizeText(ex.original ?? ex.before ?? ex.source ?? '');
          const simp = normalizeText(ex.simplified ?? ex.after ?? ex.target ?? '');
          if (orig) {
            const m = findMatch(orig);
            if (m && !strat.sourcePosition) strat.sourcePosition = m;
          }
          if (simp) {
            const m2 = findMatch(simp);
            if (m2 && !strat.targetPosition) strat.targetPosition = m2;
          }
          const ev = `${orig}${simp ? ' → ' + simp : ''}`.trim();
          if (ev) strat.evidence.push(ev);
        });
      }

      // If still missing positions, attempt to search the hierarchical tree for short probes from name/description
      if ((!strat.sourcePosition || !strat.targetPosition) && (rawMatch.name || rawMatch.description || st.description)) {
        const probe = normalizeText((rawMatch.name || rawMatch.description || st.description || '').toString()).split(/\s+/).slice(0,6).join(' ');
        const m = findMatch(probe);
        if (m) {
          if (!strat.sourcePosition && m.role === 'source') strat.sourcePosition = m;
          if (!strat.targetPosition && m.role === 'target') strat.targetPosition = m;
          // if role ambiguous, fill whichever missing
          if (!strat.sourcePosition) strat.sourcePosition = strat.sourcePosition || (m.role ? m : null);
          if (!strat.targetPosition) strat.targetPosition = strat.targetPosition || (m.role ? m : null);
        }
      }

      // Deduplicate evidence and ensure arrays exist
      strat.evidence = Array.from(new Set((strat.evidence || []).filter(Boolean)));

      return strat;
    });

    // Mirror into `strategies` as well for backward-compatible reads
    normalized.strategies = (Array.isArray(normalized.strategies) && normalized.strategies.length) ? normalized.strategies : normalized.simplification_strategies;
  }

  // Merge any other keys from original data that are not explicitly normalized
  return Object.assign({}, data, normalized);
}

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
        hierarchical_output: analysisData.hierarchical_output ?? false,
        salience_method: analysisData.salience_method,
        analysis_options: {
          include_lexical_analysis: true,
          include_syntactic_analysis: true,
            include_semantic_analysis: true,
          include_readability_metrics: true,
          include_strategy_identification: true,
          include_salience: analysisData.include_salience ?? true
        }
      });

      // Normalize backend response to ensure UI gets expected keys (snake_case & camelCase)
      const normalized = normalizeAnalysisResponse(response.data);

      return {
        success: true,
        ...normalized
      };
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
