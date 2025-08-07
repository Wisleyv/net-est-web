/**
 * Reusable Text Input Field Component
 * Supports both typed text and file upload with consistent interface
 * Updated: Fixed compilation issues
 */

import React, { useState, useCallback, useRef } from 'react';
import { Upload, Type, FileText, AlertTriangle, X } from 'lucide-react';

const TextInputField = ({
  label,
  placeholder,
  required = false,
  value,
  onChange,
  disabled = false,
}) => {
  const [activeTab, setActiveTab] = useState('type'); // 'type' or 'file'
  const [selectedFile, setSelectedFile] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const [isProcessingFile, setIsProcessingFile] = useState(false);
  const fileInputRef = useRef(null);

  // File type information
  const supportedFormats = {
    txt: { name: 'Texto simples', icon: '📄' },
    md: { name: 'Markdown', icon: '📝' },
    docx: { name: 'Word Document', icon: '📘' },
    odt: { name: 'OpenDocument Text', icon: '📄' },
    pdf: { name: 'PDF Document', icon: '📕' },
  };

  const handleFileSelection = useCallback(
    async event => {
      const file = event.target.files[0];
      if (!file) return;

      setSelectedFile(file);
      setWarnings([]);
      setIsProcessingFile(true);

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
            setWarnings(['Formato de arquivo não suportado']);
            setSelectedFile(null);
            return;
          }

          // Process the file to extract text
          const processResponse = await fetch(
            'http://localhost:8000/api/v1/text-input/process-file',
            {
              method: 'POST',
              body: formData,
            }
          );

          if (processResponse.ok) {
            const result = await processResponse.json();
            if (result.success) {
              onChange(result.source_text || '');
              setWarnings(result.warnings || []);
            } else {
              setWarnings(
                result.errors || ['Erro no processamento do arquivo']
              );
            }
          }
        }
      } catch (error) {
        console.error('File processing error:', error);
        setWarnings(['Erro ao processar arquivo']);
      } finally {
        setIsProcessingFile(false);
      }
    },
    [onChange]
  );

  const clearFile = () => {
    setSelectedFile(null);
    setWarnings([]);
    onChange('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getCharacterCount = text => text?.length || 0;
  const getWordCount = text =>
    text
      ?.trim()
      .split(/\s+/)
      .filter(word => word.length > 0).length || 0;
  const getParagraphCount = text =>
    text?.split('\n').filter(p => p.trim()).length || 0;

  return (
    <div className='space-y-3'>
      <label className='block text-sm font-medium text-gray-700'>
        {label} {required && <span className='text-red-500'>*</span>}
      </label>

      {/* Tab Navigation */}
      <div className='flex space-x-1 bg-gray-100 rounded-lg p-1'>
        <button
          onClick={() => setActiveTab('type')}
          disabled={disabled}
          className={`flex-1 flex items-center justify-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'type'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <Type className='w-4 h-4 mr-2' />
          Digitar Texto
        </button>
        <button
          onClick={() => setActiveTab('file')}
          disabled={disabled}
          className={`flex-1 flex items-center justify-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'file'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <Upload className='w-4 h-4 mr-2' />
          Carregar Arquivo
        </button>
      </div>

      {/* Warnings Display */}
      {warnings.length > 0 && (
        <div className='p-3 bg-yellow-50 border border-yellow-200 rounded-md'>
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
        <div className='space-y-2'>
          <textarea
            value={value || ''}
            onChange={e => onChange(e.target.value)}
            placeholder={placeholder}
            disabled={disabled}
            className='w-full h-40 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:bg-gray-50 disabled:cursor-not-allowed'
          />
          <div className='flex justify-between text-xs text-gray-500'>
            <span>Parágrafos: {getParagraphCount(value)}</span>
            <div className='space-x-4'>
              <span>{getWordCount(value)} palavras</span>
              <span>
                {getCharacterCount(value).toLocaleString()} caracteres
              </span>
            </div>
          </div>
        </div>
      )}

      {/* File Upload Tab */}
      {activeTab === 'file' && (
        <div className='space-y-3'>
          {!selectedFile ? (
            <div
              onClick={() => !disabled && fileInputRef.current?.click()}
              className={`border-2 border-dashed border-gray-300 rounded-lg p-6 text-center transition-colors ${
                disabled
                  ? 'cursor-not-allowed opacity-50'
                  : 'cursor-pointer hover:border-blue-400 hover:bg-blue-50'
              }`}
            >
              <Upload className='w-8 h-8 text-gray-400 mx-auto mb-2' />
              <p className='text-sm text-gray-600 mb-1'>
                Clique para selecionar um arquivo
              </p>
              <p className='text-xs text-gray-400'>
                Formatos: TXT, MD, DOCX, ODT, PDF (máx. 10MB)
              </p>
              <input
                ref={fileInputRef}
                type='file'
                onChange={handleFileSelection}
                accept='.txt,.md,.docx,.odt,.pdf'
                className='hidden'
                disabled={disabled}
              />
            </div>
          ) : (
            <div className='bg-gray-50 border border-gray-200 rounded-lg p-4'>
              <div className='flex items-center justify-between'>
                <div className='flex items-center space-x-3'>
                  <FileText className='w-8 h-8 text-blue-500' />
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
                  disabled={disabled}
                  className='p-1 text-gray-400 hover:text-red-500 transition-colors disabled:cursor-not-allowed'
                >
                  <X className='w-4 h-4' />
                </button>
              </div>

              {isProcessingFile && (
                <div className='mt-3 flex items-center text-sm text-blue-600'>
                  <div className='animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2'></div>
                  Processando arquivo...
                </div>
              )}
            </div>
          )}

          {/* Text preview for file content */}
          {value && selectedFile && !isProcessingFile && (
            <div className='space-y-2'>
              <div className='text-sm font-medium text-gray-700'>
                Conteúdo extraído:
              </div>
              <div className='bg-gray-50 border border-gray-200 rounded-lg p-3 max-h-32 overflow-y-auto'>
                <pre className='text-xs text-gray-600 whitespace-pre-wrap'>
                  {value.substring(0, 500)}
                  {value.length > 500 ? '...' : ''}
                </pre>
              </div>
              <div className='flex justify-between text-xs text-gray-500'>
                <span>Parágrafos: {getParagraphCount(value)}</span>
                <div className='space-x-4'>
                  <span>{getWordCount(value)} palavras</span>
                  <span>
                    {getCharacterCount(value).toLocaleString()} caracteres
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TextInputField;
