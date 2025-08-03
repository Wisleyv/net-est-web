/**
 * Enhanced Processed Text Display Component - Integrated with React Query and Zustand
 * Displays analysis results, alignment output, and provides interactive features
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  Copy,
  Download,
  Share2,
  Eye,
  EyeOff,
  BarChart3,
  CheckCircle,
  FileText,
  ArrowRight,
  RefreshCw,
  Edit3,
  Maximize2,
  Minimize2,
} from 'lucide-react';
import useAnalysisStore from '../stores/useAnalysisStore';
import useErrorHandler from '../hooks/useErrorHandler';
import ErrorBoundary from './common/ErrorBoundary';

const ProcessedTextDisplayIntegrated = ({
  className = '',
  showComparison = true,
  showStatistics = true,
  allowEdit = true,
  onTextEdit,
}) => {
  // Local state
  const [activeView, setActiveView] = useState('aligned');
  const [showOriginal, setShowOriginal] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState('');

  // Global state
  const {
    currentAnalysis,
    alignmentResult,
    preprocessingResults,
    isProcessing,
  } = useAnalysisStore();

  // Error handling
  const { handleSuccess, handleWarning, handleError } = useErrorHandler();

  // Computed values
  const hasResults = currentAnalysis || alignmentResult;
  const hasAlignmentResult = !!alignmentResult;
  const hasPreprocessingResult = !!preprocessingResults;

  // Get display data based on active view
  const displayData = useMemo(() => {
    if (!hasResults) return null;

    const baseData = {
      originalText: currentAnalysis?.originalText || '',
      inputType: currentAnalysis?.inputType || 'typed',
      fileName: currentAnalysis?.fileName || null,
      processedAt: currentAnalysis?.processedAt || new Date().toISOString(),
    };

    if (hasAlignmentResult) {
      return {
        ...baseData,
        alignedText: alignmentResult.alignedText,
        targetLevel: alignmentResult.targetLevel,
        statistics: alignmentResult.statistics,
        changes: alignmentResult.changes || [],
        explanations: alignmentResult.explanations || [],
        summary: alignmentResult.summary || '',
      };
    }

    if (hasPreprocessingResult) {
      return {
        ...baseData,
        preprocessedText: preprocessingResults.processedText,
        preprocessing: preprocessingResults.preprocessing || {},
        metadata: preprocessingResults.metadata || {},
      };
    }

    return baseData;
  }, [currentAnalysis, alignmentResult, preprocessingResults, hasResults, hasAlignmentResult, hasPreprocessingResult]);

  // Copy text to clipboard
  const handleCopyText = useCallback(async (text, label = 'texto') => {
    try {
      await navigator.clipboard.writeText(text);
      handleSuccess(`${label} copiado para a área de transferência!`);
    } catch (error) {
      handleError(error, {
        component: 'ProcessedTextDisplay',
        operation: 'copiar texto',
      });
    }
  }, [handleSuccess, handleError]);

  // Download text as file
  const handleDownloadText = useCallback((text, filename = 'texto-processado.txt') => {
    try {
      const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      handleSuccess(`Arquivo "${filename}" baixado com sucesso!`);
    } catch (error) {
      handleError(error, {
        component: 'ProcessedTextDisplay',
        operation: 'baixar texto',
      });
    }
  }, [handleSuccess, handleError]);

  // Share text (if Web Share API is available)
  const handleShareText = useCallback(async (text, title = 'Texto Processado') => {
    try {
      if (navigator.share) {
        await navigator.share({
          title,
          text,
        });
        handleSuccess('Texto compartilhado com sucesso!');
      } else {
        // Fallback to copy
        await handleCopyText(text, 'Link para compartilhamento');
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        handleError(error, {
          component: 'ProcessedTextDisplay',
          operation: 'compartilhar texto',
        });
      }
    }
  }, [handleCopyText, handleSuccess, handleError]);

  // Start editing
  const handleStartEdit = useCallback(() => {
    if (displayData?.alignedText) {
      setEditedText(displayData.alignedText);
      setIsEditing(true);
    }
  }, [displayData]);

  // Save edit
  const handleSaveEdit = useCallback(() => {
    if (editedText.trim() && onTextEdit) {
      onTextEdit(editedText.trim());
      setIsEditing(false);
      handleSuccess('Texto editado com sucesso!');
    } else {
      handleWarning('Por favor, insira um texto válido.');
    }
  }, [editedText, onTextEdit, handleSuccess, handleWarning]);

  // Cancel edit
  const handleCancelEdit = useCallback(() => {
    setIsEditing(false);
    setEditedText('');
  }, []);

  // Get statistics for display
  const getStatistics = () => {
    if (!displayData?.statistics) return [];

    const stats = [
      {
        label: 'Palavras Original',
        value: displayData.statistics.originalWordCount || 0,
        icon: <FileText className="w-4 h-4" />,
      },
      {
        label: 'Palavras Alinhado',
        value: displayData.statistics.alignedWordCount || 0,
        icon: <FileText className="w-4 h-4" />,
      },
      {
        label: 'Taxa de Simplificação',
        value: `${Math.round((displayData.statistics.simplificationRatio || 0) * 100)}%`,
        icon: <BarChart3 className="w-4 h-4" />,
      },
      {
        label: 'Pontuação de Legibilidade',
        value: Math.round(displayData.statistics.readabilityScore || 0),
        icon: <CheckCircle className="w-4 h-4" />,
      },
    ];

    return stats;
  };

  if (!hasResults) {
    return (
      <div className={`p-8 text-center text-gray-500 ${className}`}>
        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p className="text-lg font-medium mb-2">Nenhum resultado disponível</p>
        <p className="text-sm">
          Processe um texto ou carregue um arquivo para ver os resultados aqui.
        </p>
      </div>
    );
  }

  const statistics = getStatistics();

  return (
    <ErrorBoundary>
      <div className={`space-y-6 ${className}`}>
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <FileText className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Resultado do Processamento</h3>
              <p className="text-sm text-gray-600">
                {displayData?.fileName ? `Arquivo: ${displayData.fileName}` : 'Texto digitado'} • 
                {new Date(displayData?.processedAt).toLocaleString('pt-BR')}
              </p>
            </div>
          </div>
          
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 text-gray-500 hover:text-gray-700 rounded-md hover:bg-gray-100"
          >
            {isExpanded ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
          </button>
        </div>

        {/* Processing Status */}
        {isProcessing && (
          <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
            <span className="text-sm text-blue-700">Processando...</span>
          </div>
        )}

        {/* View Toggle */}
        {hasAlignmentResult && showComparison && (
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveView('aligned')}
              className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                activeView === 'aligned'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Texto Alinhado
            </button>
            <button
              onClick={() => setActiveView('comparison')}
              className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                activeView === 'comparison'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Comparação
            </button>
            {displayData?.explanations?.length > 0 && (
              <button
                onClick={() => setActiveView('explanations')}
                className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeView === 'explanations'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Explicações
              </button>
            )}
          </div>
        )}

        {/* Content Display */}
        <div className="space-y-4">
          {activeView === 'aligned' && (
            <div className="space-y-4">
              {/* Aligned Text */}
              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Texto Processado
                  {displayData?.targetLevel && (
                    <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                      Nível: {displayData.targetLevel}
                    </span>
                  )}
                </label>
                
                {isEditing ? (
                  <div className="space-y-3">
                    <textarea
                      value={editedText}
                      onChange={(e) => setEditedText(e.target.value)}
                      className="w-full min-h-[200px] p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
                      rows={8}
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={handleSaveEdit}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                      >
                        Salvar
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 text-sm"
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="relative p-4 bg-white border border-gray-200 rounded-lg">
                    <div className={`prose max-w-none ${isExpanded ? 'text-base' : 'text-sm'}`}>
                      {displayData?.alignedText || displayData?.preprocessedText || displayData?.originalText}
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="absolute top-2 right-2 flex gap-1">
                      {allowEdit && displayData?.alignedText && (
                        <button
                          onClick={handleStartEdit}
                          className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
                          title="Editar texto"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleCopyText(
                          displayData?.alignedText || displayData?.preprocessedText || displayData?.originalText,
                          'Texto processado'
                        )}
                        className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
                        title="Copiar texto"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDownloadText(
                          displayData?.alignedText || displayData?.preprocessedText || displayData?.originalText
                        )}
                        className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
                        title="Baixar texto"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleShareText(
                          displayData?.alignedText || displayData?.preprocessedText || displayData?.originalText
                        )}
                        className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
                        title="Compartilhar texto"
                      >
                        <Share2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeView === 'comparison' && hasAlignmentResult && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Original Text */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Texto Original
                  </label>
                  <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg min-h-[200px]">
                    <div className="text-sm text-gray-800 whitespace-pre-wrap">
                      {displayData?.originalText}
                    </div>
                  </div>
                </div>

                {/* Aligned Text */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Texto Alinhado
                  </label>
                  <div className="p-4 bg-white border border-gray-200 rounded-lg min-h-[200px]">
                    <div className="text-sm text-gray-800 whitespace-pre-wrap">
                      {displayData?.alignedText}
                    </div>
                  </div>
                </div>
              </div>

              {/* Comparison Arrow */}
              <div className="flex justify-center">
                <div className="flex items-center gap-2 px-4 py-2 bg-blue-100 rounded-full">
                  <ArrowRight className="w-4 h-4 text-blue-600" />
                  <span className="text-sm text-blue-800 font-medium">
                    Alinhamento Semântico
                  </span>
                </div>
              </div>
            </div>
          )}

          {activeView === 'explanations' && displayData?.explanations?.length > 0 && (
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">
                Explicações das Mudanças
              </label>
              <div className="space-y-2">
                {displayData.explanations.map((explanation, index) => (
                  <div key={index} className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-800">{explanation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Statistics */}
        {showStatistics && statistics.length > 0 && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
            {statistics.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="flex justify-center mb-2 text-gray-500">
                  {stat.icon}
                </div>
                <div className="text-lg font-semibold text-gray-900">{stat.value}</div>
                <div className="text-xs text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Summary */}
        {displayData?.summary && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <h4 className="font-medium text-green-900 mb-2">Resumo do Processamento</h4>
            <p className="text-sm text-green-800">{displayData.summary}</p>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
};

export default ProcessedTextDisplayIntegrated;
