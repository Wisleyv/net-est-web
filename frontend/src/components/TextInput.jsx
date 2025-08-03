/**
 * Text Input Component for NET-EST System
 * Handles both typed text and file upload inputs
 */

import React, { useState, useCallback, useRef } from 'react';
import {
  Upload,
  Type,
  FileText,
  AlertTriangle,
  CheckCircle,
  X,
} from 'lucide-react';
import TextInputField from './TextInputField';

const TextInput = ({ onTextProcessed, onError }) => {
  const [activeTab, setActiveTab] = useState('type'); // 'type' or 'file'
  const [sourceText, setSourceText] = useState('');
  const [targetText, setTargetText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [validationResults, setValidationResults] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const fileInputRef = useRef(null);

  // File type information
  const supportedFormats = {
    txt: { name: 'Texto simples', icon: '📄' },
    md: { name: 'Markdown', icon: '📝' },
    docx: { name: 'Word Document', icon: '📘' },
    odt: { name: 'OpenDocument Text', icon: '📄' },
    pdf: { name: 'PDF Document', icon: '📕' },
  };

  const validateText = useCallback(async text => {
    if (!text.trim()) return null;

    try {
      const response = await fetch(
        'http://localhost:8000/api/v1/text-input/validate',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: `text=${encodeURIComponent(text)}`,
        }
      );

      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Validation error:', error);
    }
    return null;
  }, []);

  const handleTextChange = useCallback(
    async (text, isSource = true) => {
      if (isSource) {
        setSourceText(text);
      } else {
        setTargetText(text);
      }

      // Debounced validation
      if (text.length > 100) {
        const results = await validateText(text);
        if (results && isSource) {
          setValidationResults(results);
          setWarnings(results.warnings || []);
        }
      }
    },
    [validateText]
  );

  const handleFileSelection = useCallback(
    async event => {
      const file = event.target.files[0];
      if (!file) return;

      setSelectedFile(file);
      setWarnings([]);

      // Get file info
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(
          'http://localhost:8000/api/v1/text-input/file-info',
          {
            method: 'POST',
            body: formData,
          }
        );

        if (response.ok) {
          const fileInfo = await response.json();
          setWarnings(fileInfo.warnings || []);

          if (!fileInfo.supported) {
            onError?.('Formato de arquivo não suportado');
            setSelectedFile(null);
            return;
          }
        }
      } catch (error) {
        console.error('File info error:', error);
        onError?.('Erro ao analisar arquivo');
      }
    },
    [onError]
  );

  const processTypedText = useCallback(async () => {
    if (!sourceText.trim()) {
      onError?.('Texto de origem é obrigatório');
      return;
    }

    setIsProcessing(true);

    try {
      const formData = new URLSearchParams();
      formData.append('source_text', sourceText);
      if (targetText.trim()) {
        formData.append('target_text', targetText);
      }

      const response = await fetch(
        'http://localhost:8000/api/v1/text-input/process-typed',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: formData.toString(),
        }
      );

      const result = await response.json();

      if (result.success) {
        onTextProcessed?.(result);
        setWarnings(result.warnings || []);
      } else {
        onError?.(result.errors?.join(', ') || 'Erro no processamento');
      }
    } catch (error) {
      console.error('Processing error:', error);
      onError?.('Erro na comunicação com o servidor');
    } finally {
      setIsProcessing(false);
    }
  }, [sourceText, targetText, onTextProcessed, onError]);

  const processFileUpload = useCallback(async () => {
    if (!selectedFile) {
      onError?.('Selecione um arquivo');
      return;
    }

    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (targetText.trim()) {
        formData.append('target_text', targetText);
      }

      const response = await fetch(
        'http://localhost:8000/api/v1/text-input/process-file',
        {
          method: 'POST',
          body: formData,
        }
      );

      const result = await response.json();

      if (result.success) {
        onTextProcessed?.(result);
        setWarnings(result.warnings || []);
      } else {
        onError?.(
          result.errors?.join(', ') || 'Erro no processamento do arquivo'
        );
      }
    } catch (error) {
      console.error('File processing error:', error);
      onError?.('Erro no processamento do arquivo');
    } finally {
      setIsProcessing(false);
    }
  }, [selectedFile, targetText, onTextProcessed, onError]);

  const clearFile = () => {
    setSelectedFile(null);
    setWarnings([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getCharacterCount = text => text.length;
  const getWordCount = text =>
    text
      .trim()
      .split(/\s+/)
      .filter(word => word.length > 0).length;

  return (
    <div className='bg-white rounded-lg shadow-sm border p-6'>
      <div className='mb-6'>
        <h2 className='text-xl font-semibold text-gray-900 mb-2'>
          Entrada de Texto
        </h2>
        <p className='text-gray-600 text-sm'>
          Digite ou carregue os textos para análise de tradução intralinguística
        </p>
      </div>

      {/* Tab Navigation */}
      <div className='flex space-x-1 bg-gray-100 rounded-lg p-1 mb-6'>
        <button
          onClick={() => setActiveTab('type')}
          className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'type'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Type className='w-4 h-4 mr-2' />
          Digitar Texto
        </button>
        <button
          onClick={() => setActiveTab('file')}
          className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'file'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Upload className='w-4 h-4 mr-2' />
          Carregar Arquivo
        </button>
      </div>

      {/* Warnings Display */}
      {warnings.length > 0 && (
        <div className='mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md'>
          <div className='flex items-start'>
            <AlertTriangle className='w-5 h-5 text-yellow-400 mt-0.5 mr-2 flex-shrink-0' />
            <div className='text-sm'>
              <p className='font-medium text-yellow-800 mb-1'>Avisos:</p>
              <ul className='text-yellow-700 space-y-1'>
                {warnings.map((warning, index) => (
                  <li key={index}>• {warning}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Type Text Tab */}
      {activeTab === 'type' && (
        <div className='space-y-4'>
          <TextInputField
            label='Texto de Origem'
            placeholder='Digite ou carregue o texto original aqui...'
            required={true}
            value={sourceText}
            onChange={setSourceText}
            disabled={isProcessing}
          />

          <TextInputField
            label='Texto de Destino (opcional)'
            placeholder='Digite ou carregue o texto simplificado aqui (opcional)...'
            required={false}
            value={targetText}
            onChange={setTargetText}
            disabled={isProcessing}
          />

          <button
            onClick={processTypedText}
            disabled={isProcessing || !sourceText.trim()}
            className='w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center'
          >
            {isProcessing ? (
              <>
                <div className='animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2'></div>
                Processando...
              </>
            ) : (
              <>
                <CheckCircle className='w-4 h-4 mr-2' />
                Processar Texto
              </>
            )}
          </button>
        </div>
      )}

      {/* File Upload Tab */}
      {activeTab === 'file' && (
        <div className='space-y-4'>
          <div>
            <label className='block text-sm font-medium text-gray-700 mb-2'>
              Arquivo de Origem *
            </label>

            {!selectedFile ? (
              <div
                onClick={() => fileInputRef.current?.click()}
                className='border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors'
              >
                <Upload className='w-8 h-8 text-gray-400 mx-auto mb-2' />
                <p className='text-sm text-gray-600 mb-1'>
                  Clique para selecionar um arquivo
                </p>
                <p className='text-xs text-gray-500'>
                  Formatos suportados: TXT, MD, DOCX, ODT, PDF
                </p>
              </div>
            ) : (
              <div className='border border-gray-300 rounded-lg p-4'>
                <div className='flex items-center justify-between'>
                  <div className='flex items-center'>
                    <FileText className='w-5 h-5 text-blue-500 mr-2' />
                    <div>
                      <p className='text-sm font-medium text-gray-900'>
                        {selectedFile.name}
                      </p>
                      <p className='text-xs text-gray-500'>
                        {(selectedFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={clearFile}
                    className='text-gray-400 hover:text-red-500'
                  >
                    <X className='w-4 h-4' />
                  </button>
                </div>
              </div>
            )}

            <input
              ref={fileInputRef}
              type='file'
              accept='.txt,.md,.docx,.odt,.pdf'
              onChange={handleFileSelection}
              className='hidden'
            />
          </div>

          <div>
            <label className='block text-sm font-medium text-gray-700 mb-2'>
              Texto de Destino (opcional)
            </label>
            <textarea
              value={targetText}
              onChange={e => setTargetText(e.target.value)}
              placeholder='Cole ou digite o texto simplificado aqui (opcional)...'
              className='w-full h-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none'
            />
          </div>

          <button
            onClick={processFileUpload}
            disabled={isProcessing || !selectedFile}
            className='w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center'
          >
            {isProcessing ? (
              <>
                <div className='animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2'></div>
                Processando Arquivo...
              </>
            ) : (
              <>
                <Upload className='w-4 h-4 mr-2' />
                Processar Arquivo
              </>
            )}
          </button>
        </div>
      )}

      {/* Validation Results */}
      {validationResults && activeTab === 'type' && (
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

      {/* Supported Formats Info */}
      {activeTab === 'file' && (
        <div className='mt-4 p-3 bg-gray-50 rounded-md'>
          <p className='text-xs font-medium text-gray-700 mb-2'>
            Formatos suportados:
          </p>
          <div className='flex flex-wrap gap-2'>
            {Object.entries(supportedFormats).map(([ext, info]) => (
              <span
                key={ext}
                className='inline-flex items-center px-2 py-1 bg-white rounded text-xs text-gray-600 border'
              >
                <span className='mr-1'>{info.icon}</span>
                {info.name} (.{ext})
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TextInput;
