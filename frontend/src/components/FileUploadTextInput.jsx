/**
 * FileUploadTextInput.jsx - Enhanced text input with file upload support
 * Phase 2.B.5: Frontend integration for Portuguese document processing
 */

import React, { useState, useCallback } from 'react';
import ComparativeAnalysisService from '../services/comparativeAnalysisService';

const FileUploadTextInput = ({ 
  label, 
  value, 
  onChange, 
  placeholder,
  disabled = false,
  accept = ".txt,.pdf,.docx,.odt,.md",
  maxFileSize = 5 * 1024 * 1024, // 5MB
  className = ""
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  // Process uploaded file
  const processFile = useCallback(async (file) => {
    setUploadError(null);
    
    // Validate file type
    if (!ComparativeAnalysisService.isFileTypeSupported(file)) {
      setUploadError(`Tipo de arquivo não suportado: ${file.type || 'desconhecido'}`);
      return;
    }

    // Validate file size
    if (file.size > maxFileSize) {
      setUploadError(`Arquivo muito grande. Máximo: ${ComparativeAnalysisService.formatFileSize(maxFileSize)}`);
      return;
    }

    setIsUploading(true);
    setUploadProgress(`Processando ${file.name}...`);

    try {
      const result = await ComparativeAnalysisService.uploadTextFile(file);
      
      if (result.success && result.extracted_text) {
        onChange(result.extracted_text);
        setUploadProgress(`✅ Texto extraído: ${result.character_count} caracteres`);
        
        // Clear progress after 3 seconds
        setTimeout(() => {
          setUploadProgress(null);
        }, 3000);
      } else {
        throw new Error(result.message || 'Falha na extração de texto');
      }
    } catch (error) {
      console.error('File upload error:', error);
      setUploadError(error.message);
    } finally {
      setIsUploading(false);
    }
  }, [maxFileSize, onChange]);

  // Handle file selection via input
  const handleFileSelect = useCallback(async (event) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      await processFile(files[0]);
    }
    // Reset input value to allow re-selecting the same file
    event.target.value = '';
  }, [processFile]);

  // Handle drag and drop
  const handleDrop = useCallback(async (event) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
      await processFile(files[0]);
    }
  }, [processFile]);

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((event) => {
    event.preventDefault();
    setIsDragOver(false);
  }, []);

  return (
    <div className={`file-upload-text-input ${className}`}>
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}

      {/* File Upload Area */}
      <div 
        className={`
          border-2 border-dashed rounded-lg p-4 mb-3 transition-colors
          ${isDragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-gray-400'}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="text-center">
          <svg 
            className="mx-auto h-12 w-12 text-gray-400" 
            stroke="currentColor" 
            fill="none" 
            viewBox="0 0 48 48"
          >
            <path 
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" 
              strokeWidth={2} 
              strokeLinecap="round" 
              strokeLinejoin="round" 
            />
          </svg>
          <div className="mt-2">
            <label htmlFor="file-upload" className="cursor-pointer">
              <span className="text-blue-600 hover:text-blue-500 font-medium">
                Clique para selecionar um arquivo
              </span>
              <span className="text-gray-500"> ou arraste e solte aqui</span>
              <input
                id="file-upload"
                name="file-upload"
                type="file"
                className="sr-only"
                accept={accept}
                onChange={handleFileSelect}
                disabled={disabled || isUploading}
              />
            </label>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Suporta: TXT, PDF, DOCX, ODT, MD (máx. {ComparativeAnalysisService.formatFileSize(maxFileSize)})
          </p>
        </div>
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            <span className="text-sm text-blue-700">Processando arquivo...</span>
          </div>
        </div>
      )}

      {/* Upload Progress Message */}
      {uploadProgress && !isUploading && (
        <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-md">
          <span className="text-sm text-green-700">{uploadProgress}</span>
        </div>
      )}

      {/* Upload Error */}
      {uploadError && (
        <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-md">
          <span className="text-sm text-red-700">❌ {uploadError}</span>
        </div>
      )}

      {/* Text Area */}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className={`
          w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm 
          focus:outline-none focus:ring-blue-500 focus:border-blue-500
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}
          min-h-[120px] resize-vertical
        `}
        rows={6}
      />

      {/* Character Count */}
      {value && (
        <div className="mt-2 text-xs text-gray-500 text-right">
          {value.length} caracteres
        </div>
      )}
    </div>
  );
};

export default FileUploadTextInput;
