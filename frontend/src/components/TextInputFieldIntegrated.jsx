/**
 * Enhanced Text Input Field Component - Integrated with React Query and Zustand
 * Supports both typed text and file upload with backend integration
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Upload, Type, FileText, AlertTriangle, X, Loader } from 'lucide-react';
import { useProcessTypedText, useProcessFileUpload } from '../hooks/useTextInputQueries';
import useAnalysisStore from '../stores/useAnalysisStore';
import useErrorHandler from '../hooks/useErrorHandler';
import ErrorBoundary from './common/ErrorBoundary';

const TextInputFieldIntegrated = ({
  label = 'Entrada de Texto',
  placeholder = 'Digite ou cole seu texto aqui...',
  required = false,
  disabled = false,
  onProcessingComplete,
  className = '',
}) => {
  // Local component state
  const [activeTab, setActiveTab] = useState('type');
  const [textInput, setTextInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const fileInputRef = useRef(null);

  // Global state
  const { 
    currentAnalysis, 
    isProcessing, 
    processingStep,
    processingError 
  } = useAnalysisStore();

  // Error handling
  const { handleError, handleSuccess, handleWarning } = useErrorHandler();

  // React Query mutations
  const processTypedTextMutation = useProcessTypedText();
  const processFileUploadMutation = useProcessFileUpload();

  // File type information
  const supportedFormats = {
    txt: { name: 'Texto simples', icon: '📄' },
    md: { name: 'Markdown', icon: '📝' },
    docx: { name: 'Word Document', icon: '📘' },
    odt: { name: 'OpenDocument Text', icon: '📄' },
    pdf: { name: 'PDF Document', icon: '📕' },
  };

  // Reset warnings when switching tabs
  useEffect(() => {
    setWarnings([]);
  }, [activeTab]);

  // Handle typed text processing
  const handleProcessTypedText = useCallback(async () => {
    if (!textInput.trim()) {
      handleWarning('Por favor, digite algum texto antes de processar.');
      return;
    }

    try {
      const result = await processTypedTextMutation.mutateAsync({
        text: textInput.trim(),
        options: {
          clean_whitespace: true,
          validate_encoding: true,
        }
      });

      handleSuccess('Texto processado com sucesso!');
      onProcessingComplete?.(result);
      
    } catch (error) {
      handleError(error, {
        component: 'TextInputField',
        operation: 'processar texto digitado'
      });
    }
  }, [textInput, processTypedTextMutation, handleError, handleSuccess, handleWarning, onProcessingComplete]);

  // Handle file upload and processing
  const handleFileUpload = useCallback(async (file) => {
    if (!file) return;

    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    
    if (!supportedFormats[fileExtension]) {
      handleWarning(
        `Formato de arquivo não suportado: .${fileExtension}`,
        'Formato Inválido'
      );
      return;
    }

    // File size validation (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      handleWarning(
        'Arquivo muito grande. O tamanho máximo é 10MB.',
        'Arquivo Grande'
      );
      return;
    }

    try {
      const result = await processFileUploadMutation.mutateAsync({
        file,
        options: {
          preserve_formatting: true,
          extract_metadata: true,
        }
      });

      handleSuccess(`Arquivo "${file.name}" processado com sucesso!`);
      onProcessingComplete?.(result);
      
    } catch (error) {
      handleError(error, {
        component: 'TextInputField',
        operation: 'processar arquivo'
      });
    }
  }, [processFileUploadMutation, handleError, handleSuccess, handleWarning, onProcessingComplete]);

  // File selection handler
  const handleFileSelect = useCallback((event) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      handleFileUpload(file);
    }
  }, [handleFileUpload]);

  // Clear file selection
  const clearFile = useCallback(() => {
    setSelectedFile(null);
    setWarnings([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  // Text statistics
  const getTextStats = (text) => ({
    characters: text?.length || 0,
    words: text?.trim().split(/\s+/).filter(word => word.length > 0).length || 0,
    paragraphs: text?.split('\n').filter(p => p.trim()).length || 0,
  });

  const textStats = getTextStats(textInput);
  const isCurrentlyProcessing = isProcessing || processTypedTextMutation.isPending || processFileUploadMutation.isPending;

  return (
    <ErrorBoundary>
      <div className={`space-y-4 ${className}`}>
        {/* Label */}
        <label className="block text-sm font-medium text-gray-700">
          {label} {required && <span className="text-red-500">*</span>}
        </label>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('type')}
            disabled={disabled || isCurrentlyProcessing}
            className={`flex-1 flex items-center justify-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'type'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            } ${(disabled || isCurrentlyProcessing) ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <Type className="w-4 h-4 mr-2" />
            Digitar Texto
          </button>
          <button
            onClick={() => setActiveTab('file')}
            disabled={disabled || isCurrentlyProcessing}
            className={`flex-1 flex items-center justify-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'file'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            } ${(disabled || isCurrentlyProcessing) ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <Upload className="w-4 h-4 mr-2" />
            Carregar Arquivo
          </button>
        </div>

        {/* Processing Status */}
        {isCurrentlyProcessing && (
          <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <Loader className="w-4 h-4 animate-spin text-blue-600" />
            <span className="text-sm text-blue-700">
              {processingStep === 'preprocessing' ? 'Processando texto...' : 'Processando...'}
            </span>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'type' && (
          <div className="space-y-3">
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder={placeholder}
              disabled={disabled || isCurrentlyProcessing}
              className="w-full min-h-[200px] p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
              rows={8}
            />
            
            {/* Text Statistics */}
            {textInput && (
              <div className="flex justify-between text-xs text-gray-500 bg-gray-50 px-3 py-2 rounded">
                <span>{textStats.characters} caracteres</span>
                <span>{textStats.words} palavras</span>
                <span>{textStats.paragraphs} parágrafos</span>
              </div>
            )}

            {/* Process Button */}
            <button
              onClick={handleProcessTypedText}
              disabled={!textInput.trim() || disabled || isCurrentlyProcessing}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {processTypedTextMutation.isPending ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Processando...
                </>
              ) : (
                'Processar Texto'
              )}
            </button>
          </div>
        )}

        {activeTab === 'file' && (
          <div className="space-y-3">
            {/* File Upload Area */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                accept=".txt,.md,.docx,.odt,.pdf"
                disabled={disabled || isCurrentlyProcessing}
                className="hidden"
              />
              
              {selectedFile ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-center gap-2">
                    <FileText className="w-8 h-8 text-blue-500" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900">{selectedFile.name}</p>
                      <p className="text-sm text-gray-500">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <button
                      onClick={clearFile}
                      disabled={isCurrentlyProcessing}
                      className="ml-2 text-gray-400 hover:text-gray-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  
                  {processFileUploadMutation.isPending && (
                    <div className="flex items-center justify-center gap-2 text-blue-600">
                      <Loader className="w-4 h-4 animate-spin" />
                      <span className="text-sm">Processando arquivo...</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                  <div>
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={disabled || isCurrentlyProcessing}
                      className="font-medium text-blue-600 hover:text-blue-500 disabled:text-gray-400"
                    >
                      Clique para selecionar um arquivo
                    </button>
                    <p className="text-sm text-gray-500">ou arraste e solte aqui</p>
                  </div>
                </div>
              )}
            </div>

            {/* Supported Formats */}
            <div className="text-xs text-gray-500">
              <p className="font-medium mb-1">Formatos suportados:</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(supportedFormats).map(([ext, info]) => (
                  <span key={ext} className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded">
                    <span>{info.icon}</span>
                    <span>.{ext}</span>
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Warnings Display */}
        {warnings.length > 0 && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <div className="flex items-start">
              <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 mr-2 flex-shrink-0" />
              <div className="flex-1">
                {warnings.map((warning, index) => (
                  <p key={index} className="text-sm text-yellow-800">
                    {warning}
                  </p>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
};

export default TextInputFieldIntegrated;
