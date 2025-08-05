/**
 * FileUploadTestPage.jsx - Test page for demonstrating file upload integration
 * Phase 2.B.5: Frontend integration testing component
 */

import React, { useState } from 'react';
import FileUploadTextInput from './FileUploadTextInput';
import ComparativeAnalysisService from '../services/comparativeAnalysisService';

const FileUploadTestPage = () => {
  const [sourceText, setSourceText] = useState('');
  const [targetText, setTargetText] = useState('');
  const [validationResult, setValidationResult] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Test validation endpoint
  const handleValidateTexts = async () => {
    if (!sourceText.trim() || !targetText.trim()) {
      setError('Por favor, forneça ambos os textos para validação.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await ComparativeAnalysisService.validateTexts(sourceText, targetText);
      setValidationResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Test full comparative analysis
  const handleFullAnalysis = async () => {
    if (!sourceText.trim() || !targetText.trim()) {
      setError('Por favor, forneça ambos os textos para análise.');
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
      setAnalysisResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Load sample Portuguese legal texts
  const loadSampleTexts = () => {
    const complexText = `
A Lei de Responsabilidade Fiscal representa um marco fundamental na gestão pública brasileira, estabelecendo princípios, normas e diretrizes que visam ao controle rigoroso dos gastos públicos e à transparência na administração dos recursos financeiros governamentais.

Esta legislação instituiu mecanismos de controle que abrangem desde a elaboração orçamentária até a execução das despesas, determinando limites para gastos com pessoal, estabelecendo critérios para a criação de despesas continuadas e implementando instrumentos de planejamento fiscal de médio e longo prazo.

Os dispositivos legais contemplam ainda penalidades severas para gestores que descumprirem as determinações estabelecidas, incluindo a possibilidade de responsabilização criminal, civil e administrativa, configurando um sistema abrangente de accountability na gestão dos recursos públicos.
`.trim();

    const simplifiedText = `
A Lei de Responsabilidade Fiscal é uma lei muito importante para o Brasil. Ela criou regras para controlar os gastos do governo e tornar mais transparente o uso do dinheiro público.

Esta lei criou formas de controlar os gastos desde o planejamento até o uso final do dinheiro. Ela também definiu limites para gastos com funcionários públicos e criou regras para planejar os gastos futuros.

Se os responsáveis não seguirem essas regras, podem ser punidos de diferentes formas. Isso garante que o dinheiro público seja usado corretamente.
`.trim();

    setSourceText(complexText);
    setTargetText(simplifiedText);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Teste de Integração: Upload de Arquivos
        </h1>
        <p className="text-gray-600">
          Demonstração da funcionalidade de upload de arquivos PDF/TXT com análise comparativa em português.
        </p>
        
        {/* Sample Data Button */}
        <div className="mt-4">
          <button
            onClick={loadSampleTexts}
            className="bg-blue-100 text-blue-700 px-4 py-2 rounded-md hover:bg-blue-200 transition-colors"
          >
            📄 Carregar Textos de Exemplo (Lei de Responsabilidade Fiscal)
          </button>
        </div>
      </div>

      {/* Input Areas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <FileUploadTextInput
            label="Texto Complexo (Original)"
            placeholder="Digite ou faça upload de um documento complexo..."
            value={sourceText}
            onChange={setSourceText}
            disabled={loading}
          />
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <FileUploadTextInput
            label="Texto Simplificado (Alvo)"
            placeholder="Digite ou faça upload de um documento simplificado..."
            value={targetText}
            onChange={setTargetText}
            disabled={loading}
          />
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="text-red-600 font-medium">❌ Erro:</div>
            <div className="ml-2 text-red-700">{error}</div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Testes de API</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={handleValidateTexts}
            disabled={loading || !sourceText.trim() || !targetText.trim()}
            className="bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Validando...
              </>
            ) : (
              <>
                ✓ Validar Textos
              </>
            )}
          </button>

          <button
            onClick={handleFullAnalysis}
            disabled={loading || !sourceText.trim() || !targetText.trim()}
            className="bg-purple-600 text-white py-3 px-4 rounded-md hover:bg-purple-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Analisando...
              </>
            ) : (
              <>
                🔍 Análise Completa
              </>
            )}
          </button>
        </div>
      </div>

      {/* Validation Results */}
      {validationResult && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">
            Resultados da Validação
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {validationResult.source_stats?.character_count || 0}
              </div>
              <div className="text-sm text-blue-600">Caracteres (Fonte)</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {validationResult.target_stats?.character_count || 0}
              </div>
              <div className="text-sm text-green-600">Caracteres (Alvo)</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {validationResult.comparison?.length_reduction_percentage?.toFixed(1) || 0}%
              </div>
              <div className="text-sm text-purple-600">Redução</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {validationResult.validation_score?.toFixed(2) || 0}
              </div>
              <div className="text-sm text-orange-600">Score de Validação</div>
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-2">Status da Validação</h4>
            <div className="text-sm space-y-1">
              <div className="flex justify-between">
                <span>Válido:</span>
                <span className={validationResult.is_valid ? 'text-green-600' : 'text-red-600'}>
                  {validationResult.is_valid ? '✅ Sim' : '❌ Não'}
                </span>
              </div>
              {validationResult.validation_issues && validationResult.validation_issues.length > 0 && (
                <div className="mt-2">
                  <span className="text-red-600">Problemas encontrados:</span>
                  <ul className="list-disc list-inside ml-4 text-red-600">
                    {validationResult.validation_issues.map((issue, index) => (
                      <li key={index}>{issue}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Full Analysis Results */}
      {analysisResult && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">
            Análise Comparativa Completa
          </h3>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap">
              {JSON.stringify(analysisResult, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploadTestPage;
