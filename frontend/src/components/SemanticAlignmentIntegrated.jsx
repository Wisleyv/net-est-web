/**
 * Enhanced Semantic Alignment Component - Integrated with React Query and Zustand
 * Provides text simplification functionality with backend integration
 */

import React, { useState, useCallback, useEffect } from 'react';
import { 
  Target, 
  Shuffle, 
  CheckCircle, 
  AlertCircle, 
  Settings, 
  Loader,
  ArrowRight,
  BookOpen,
  Users,
  Brain
} from 'lucide-react';
import { useSemanticAlignment } from '../hooks/useSemanticAlignmentQueries';
import useAnalysisStore from '../stores/useAnalysisStore';
import useErrorHandler from '../hooks/useErrorHandler';
import ErrorBoundary from './common/ErrorBoundary';

const SemanticAlignmentIntegrated = ({ 
  inputText,
  onAlignmentComplete,
  className = '',
  disabled = false 
}) => {
  // Local state
  const [selectedLevel, setSelectedLevel] = useState('fundamental');
  const [customOptions, setCustomOptions] = useState({
    preserveFormatting: true,
    maintainStructure: true,
    includeExplanations: false,
  });
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);

  // Global state
  const { 
    currentAnalysis, 
    alignmentResult,
    isProcessing,
    processingStep,
    setAlignmentResult 
  } = useAnalysisStore();

  // Error handling
  const { handleError, handleSuccess, handleWarning } = useErrorHandler();

  // React Query mutation
  const alignmentMutation = useSemanticAlignment();

  // Education levels configuration
  const educationLevels = {
    elementary: {
      name: 'Ensino Fundamental',
      description: 'Linguagem simples para crianças e adolescentes (6-14 anos)',
      icon: <BookOpen className="w-5 h-5" />,
      color: 'bg-green-500',
      features: ['Vocabulário básico', 'Frases curtas', 'Exemplos cotidianos'],
    },
    middle: {
      name: 'Ensino Médio',
      description: 'Linguagem acessível para jovens (15-17 anos)',
      icon: <Users className="w-5 h-5" />,
      color: 'bg-blue-500',
      features: ['Vocabulário intermediário', 'Conceitos explicados', 'Contexto social'],
    },
    fundamental: {
      name: 'Adultos - Fundamental',
      description: 'Linguagem clara para adultos com educação básica',
      icon: <Target className="w-5 h-5" />,
      color: 'bg-purple-500',
      features: ['Termos cotidianos', 'Estrutura clara', 'Conceitos práticos'],
    },
    technical: {
      name: 'Técnico/Superior',
      description: 'Linguagem técnica para profissionais e estudantes superiores',
      icon: <Brain className="w-5 h-5" />,
      color: 'bg-orange-500',
      features: ['Termos técnicos', 'Conceitos complexos', 'Referências acadêmicas'],
    },
  };

  // Validate input text
  const hasValidInput = inputText && inputText.trim().length > 10;

  // Handle alignment processing
  const handleAlignment = useCallback(async () => {
    if (!hasValidInput) {
      handleWarning('Por favor, forneça um texto com pelo menos 10 caracteres para realizar o alinhamento semântico.');
      return;
    }

    try {
      const alignmentRequest = {
        text: inputText.trim(),
        targetLevel: selectedLevel,
        options: {
          preserveFormatting: customOptions.preserveFormatting,
          maintainStructure: customOptions.maintainStructure,
          includeExplanations: customOptions.includeExplanations,
          provideSummary: true,
          highlightChanges: true,
        },
      };

      const result = await alignmentMutation.mutateAsync(alignmentRequest);

      // Store result in global state
      setAlignmentResult(result);
      
      handleSuccess(
        `Texto alinhado com sucesso para o nível "${educationLevels[selectedLevel].name}"!`
      );
      
      onAlignmentComplete?.(result);

    } catch (error) {
      handleError(error, {
        component: 'SemanticAlignment',
        operation: 'realizar alinhamento semântico',
        context: `Nível: ${selectedLevel}`
      });
    }
  }, [
    inputText, 
    selectedLevel, 
    customOptions, 
    hasValidInput,
    alignmentMutation, 
    setAlignmentResult,
    handleError, 
    handleSuccess, 
    handleWarning,
    onAlignmentComplete,
    educationLevels
  ]);

  // Text statistics
  const getInputStats = () => {
    if (!inputText) return null;
    
    const words = inputText.trim().split(/\s+/).length;
    const sentences = inputText.split(/[.!?]+/).filter(s => s.trim()).length;
    const avgWordsPerSentence = Math.round(words / sentences);
    
    return { words, sentences, avgWordsPerSentence };
  };

  const inputStats = getInputStats();
  const isProcessingAlignment = isProcessing || alignmentMutation.isPending;

  return (
    <ErrorBoundary>
      <div className={`space-y-6 ${className}`}>
        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Target className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Alinhamento Semântico</h3>
            <p className="text-sm text-gray-600 mt-1">
              Adapte o texto para diferentes níveis de compreensão
            </p>
          </div>
        </div>

        {/* Input Statistics */}
        {inputStats && (
          <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">{inputStats.words}</div>
              <div className="text-xs text-gray-600">Palavras</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">{inputStats.sentences}</div>
              <div className="text-xs text-gray-600">Sentenças</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">{inputStats.avgWordsPerSentence}</div>
              <div className="text-xs text-gray-600">Palavras/Sentença</div>
            </div>
          </div>
        )}

        {/* Education Level Selection */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">
            Nível Educacional de Destino
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(educationLevels).map(([key, level]) => (
              <button
                key={key}
                onClick={() => setSelectedLevel(key)}
                disabled={disabled || isProcessingAlignment}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  selectedLevel === key
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                } ${(disabled || isProcessingAlignment) ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-sm'}`}
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-md text-white ${level.color}`}>
                    {level.icon}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{level.name}</div>
                    <div className="text-sm text-gray-600 mt-1">{level.description}</div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {level.features.map((feature, index) => (
                        <span
                          key={index}
                          className="inline-block px-2 py-1 bg-gray-100 text-xs text-gray-600 rounded"
                        >
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                  {selectedLevel === key && (
                    <CheckCircle className="w-5 h-5 text-purple-500 flex-shrink-0" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Advanced Options */}
        <div className="space-y-3">
          <button
            onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
            disabled={disabled || isProcessingAlignment}
            className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            <Settings className="w-4 h-4" />
            Opções Avançadas
            <Shuffle className={`w-3 h-3 transition-transform ${showAdvancedOptions ? 'rotate-180' : ''}`} />
          </button>

          {showAdvancedOptions && (
            <div className="p-4 bg-gray-50 rounded-lg space-y-3">
              <div className="space-y-2">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={customOptions.preserveFormatting}
                    onChange={(e) => setCustomOptions(prev => ({
                      ...prev,
                      preserveFormatting: e.target.checked
                    }))}
                    disabled={disabled || isProcessingAlignment}
                    className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-sm text-gray-700">Preservar formatação original</span>
                </label>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={customOptions.maintainStructure}
                    onChange={(e) => setCustomOptions(prev => ({
                      ...prev,
                      maintainStructure: e.target.checked
                    }))}
                    disabled={disabled || isProcessingAlignment}
                    className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-sm text-gray-700">Manter estrutura do texto</span>
                </label>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={customOptions.includeExplanations}
                    onChange={(e) => setCustomOptions(prev => ({
                      ...prev,
                      includeExplanations: e.target.checked
                    }))}
                    disabled={disabled || isProcessingAlignment}
                    className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-sm text-gray-700">Incluir explicações das mudanças</span>
                </label>
              </div>
            </div>
          )}
        </div>

        {/* Processing Status */}
        {isProcessingAlignment && (
          <div className="flex items-center gap-3 p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <Loader className="w-5 h-5 animate-spin text-purple-600" />
            <div className="flex-1">
              <div className="text-sm font-medium text-purple-900">
                Processando alinhamento semântico...
              </div>
              <div className="text-xs text-purple-700 mt-1">
                {processingStep === 'analyzing' && 'Analisando complexidade do texto...'}
                {processingStep === 'simplifying' && 'Simplificando vocabulário...'}
                {processingStep === 'formatting' && 'Ajustando formatação...'}
                {!processingStep && 'Preparando processamento...'}
              </div>
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="flex gap-3">
          <button
            onClick={handleAlignment}
            disabled={!hasValidInput || disabled || isProcessingAlignment}
            className="flex-1 bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 font-medium"
          >
            {alignmentMutation.isPending ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Processando Alinhamento...
              </>
            ) : (
              <>
                <Target className="w-5 h-5" />
                Realizar Alinhamento
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

        {/* Input Requirements */}
        {!hasValidInput && (
          <div className="flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-amber-800">
              <p className="font-medium">Texto insuficiente</p>
              <p className="mt-1">
                Por favor, forneça um texto com pelo menos 10 caracteres para realizar o alinhamento semântico.
              </p>
            </div>
          </div>
        )}

        {/* Alignment Result Preview */}
        {alignmentResult && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="font-medium text-green-900">Alinhamento Concluído</span>
            </div>
            <p className="text-sm text-green-800">
              Texto alinhado para o nível "{educationLevels[selectedLevel].name}" com sucesso. 
              Verifique os resultados na seção de saída.
            </p>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
};

export default SemanticAlignmentIntegrated;
