/**
 * Processed Text Display Component for NET-EST System
 * Shows the results of text processing with source/target comparison
 */

import React, { useState } from 'react';
import {
  FileText,
  AlignLeft,
  BarChart3,
  Download,
  Eye,
  EyeOff,
  CheckCircle,
  AlertTriangle,
  Copy,
  Check,
} from 'lucide-react';

const ProcessedTextDisplay = ({ processedData, onContinue }) => {
  const [showParagraphs, setShowParagraphs] = useState(true);
  const [copiedField, setCopiedField] = useState(null);

  if (!processedData || !processedData.success) {
    return null;
  }

  const { processed_text, warnings, metadata } = processedData;
  const { source_text, target_text, source_paragraphs, target_paragraphs } =
    processed_text;

  const copyToClipboard = async (text, field) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const downloadText = (text, filename) => {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className='bg-white rounded-lg shadow-sm border p-6'>
      <div className='mb-6'>
        <div className='flex items-center justify-between'>
          <div>
            <h2 className='text-xl font-semibold text-gray-900 mb-2'>
              Texto Processado
            </h2>
            <p className='text-gray-600 text-sm'>
              Textos limpos e segmentados, prontos para análise
            </p>
          </div>
          <div className='flex items-center space-x-2'>
            <CheckCircle className='w-5 h-5 text-green-500' />
            <span className='text-sm text-green-600 font-medium'>
              Processamento concluído
            </span>
          </div>
        </div>
      </div>

      {/* Processing Warnings */}
      {warnings && warnings.length > 0 && (
        <div className='mb-6 p-3 bg-yellow-50 border border-yellow-200 rounded-md'>
          <div className='flex items-start'>
            <AlertTriangle className='w-5 h-5 text-yellow-400 mt-0.5 mr-2 flex-shrink-0' />
            <div className='text-sm'>
              <p className='font-medium text-yellow-800 mb-1'>
                Avisos do processamento:
              </p>
              <ul className='text-yellow-700 space-y-1'>
                {warnings.map((warning, index) => (
                  <li key={index}>• {warning}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Processing Statistics */}
      <div className='mb-6 grid grid-cols-1 md:grid-cols-3 gap-4'>
        <div className='bg-blue-50 p-4 rounded-lg'>
          <div className='flex items-center'>
            <BarChart3 className='w-5 h-5 text-blue-500 mr-2' />
            <h3 className='font-medium text-blue-800'>
              Estatísticas do Processamento
            </h3>
          </div>
          <div className='mt-2 space-y-1 text-sm text-blue-700'>
            <div>Tempo: {metadata?.processing_time || 'N/A'}</div>
            <div>Tipo: {metadata?.processing?.input_type || 'N/A'}</div>
            {metadata?.processing?.file_name && (
              <div>Arquivo: {metadata.processing.file_name}</div>
            )}
          </div>
        </div>

        <div className='bg-green-50 p-4 rounded-lg'>
          <div className='flex items-center'>
            <FileText className='w-5 h-5 text-green-500 mr-2' />
            <h3 className='font-medium text-green-800'>Texto de Origem</h3>
          </div>
          <div className='mt-2 space-y-1 text-sm text-green-700'>
            <div>
              Caracteres:{' '}
              {processed_text?.metadata?.source_stats?.characters?.toLocaleString() ||
                'N/A'}
            </div>
            <div>
              Palavras:{' '}
              {processed_text?.metadata?.source_stats?.words?.toLocaleString() ||
                'N/A'}
            </div>
            <div>
              Parágrafos:{' '}
              {processed_text?.metadata?.source_stats?.paragraphs || 'N/A'}
            </div>
          </div>
        </div>

        <div className='bg-purple-50 p-4 rounded-lg'>
          <div className='flex items-center'>
            <AlignLeft className='w-5 h-5 text-purple-500 mr-2' />
            <h3 className='font-medium text-purple-800'>Texto de Destino</h3>
          </div>
          <div className='mt-2 space-y-1 text-sm text-purple-700'>
            <div>
              Caracteres:{' '}
              {processed_text?.metadata?.target_stats?.characters?.toLocaleString() ||
                'N/A'}
            </div>
            <div>
              Palavras:{' '}
              {processed_text?.metadata?.target_stats?.words?.toLocaleString() ||
                'N/A'}
            </div>
            <div>
              Parágrafos:{' '}
              {processed_text?.metadata?.target_stats?.paragraphs || 'N/A'}
            </div>
          </div>
        </div>
      </div>

      {/* View Toggle */}
      <div className='mb-4 flex items-center justify-between'>
        <button
          onClick={() => setShowParagraphs(!showParagraphs)}
          className='flex items-center text-sm text-gray-600 hover:text-gray-900'
        >
          {showParagraphs ? (
            <>
              <EyeOff className='w-4 h-4 mr-1' />
              Mostrar texto contínuo
            </>
          ) : (
            <>
              <Eye className='w-4 h-4 mr-1' />
              Mostrar parágrafos
            </>
          )}
        </button>
      </div>

      {/* Text Display */}
      <div className='space-y-6'>
        {/* Source Text */}
        <div className='border border-gray-200 rounded-lg'>
          <div className='bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between'>
            <h3 className='font-medium text-gray-900 flex items-center'>
              <FileText className='w-4 h-4 mr-2 text-green-500' />
              Texto de Origem
            </h3>
            <div className='flex space-x-2'>
              <button
                onClick={() => copyToClipboard(source_text, 'source')}
                className='text-gray-500 hover:text-gray-700 p-1'
                title='Copiar texto'
              >
                {copiedField === 'source' ? (
                  <Check className='w-4 h-4 text-green-500' />
                ) : (
                  <Copy className='w-4 h-4' />
                )}
              </button>
              <button
                onClick={() => downloadText(source_text, 'texto_origem.txt')}
                className='text-gray-500 hover:text-gray-700 p-1'
                title='Baixar texto'
              >
                <Download className='w-4 h-4' />
              </button>
            </div>
          </div>
          <div className='p-4'>
            {showParagraphs ? (
              <div className='space-y-4'>
                {source_paragraphs.map((paragraph, index) => (
                  <div key={index} className='border-l-4 border-green-200 pl-4'>
                    <div className='text-xs text-gray-500 mb-1'>
                      Parágrafo {index + 1}
                    </div>
                    <p className='text-gray-800 leading-relaxed'>{paragraph}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className='prose prose-sm max-w-none'>
                <p className='text-gray-800 leading-relaxed whitespace-pre-wrap'>
                  {source_text}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Target Text */}
        <div className='border border-gray-200 rounded-lg'>
          <div className='bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between'>
            <h3 className='font-medium text-gray-900 flex items-center'>
              <AlignLeft className='w-4 h-4 mr-2 text-purple-500' />
              Texto de Destino
            </h3>
            <div className='flex space-x-2'>
              <button
                onClick={() => copyToClipboard(target_text, 'target')}
                className='text-gray-500 hover:text-gray-700 p-1'
                title='Copiar texto'
              >
                {copiedField === 'target' ? (
                  <Check className='w-4 h-4 text-green-500' />
                ) : (
                  <Copy className='w-4 h-4' />
                )}
              </button>
              <button
                onClick={() => downloadText(target_text, 'texto_destino.txt')}
                className='text-gray-500 hover:text-gray-700 p-1'
                title='Baixar texto'
              >
                <Download className='w-4 h-4' />
              </button>
            </div>
          </div>
          <div className='p-4'>
            {showParagraphs ? (
              <div className='space-y-4'>
                {target_paragraphs.map((paragraph, index) => (
                  <div
                    key={index}
                    className='border-l-4 border-purple-200 pl-4'
                  >
                    <div className='text-xs text-gray-500 mb-1'>
                      Parágrafo {index + 1}
                    </div>
                    <p className='text-gray-800 leading-relaxed'>{paragraph}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className='prose prose-sm max-w-none'>
                <p className='text-gray-800 leading-relaxed whitespace-pre-wrap'>
                  {target_text}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className='mt-6 flex justify-end space-x-3'>
        <button
          onClick={() => window.location.reload()}
          className='px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200'
        >
          Processar Novo Texto
        </button>
        <button
          onClick={() => onContinue?.(processedData)}
          className='px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center'
        >
          Continuar para Alinhamento
          <span className='ml-2'>→</span>
        </button>
      </div>
    </div>
  );
};

export default ProcessedTextDisplay;
