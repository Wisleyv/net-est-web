/**
 * Enhanced Text Input Component with Visual Analysis
 * Integrates with SideBySideTextDisplay for comparative analysis
 */

import React, { useState, useCallback } from 'react';
import {
  AlertTriangle,
  X,
  Eye,
  EyeOff,
  Palette,
  Download,
  Settings
} from 'lucide-react';
import { STRATEGY_METADATA } from '../services/strategyColorMapping.js';
import config from '../services/config.js';
import TextInputField from './TextInputField';
import SideBySideTextDisplay from './SideBySideTextDisplay';
import InteractiveTextHighlighter from './InteractiveTextHighlighter';

const EnhancedTextInput = ({ onTextProcessed, onError }) => {
  const [sourceText, setSourceText] = useState('');
  const [targetText, setTargetText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [validationResults, setValidationResults] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [showVisualAnalysis, setShowVisualAnalysis] = useState(false);
  const [selectedStrategies, setSelectedStrategies] = useState(new Set());
  const [showSettings, setShowSettings] = useState(false);
  const [useInteractiveMode, setUseInteractiveMode] = useState(false);

  // Handle strategy updates for interactive mode
  const handleStrategyUpdate = (action, data) => {
    if (action === 'add' && data) {
      // Add new manually created strategy to the analysis result
      setAnalysisResult(prev => {
        if (!prev) return prev;
        
        const updatedStrategies = [...(prev.simplification_strategies || [])];
        
        // Create strategy entry that preserves position information
        const newStrategyEntry = {
          name: data.fullName || data.code, // Use the full name provided
          confidence: data.confidence,
          evidence: data.evidence,
          // Preserve position information for proper rendering
          targetPosition: data.targetPosition,
          sourcePosition: data.sourcePosition,
          isManual: true, // Mark as manually added
          id: data.id // Keep the unique ID
        };
        
        updatedStrategies.push(newStrategyEntry);
        
        return {
          ...prev,
          simplification_strategies: updatedStrategies
        };
      });
    }
  };

  // File type information (for supported formats display)

  const validateText = useCallback(async text => {
    if (!text.trim()) return null;

    try {
      const formData = new FormData();
      formData.append('text', text);

      const response = await fetch(
        `${config.API_BASE_URL}/api/v1/text-input/validate`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (response.ok) {
        return await response.json();
      } else {
        console.log('Validation API returned:', response.status, response.statusText);
        // Don't fail on validation errors, just return null
        return null;
      }
    } catch (error) {
      console.error('Validation error:', error);
      return null;
    }
  }, []);

  const handleTextChange = useCallback(
    async (text, isSource = true) => {
      console.log('handleTextChange called:', { 
        isSource, 
        textLength: text.length, 
        textPreview: text.substring(0, 50) + '...' 
      });
      
      if (isSource) {
        setSourceText(text);
        console.log('Source text updated, length:', text.length);
      } else {
        setTargetText(text);
        console.log('Target text updated, length:', text.length);
      }

      // Disabled automatic validation to avoid 422 errors
      // Validation will be done when processing the text
    },
    []
  );

  const runComparativeAnalysis = useCallback(async () => {
    console.log('runComparativeAnalysis started');
    
    if (!sourceText.trim() || !targetText.trim()) {
      console.log('Missing texts:', { source: !!sourceText.trim(), target: !!targetText.trim() });
      onError?.('Ambos os textos são necessários para análise comparativa');
      return;
    }

    console.log('Setting processing to true');
    setIsProcessing(true);

    try {
      const payload = {
        source_text: sourceText,
        target_text: targetText,
        analysis_options: {
          enable_om_detection: false, // OM+ disabled by default
          pro_tag_allowed: false // PRO+ manual only
        }
      };

      console.log('Sending request to backend with payload:', payload);

      const response = await fetch(
        `${config.API_BASE_URL}/api/v1/comparative-analysis/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        }
      );

      console.log('Backend response status:', response.status);
      const result = await response.json();
      console.log('Backend response data:', result);

      if (response.ok && result.analysis_id) {
        console.log('Analysis successful, setting results');
        setAnalysisResult(result);
        setShowVisualAnalysis(true);
        onTextProcessed?.(result);
      } else {
        console.log('Analysis failed. Response ok:', response.ok, 'Has analysis_id:', !!result.analysis_id);
        onError?.(result.error || 'Erro na análise comparativa');
      }
    } catch (error) {
      console.error('Comparative analysis error:', error);
      onError?.('Erro na comunicação com o servidor');
    } finally {
      console.log('Setting processing to false');
      setIsProcessing(false);
    }
  }, [sourceText, targetText, onTextProcessed, onError]);

  const processTypedText = useCallback(async () => {
    console.log('processTypedText called!', { sourceText: sourceText.length, targetText: targetText.length });
    
    if (!sourceText.trim()) {
      console.log('Source text is empty');
      onError?.('Texto de origem é obrigatório');
      return;
    }

    // If both texts are available, run comparative analysis
    if (targetText.trim()) {
      console.log('Both texts available, running comparative analysis');
      await runComparativeAnalysis();
      return;
    }

    console.log('Processing single text');
    setIsProcessing(true);

    try {
      // For single text processing, we'll validate and then wait for target text
      const validation = await validateText(sourceText);
      console.log('Validation result:', validation);
      
      if (validation) {
        setValidationResults(validation);
        setWarnings(validation.warnings || []);
        
        // Create a simple result for single text mode
        const result = {
          success: true,
          source_text: sourceText,
          message: 'Texto fonte processado. Adicione o texto alvo para análise comparativa.',
          warnings: validation.warnings || []
        };
        
        console.log('Calling onTextProcessed with result:', result);
        onTextProcessed?.(result);
      } else {
        console.log('Validation failed');
        onError?.('Não foi possível validar o texto');
      }
    } catch (error) {
      console.error('Processing error:', error);
      onError?.('Erro na comunicação com o servidor');
    } finally {
      setIsProcessing(false);
    }
  }, [sourceText, targetText, runComparativeAnalysis, validateText, onTextProcessed, onError]);

  const handleStrategyClick = (strategyCode) => {
    const newSelected = new Set(selectedStrategies);
    if (newSelected.has(strategyCode)) {
      newSelected.delete(strategyCode);
    } else {
      newSelected.add(strategyCode);
    }
    setSelectedStrategies(newSelected);
  };

  const clearResults = () => {
    setAnalysisResult(null);
    setShowVisualAnalysis(false);
    setSelectedStrategies(new Set());
  };

  const exportResults = () => {
    if (!analysisResult) return;

    const exportData = {
      timestamp: new Date().toISOString(),
      source_text: sourceText,
      target_text: targetText,
      analysis: analysisResult,
      settings: {
        selected_strategies: Array.from(selectedStrategies)
      }
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `net-est-analysis-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className='space-y-6'>
      {/* Input Section */}
      <div className='bg-white rounded-lg shadow-sm border p-6'>
        <div className='mb-6'>
          <div className='flex justify-between items-center mb-2'>
            <h2 className='text-xl font-semibold text-gray-900'>
              Análise Comparativa de Textos
            </h2>
            <div className='flex gap-2'>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className='p-2 text-gray-500 hover:text-gray-700 transition-colors'
                title='Configurações'
              >
                <Settings className='w-5 h-5' />
              </button>
              {analysisResult && (
                <>
                  <button
                    onClick={() => setShowVisualAnalysis(!showVisualAnalysis)}
                    className='p-2 text-blue-600 hover:text-blue-700 transition-colors'
                    title={showVisualAnalysis ? 'Ocultar análise visual' : 'Mostrar análise visual'}
                  >
                    {showVisualAnalysis ? <EyeOff className='w-5 h-5' /> : <Eye className='w-5 h-5' />}
                  </button>
                  <button
                    onClick={exportResults}
                    className='p-2 text-green-600 hover:text-green-700 transition-colors'
                    title='Exportar resultados'
                  >
                    <Download className='w-5 h-5' />
                  </button>
                  <button
                    onClick={clearResults}
                    className='p-2 text-red-600 hover:text-red-700 transition-colors'
                    title='Limpar resultados'
                  >
                    <X className='w-5 h-5' />
                  </button>
                </>
              )}
            </div>
          </div>
          <p className='text-gray-600 text-sm'>
            Digite ou carregue os textos para análise de estratégias de simplificação
          </p>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className='mb-6 p-4 bg-gray-50 rounded-lg border'>
            <h3 className='font-medium text-gray-900 mb-3'>Configurações de Análise</h3>
            <div className='space-y-3'>
              <div className='text-sm text-gray-600'>
                <p className='mb-2'>⚙️ Configurações avançadas serão implementadas em versões futuras:</p>
                <ul className='list-disc pl-6 space-y-1'>
                  <li>Seleção de estratégias específicas para análise</li>
                  <li>Priorização de tags na classificação</li>
                  <li>Ajustes de sensibilidade para detecção automática</li>
                  <li>Configurações de visualização personalizada</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Unified Input Interface */}
        <div className='space-y-6'>
          {/* Text Input Fields with File Support */}
          <div className='space-y-4'>
            <TextInputField
              label='Texto Fonte'
              value={sourceText}
              onChange={text => handleTextChange(text, true)}
              placeholder='Cole ou digite o texto fonte aqui...'
              required={true}
              height='h-32'
            />

            <TextInputField
              label='Texto Alvo'
              value={targetText}
              onChange={text => handleTextChange(text, false)}
              placeholder='Cole ou digite o texto alvo aqui...'
              required={false}
              height='h-32'
              helpText='Necessário para análise comparativa completa'
            />
          </div>

          {/* Process Button */}
          <button
            onClick={processTypedText}
            disabled={isProcessing || !sourceText.trim()}
            className='w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center font-medium'
          >
            {(() => {
              // Debug button state
              console.log('🔘 Button render:', {
                isProcessing,
                sourceTextLength: sourceText?.length || 0,
                sourceTextTrim: sourceText?.trim()?.length || 0,
                isDisabled: isProcessing || !sourceText.trim(),
                timestamp: new Date().toISOString()
              });
              return null;
            })()}
            {isProcessing ? (
              <>
                <div className='animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2'></div>
                {targetText.trim() ? 'Executando Análise Comparativa...' : 'Processando Texto...'}
              </>
            ) : (
              <>
                <Palette className='w-4 h-4 mr-2' />
                {targetText.trim() ? 'Analisar Estratégias de Simplificação' : 'Processar Texto'}
              </>
            )}
          </button>
        </div>

        {/* Validation Results */}
        {validationResults && (
          <div className='mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md'>
            <div className='text-sm'>
              <p className='font-medium text-blue-800 mb-1'>Análise do Texto:</p>
              <div className='text-blue-700 grid grid-cols-3 gap-4'>
                <div>
                  <span className='font-medium'>Caracteres:</span>{' '}
                  {validationResults.character_count.toLocaleString()}
                </div>
                <div>
                  <span className='font-medium'>Palavras:</span>{' '}
                  {validationResults.word_count.toLocaleString()}
                </div>
                <div>
                  <span className='font-medium'>Parágrafos:</span>{' '}
                  {validationResults.paragraph_count}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Warnings */}
        {warnings.length > 0 && (
          <div className='mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md'>
            <div className='flex items-start'>
              <AlertTriangle className='w-5 h-5 text-yellow-600 mt-0.5 mr-2 flex-shrink-0' />
              <div>
                <p className='text-sm font-medium text-yellow-800'>Avisos:</p>
                <ul className='text-sm text-yellow-700 mt-1 list-disc list-inside'>
                  {warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Supported Formats Info */}
        <div className='mt-4 p-3 bg-gray-50 rounded-md'>
          <p className='text-xs font-medium text-gray-700 mb-2'>
            Formatos suportados:
          </p>
          <div className='flex flex-wrap gap-2'>
            {[
              { ext: 'txt', name: 'Texto simples', icon: '📄' },
              { ext: 'md', name: 'Markdown', icon: '📝' },
              { ext: 'docx', name: 'Word Document', icon: '📘' },
              { ext: 'odt', name: 'OpenDocument Text', icon: '📄' },
              { ext: 'pdf', name: 'PDF Document', icon: '📕' }
            ].map(({ ext, name, icon }) => (
              <span
                key={ext}
                className='inline-flex items-center px-2 py-1 bg-white rounded text-xs text-gray-600 border'
              >
                <span className='mr-1'>{icon}</span>
                {name} (.{ext})
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Visual Analysis Section */}
      {showVisualAnalysis && analysisResult && (
        <div className="space-y-4">
          {/* Display Mode Toggle */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-medium text-gray-900">Análise Visual</h3>
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-600">Modo de Visualização:</span>
              <button
                onClick={() => setUseInteractiveMode(false)}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  !useInteractiveMode 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                📊 Análise Padrão
              </button>
              <button
                onClick={() => setUseInteractiveMode(true)}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  useInteractiveMode 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                🎯 Modo Interativo
              </button>
            </div>
          </div>

          {/* Display Component */}
          {useInteractiveMode ? (
            <InteractiveTextHighlighter
              sourceText={sourceText}
              targetText={targetText}
              analysisResult={analysisResult}
              onStrategyUpdate={handleStrategyUpdate}
            />
          ) : (
            <SideBySideTextDisplay
              sourceText={sourceText}
              targetText={targetText}
              analysisResult={analysisResult}
              useColorblindFriendly={false}
              onStrategyClick={handleStrategyClick}
              selectedStrategies={selectedStrategies}
              showStrategyLegend={true}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default EnhancedTextInput;

/*
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
*/
