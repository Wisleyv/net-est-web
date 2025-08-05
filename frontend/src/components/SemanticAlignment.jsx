import React, { useState, useEffect } from 'react';
import {
  ChevronDown,
  ChevronUp,
  Info,
  Zap,
  ArrowRightLeft,
  Settings,
} from 'lucide-react';
import FileUploadTextInput from './FileUploadTextInput';
import ComparativeAnalysisService from '../services/comparativeAnalysisService';

const SemanticAlignment = () => {
  const [sourceText, setSourceText] = useState('');
  const [targetText, setTargetText] = useState('');
  const [alignmentResult, setAlignmentResult] = useState(null);
  const [comparativeResult, setComparativeResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [config, setConfig] = useState({
    similarity_threshold: 0.7,
    alignment_method: 'cosine_similarity',
    max_alignments_per_source: 3,
  });
  const [showConfig, setShowConfig] = useState(false);
  const [availableMethods, setAvailableMethods] = useState({});

  // Fetch available methods on component mount
  useEffect(() => {
    fetchMethods();
  }, []);

  const fetchMethods = async () => {
    try {
      const response = await fetch(
        'http://localhost:8000/semantic-alignment/methods'
      );
      const data = await response.json();
      setAvailableMethods(data);
    } catch (err) {
      console.error('Error fetching methods:', err);
    }
  };

  const handleAlignment = async () => {
    if (!sourceText.trim() || !targetText.trim()) {
      setError('Por favor, forneça tanto o texto fonte quanto o texto alvo.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Split texts into paragraphs
      const sourceParagraphs = sourceText.split('\n').filter(p => p.trim());
      const targetParagraphs = targetText.split('\n').filter(p => p.trim());

      const response = await fetch(
        'http://localhost:8000/semantic-alignment/align',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            source_paragraphs: sourceParagraphs,
            target_paragraphs: targetParagraphs,
            similarity_threshold: config.similarity_threshold,
            alignment_method: config.alignment_method,
            max_alignments_per_source: config.max_alignments_per_source,
          }),
        }
      );

      const data = await response.json();

      if (data.success) {
        setAlignmentResult(data);
      } else {
        setError(data.errors?.join(', ') || 'Erro no alinhamento');
      }
    } catch (err) {
      setError(`Erro na requisição: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleComparativeAnalysis = async () => {
    if (!sourceText.trim() || !targetText.trim()) {
      setError('Por favor, forneça tanto o texto fonte quanto o texto alvo.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const analysisData = {
        sourceText: sourceText.trim(),
        targetText: targetText.trim(),
        metadata: {
          source_length: sourceText.length,
          target_length: targetText.length,
          timestamp: new Date().toISOString(),
        }
      };

      const result = await ComparativeAnalysisService.performComparativeAnalysis(analysisData);
      
      if (result.success) {
        setComparativeResult(result);
        setAlignmentResult(null); // Clear previous alignment results
      } else {
        setError(result.message || 'Erro na análise comparativa');
      }
    } catch (err) {
      setError(`Erro na análise: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = confidence => {
    switch (confidence) {
      case 'high':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-orange-600 bg-orange-100';
      default:
        return 'text-red-600 bg-red-100';
    }
  };

  const formatSimilarity = score => {
    return `${(score * 100).toFixed(1)}%`;
  };

  return (
    <div className='max-w-6xl mx-auto p-6 space-y-6'>
      <div className='bg-white rounded-lg shadow-lg p-6'>
        <div className='flex items-center gap-3 mb-6'>
          <ArrowRightLeft className='w-6 h-6 text-blue-600' />
          <h2 className='text-2xl font-bold text-gray-800'>
            Alinhamento Semântico
          </h2>
          <button
            onClick={() => setShowConfig(!showConfig)}
            className='ml-auto p-2 text-gray-600 hover:text-blue-600 rounded'
            title='Configurações'
          >
            <Settings className='w-5 h-5' />
          </button>
        </div>

        {/* Configuration Panel */}
        {showConfig && (
          <div className='mb-6 p-4 bg-gray-50 rounded-lg border'>
            <h3 className='text-lg font-medium mb-4'>
              Configurações de Alinhamento
            </h3>
            <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
              <div>
                <label className='block text-sm font-medium text-gray-700 mb-2'>
                  Método de Alinhamento
                </label>
                <select
                  value={config.alignment_method}
                  onChange={e =>
                    setConfig({ ...config, alignment_method: e.target.value })
                  }
                  className='w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'
                >
                  <option value='cosine_similarity'>
                    Similaridade de Cosseno
                  </option>
                  <option value='euclidean_distance'>
                    Distância Euclidiana
                  </option>
                  <option value='dot_product'>Produto Escalar</option>
                </select>
              </div>
              <div>
                <label className='block text-sm font-medium text-gray-700 mb-2'>
                  Limiar de Similaridade
                </label>
                <div className='flex items-center gap-2'>
                  <input
                    type='range'
                    min='0.1'
                    max='1.0'
                    step='0.05'
                    value={config.similarity_threshold}
                    onChange={e =>
                      setConfig({
                        ...config,
                        similarity_threshold: parseFloat(e.target.value),
                      })
                    }
                    className='flex-1'
                  />
                  <span className='text-sm font-medium w-12'>
                    {(config.similarity_threshold * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              <div>
                <label className='block text-sm font-medium text-gray-700 mb-2'>
                  Max. Alinhamentos por Fonte
                </label>
                <input
                  type='number'
                  min='1'
                  max='5'
                  value={config.max_alignments_per_source}
                  onChange={e =>
                    setConfig({
                      ...config,
                      max_alignments_per_source: parseInt(e.target.value),
                    })
                  }
                  className='w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'
                />
              </div>
            </div>
          </div>
        )}

        {/* Input Areas */}
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6'>
          <FileUploadTextInput
            label='Texto Fonte (Original)'
            placeholder='Digite ou carregue o texto original aqui. Separe parágrafos com quebras de linha.'
            value={sourceText}
            onChange={setSourceText}
            disabled={loading}
          />

          <FileUploadTextInput
            label='Texto Alvo (Simplificado)'
            placeholder='Digite ou carregue o texto simplificado aqui. Separe parágrafos com quebras de linha.'
            value={targetText}
            onChange={setTargetText}
            disabled={loading}
          />
        </div>

        {/* Error Display */}
        {error && (
          <div className='mb-4 p-4 bg-red-50 border border-red-200 rounded-md'>
            <div className='flex'>
              <div className='ml-3'>
                <h3 className='text-sm font-medium text-red-800'>Erro</h3>
                <div className='mt-2 text-sm text-red-700'>{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={handleAlignment}
            disabled={loading || !sourceText.trim() || !targetText.trim()}
            className='bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2'
          >
            {loading ? (
              <>
                <div className='animate-spin rounded-full h-4 w-4 border-b-2 border-white'></div>
                Processando Alinhamento...
              </>
            ) : (
              <>
                <Zap className='w-4 h-4' />
                Realizar Alinhamento Semântico
              </>
            )}
          </button>

          <button
            onClick={handleComparativeAnalysis}
            disabled={loading || !sourceText.trim() || !targetText.trim()}
            className='bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2'
          >
            {loading ? (
              <>
                <div className='animate-spin rounded-full h-4 w-4 border-b-2 border-white'></div>
                Analisando Comparação...
              </>
            ) : (
              <>
                <ArrowRightLeft className='w-4 h-4' />
                Análise Comparativa Completa
              </>
            )}
          </button>
        </div>
      </div>

      {/* Comparative Analysis Results */}
      {comparativeResult && (
        <div className='bg-white rounded-lg shadow-lg p-6 mb-6'>
          <h3 className='text-xl font-bold text-gray-800 mb-4'>
            Análise Comparativa Completa
          </h3>

          {/* Analysis Statistics */}
          <div className='grid grid-cols-2 md:grid-cols-4 gap-4 mb-6'>
            <div className='bg-blue-50 p-4 rounded-lg'>
              <div className='text-2xl font-bold text-blue-600'>
                {comparativeResult.statistics?.word_reduction_percentage?.toFixed(1) || 0}%
              </div>
              <div className='text-sm text-blue-600'>Redução de Palavras</div>
            </div>
            <div className='bg-green-50 p-4 rounded-lg'>
              <div className='text-2xl font-bold text-green-600'>
                {comparativeResult.statistics?.readability_improvement?.toFixed(2) || 0}
              </div>
              <div className='text-sm text-green-600'>Melhoria de Legibilidade</div>
            </div>
            <div className='bg-purple-50 p-4 rounded-lg'>
              <div className='text-2xl font-bold text-purple-600'>
                {comparativeResult.statistics?.complexity_reduction?.toFixed(1) || 0}%
              </div>
              <div className='text-sm text-purple-600'>Redução de Complexidade</div>
            </div>
            <div className='bg-orange-50 p-4 rounded-lg'>
              <div className='text-2xl font-bold text-orange-600'>
                {comparativeResult.statistics?.semantic_similarity?.toFixed(2) || 0}
              </div>
              <div className='text-sm text-orange-600'>Similaridade Semântica</div>
            </div>
          </div>

          {/* Simplification Strategies */}
          {comparativeResult.simplification_strategies && (
            <div className='mb-6'>
              <h4 className='text-lg font-semibold text-gray-800 mb-3'>
                Estratégias de Simplificação Identificadas
              </h4>
              <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
                {comparativeResult.simplification_strategies.map((strategy, index) => (
                  <div key={index} className='bg-gray-50 p-4 rounded-lg'>
                    <h5 className='font-medium text-gray-800 mb-2'>{strategy.name}</h5>
                    <p className='text-sm text-gray-600 mb-2'>{strategy.description}</p>
                    <div className='flex items-center justify-between text-xs'>
                      <span className='text-gray-500'>
                        Confiança: {(strategy.confidence * 100).toFixed(1)}%
                      </span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        strategy.impact === 'high' ? 'bg-red-100 text-red-700' :
                        strategy.impact === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {strategy.impact} impacto
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Analysis */}
          {comparativeResult.analysis && (
            <div className='space-y-4'>
              <div className='border-t pt-4'>
                <h4 className='text-lg font-semibold text-gray-800 mb-3'>
                  Análise Detalhada
                </h4>
                <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
                  <div>
                    <h5 className='font-medium text-gray-700 mb-2'>Métricas Lexicais</h5>
                    <div className='space-y-2 text-sm'>
                      <div className='flex justify-between'>
                        <span>Palavras únicas fonte:</span>
                        <span>{comparativeResult.analysis.lexical?.source_unique_words || 0}</span>
                      </div>
                      <div className='flex justify-between'>
                        <span>Palavras únicas alvo:</span>
                        <span>{comparativeResult.analysis.lexical?.target_unique_words || 0}</span>
                      </div>
                      <div className='flex justify-between'>
                        <span>Palavras compartilhadas:</span>
                        <span>{comparativeResult.analysis.lexical?.shared_words || 0}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h5 className='font-medium text-gray-700 mb-2'>Métricas de Legibilidade</h5>
                    <div className='space-y-2 text-sm'>
                      <div className='flex justify-between'>
                        <span>Flesch Reading Ease (fonte):</span>
                        <span>{comparativeResult.analysis.readability?.source_flesch?.toFixed(1) || 0}</span>
                      </div>
                      <div className='flex justify-between'>
                        <span>Flesch Reading Ease (alvo):</span>
                        <span>{comparativeResult.analysis.readability?.target_flesch?.toFixed(1) || 0}</span>
                      </div>
                      <div className='flex justify-between'>
                        <span>Melhoria:</span>
                        <span className='text-green-600'>
                          +{((comparativeResult.analysis.readability?.target_flesch || 0) - 
                              (comparativeResult.analysis.readability?.source_flesch || 0)).toFixed(1)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Alignment Results */}
      {alignmentResult && (
        <div className='bg-white rounded-lg shadow-lg p-6'>
          <h3 className='text-xl font-bold text-gray-800 mb-4'>
            Resultados do Alinhamento
          </h3>

          {/* Statistics */}
          <div className='grid grid-cols-2 md:grid-cols-4 gap-4 mb-6'>
            <div className='bg-blue-50 p-4 rounded-lg'>
              <div className='text-2xl font-bold text-blue-600'>
                {alignmentResult.alignment_result.aligned_pairs.length}
              </div>
              <div className='text-sm text-blue-600'>Pares Alinhados</div>
            </div>
            <div className='bg-green-50 p-4 rounded-lg'>
              <div className='text-2xl font-bold text-green-600'>
                {formatSimilarity(
                  alignmentResult.alignment_result.alignment_stats
                    .alignment_rate_source
                )}
              </div>
              <div className='text-sm text-green-600'>Taxa Alinhamento</div>
            </div>
            <div className='bg-purple-50 p-4 rounded-lg'>
              <div className='text-2xl font-bold text-purple-600'>
                {formatSimilarity(
                  alignmentResult.alignment_result.alignment_stats
                    .average_similarity
                )}
              </div>
              <div className='text-sm text-purple-600'>Similaridade Média</div>
            </div>
            <div className='bg-orange-50 p-4 rounded-lg'>
              <div className='text-2xl font-bold text-orange-600'>
                {(
                  alignmentResult.alignment_result.alignment_stats
                    .processing_time_seconds * 1000
                ).toFixed(0)}
                ms
              </div>
              <div className='text-sm text-orange-600'>Tempo Processamento</div>
            </div>
          </div>

          {/* Aligned Pairs */}
          {alignmentResult.alignment_result.aligned_pairs.length > 0 && (
            <div className='mb-6'>
              <h4 className='text-lg font-semibold text-gray-800 mb-3'>
                Pares Alinhados
              </h4>
              <div className='space-y-4'>
                {alignmentResult.alignment_result.aligned_pairs.map(
                  (pair, index) => (
                    <div
                      key={index}
                      className='border border-gray-200 rounded-lg p-4'
                    >
                      <div className='flex items-center justify-between mb-3'>
                        <div className='flex items-center gap-2'>
                          <span className='text-sm font-medium text-gray-600'>
                            Par {index + 1} (Fonte #{pair.source_index + 1} →
                            Alvo #{pair.target_index + 1})
                          </span>
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(pair.confidence)}`}
                          >
                            {pair.confidence === 'high'
                              ? 'Alta'
                              : pair.confidence === 'medium'
                                ? 'Média'
                                : pair.confidence === 'low'
                                  ? 'Baixa'
                                  : 'Muito Baixa'}
                          </span>
                        </div>
                        <div className='text-sm font-medium text-gray-800'>
                          {formatSimilarity(pair.similarity_score)}
                        </div>
                      </div>
                      <div className='grid grid-cols-1 lg:grid-cols-2 gap-4'>
                        <div className='bg-blue-50 p-3 rounded'>
                          <div className='text-sm font-medium text-blue-800 mb-1'>
                            Original
                          </div>
                          <div className='text-sm text-gray-700'>
                            {pair.source_text}
                          </div>
                        </div>
                        <div className='bg-green-50 p-3 rounded'>
                          <div className='text-sm font-medium text-green-800 mb-1'>
                            Simplificado
                          </div>
                          <div className='text-sm text-gray-700'>
                            {pair.target_text}
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          {/* Unaligned Paragraphs */}
          {(alignmentResult.alignment_result.unaligned_source_details.length >
            0 ||
            alignmentResult.alignment_result.unaligned_target_details.length >
              0) && (
            <div>
              <h4 className='text-lg font-semibold text-gray-800 mb-3'>
                Parágrafos Não Alinhados
              </h4>
              <div className='grid grid-cols-1 lg:grid-cols-2 gap-4'>
                {alignmentResult.alignment_result.unaligned_source_details
                  .length > 0 && (
                  <div>
                    <h5 className='text-md font-medium text-gray-700 mb-2'>
                      Texto Fonte
                    </h5>
                    <div className='space-y-2'>
                      {alignmentResult.alignment_result.unaligned_source_details.map(
                        (item, index) => (
                          <div
                            key={index}
                            className='bg-red-50 border border-red-200 p-3 rounded'
                          >
                            <div className='flex items-center justify-between mb-2'>
                              <span className='text-sm font-medium text-red-800'>
                                Parágrafo #{item.index + 1}
                              </span>
                              <span className='text-xs text-red-600'>
                                Melhor:{' '}
                                {formatSimilarity(item.nearest_similarity)}
                              </span>
                            </div>
                            <div className='text-sm text-gray-700'>
                              {item.text}
                            </div>
                            <div className='text-xs text-red-600 mt-1'>
                              {item.reason}
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {alignmentResult.alignment_result.unaligned_target_details
                  .length > 0 && (
                  <div>
                    <h5 className='text-md font-medium text-gray-700 mb-2'>
                      Texto Alvo
                    </h5>
                    <div className='space-y-2'>
                      {alignmentResult.alignment_result.unaligned_target_details.map(
                        (item, index) => (
                          <div
                            key={index}
                            className='bg-red-50 border border-red-200 p-3 rounded'
                          >
                            <div className='flex items-center justify-between mb-2'>
                              <span className='text-sm font-medium text-red-800'>
                                Parágrafo #{item.index + 1}
                              </span>
                              <span className='text-xs text-red-600'>
                                Melhor:{' '}
                                {formatSimilarity(item.nearest_similarity)}
                              </span>
                            </div>
                            <div className='text-sm text-gray-700'>
                              {item.text}
                            </div>
                            <div className='text-xs text-red-600 mt-1'>
                              {item.reason}
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SemanticAlignment;
