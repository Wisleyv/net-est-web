/**
 * DualTextInputComponent.jsx - Phase 2.B.5 Implementation
 * Dual input system for source text and simplified translation comparison
 */

import React, { useState } from 'react';
import { Upload, FileText, Type, AlertCircle, CheckCircle2 } from 'lucide-react';
import useErrorHandler from '../hooks/useErrorHandler';
import api from '../services/api';

const DualTextInputComponent = ({ onComparativeAnalysis, className = "" }) => {
  const [sourceText, setSourceText] = useState('');
  const [targetText, setTargetText] = useState('');
  const [sourceFile, setSourceFile] = useState(null);
  const [targetFile, setTargetFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});

  const { handleError, handleSuccess } = useErrorHandler();

  // File upload handler
  const handleFileUpload = async (file, type) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/api/v1/comparative-analysis/upload-text', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const data = response.data;
      
      if (data.success) {
        if (type === 'source') {
          setSourceText(data.content);
          setSourceFile(file);
        } else {
          setTargetText(data.content);
          setTargetFile(file);
        }
        
        // Show validation information if available
        if (data.validation && data.validation.warnings.length > 0) {
          handleSuccess(
            `Arquivo ${type} carregado com sucesso! ` +
            `${data.validation.warnings.length} avisos encontrados.`
          );
        } else {
          handleSuccess(
            `Arquivo ${type} carregado com sucesso! ` +
            `${data.extracted_words} palavras extraídas.`
          );
        }
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      handleError(error, {
        component: 'DualTextInput',
        operation: `upload ${type} file`,
      });
    }
  };

  // Enhanced validation using comparative analysis validation
  const validateInputs = async () => {
    const errors = {};
    
    // Basic required field validation
    if (!sourceText.trim()) {
      errors.source = 'Texto fonte é obrigatório';
    } else if (sourceText.trim().length < 50) {
      errors.source = 'Texto fonte deve ter pelo menos 50 caracteres';
    }
    
    if (!targetText.trim()) {
      errors.target = 'Texto simplificado é obrigatório';
    } else if (targetText.trim().length < 20) {
      errors.target = 'Texto simplificado deve ter pelo menos 20 caracteres';
    }
    
    // If both texts are provided, do comprehensive validation
    if (sourceText.trim() && targetText.trim() && Object.keys(errors).length === 0) {
      try {
        const formData = new URLSearchParams();
        formData.append('source_text', sourceText.trim());
        formData.append('target_text', targetText.trim());
        
        const response = await api.post('/api/v1/comparative-analysis/validate-texts', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        });
        
        const validation = response.data;
        
        // Add warnings from comprehensive validation
        if (!validation.source_validation.is_valid) {
          errors.source = validation.source_validation.errors.join(', ');
        }
        
        if (!validation.target_validation.is_valid) {
          errors.target = validation.target_validation.errors.join(', ');
        }
        
        // Show comparative analysis warnings (but don't block submission)
        if (validation.combined_warnings && validation.combined_warnings.length > 0) {
          handleSuccess(
            `Validação concluída. ${validation.combined_warnings.length} recomendações encontradas: ` +
            validation.combined_warnings[0]
          );
        }
        
      } catch (validationError) {
        console.warn('Enhanced validation failed, using basic validation:', validationError);
        // Fall back to basic validation only
      }
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle comparative analysis
  const handleSubmit = async () => {
    const isValid = await validateInputs();
    if (!isValid) {
      handleError(new Error('Por favor, corrija os erros de validação'), {
        component: 'DualTextInput',
        operation: 'validation',
      });
      return;
    }

    setIsProcessing(true);
    
    try {
      const analysisData = {
        sourceText: sourceText.trim(),
        targetText: targetText.trim(),
        metadata: {
          sourceFile: sourceFile?.name,
          targetFile: targetFile?.name,
          timestamp: new Date().toISOString(),
        }
      };
      
      await onComparativeAnalysis(analysisData);
      handleSuccess('Análise comparativa iniciada com sucesso!');
    } catch (error) {
      handleError(error, {
        component: 'DualTextInput',
        operation: 'comparative analysis',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // Clear inputs
  const handleClear = () => {
    setSourceText('');
    setTargetText('');
    setSourceFile(null);
    setTargetFile(null);
    setValidationErrors({});
    handleSuccess('Campos limpos com sucesso!');
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
            <span className="text-white text-xs font-bold">2.5</span>
          </div>
          <div>
            <h3 className="font-medium text-blue-900">Análise Comparativa</h3>
            <p className="text-sm text-blue-800 mt-1">
              Compare um texto fonte com sua tradução intralingual simplificada para identificar estratégias de simplificação utilizadas.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Source Text Input */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-gray-600" />
            <h4 className="font-medium text-gray-900">Texto Fonte (Original)</h4>
            <span className="text-sm text-gray-500">• Complexo</span>
          </div>
          
          {/* Source File Upload */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-gray-400 transition-colors">
            <input
              type="file"
              id="source-file"
              accept=".txt,.md,.docx,.odt,.pdf"
              onChange={(e) => e.target.files[0] && handleFileUpload(e.target.files[0], 'source')}
              className="hidden"
            />
            <label htmlFor="source-file" className="cursor-pointer flex flex-col items-center gap-2">
              <Upload className="w-8 h-8 text-gray-400" />
              <span className="text-sm text-gray-600">
                {sourceFile ? sourceFile.name : 'Clique para carregar arquivo fonte'}
              </span>
              <span className="text-xs text-gray-500">TXT, MD, DOCX, ODT, PDF (máx. 10MB)</span>
            </label>
          </div>

          {/* Source Text Area */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">
                <Type className="inline w-4 h-4 mr-1" />
                Ou digite o texto fonte
              </label>
              <span className="text-xs text-gray-500">{sourceText.length} caracteres</span>
            </div>
            <textarea
              value={sourceText}
              onChange={(e) => setSourceText(e.target.value)}
              placeholder="Cole ou digite o texto original complexo aqui..."
              rows={8}
              className={`w-full p-3 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                validationErrors.source ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
            />
            {validationErrors.source && (
              <div className="flex items-center gap-1 text-sm text-red-600">
                <AlertCircle className="w-4 h-4" />
                {validationErrors.source}
              </div>
            )}
          </div>
        </div>

        {/* Target Text Input */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-green-600" />
            <h4 className="font-medium text-gray-900">Texto Simplificado (Tradução)</h4>
            <span className="text-sm text-green-600">• Simplificado</span>
          </div>
          
          {/* Target File Upload */}
          <div className="border-2 border-dashed border-green-300 rounded-lg p-4 hover:border-green-400 transition-colors">
            <input
              type="file"
              id="target-file"
              accept=".txt,.md,.docx,.odt,.pdf"
              onChange={(e) => e.target.files[0] && handleFileUpload(e.target.files[0], 'target')}
              className="hidden"
            />
            <label htmlFor="target-file" className="cursor-pointer flex flex-col items-center gap-2">
              <Upload className="w-8 h-8 text-green-400" />
              <span className="text-sm text-gray-600">
                {targetFile ? targetFile.name : 'Clique para carregar arquivo simplificado'}
              </span>
              <span className="text-xs text-gray-500">TXT, MD, DOCX, ODT, PDF (máx. 10MB)</span>
            </label>
          </div>

          {/* Target Text Area */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">
                <Type className="inline w-4 h-4 mr-1" />
                Ou digite o texto simplificado
              </label>
              <span className="text-xs text-gray-500">{targetText.length} caracteres</span>
            </div>
            <textarea
              value={targetText}
              onChange={(e) => setTargetText(e.target.value)}
              placeholder="Cole ou digite a versão simplificada do texto aqui..."
              rows={8}
              className={`w-full p-3 border rounded-lg resize-none focus:ring-2 focus:ring-green-500 focus:border-green-500 ${
                validationErrors.target ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
            />
            {validationErrors.target && (
              <div className="flex items-center gap-1 text-sm text-red-600">
                <AlertCircle className="w-4 h-4" />
                {validationErrors.target}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <div className="flex items-center gap-4">
          {sourceText && targetText && (
            <div className="flex items-center gap-1 text-sm text-green-600">
              <CheckCircle2 className="w-4 h-4" />
              Ambos os textos fornecidos
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={handleClear}
            disabled={isProcessing || (!sourceText && !targetText)}
            className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Limpar
          </button>
          
          <button
            onClick={handleSubmit}
            disabled={isProcessing || !sourceText || !targetText}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isProcessing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Analisando...
              </>
            ) : (
              <>
                <FileText className="w-4 h-4" />
                Iniciar Análise Comparativa
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DualTextInputComponent;
