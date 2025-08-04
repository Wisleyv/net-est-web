/**
 * ComparativeResultsDisplay.jsx - Phase 2.B.5 Implementation
 * Display component for comparative analysis results
 */

import React, { useState } from 'react';
import { 
  FileText, 
  TrendingUp, 
  BarChart3, 
  Target, 
  Download, 
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  AlertCircle,
  CheckCircle2,
  Info
} from 'lucide-react';

const ComparativeResultsDisplay = ({ 
  analysisResult, 
  onExport, 
  isExporting = false,
  className = "" 
}) => {
  const [activeSection, setActiveSection] = useState('overview');
  const [expandedSections, setExpandedSections] = useState({
    lexical: true,
    syntactic: false,
    strategies: true,
    readability: false,
  });

  if (!analysisResult) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p>Nenhuma análise comparativa disponível</p>
      </div>
    );
  }

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getStrategyIcon = (strategy) => {
    switch (strategy.type) {
      case 'lexical': return <Target className="w-4 h-4" />;
      case 'syntactic': return <BarChart3 className="w-4 h-4" />;
      case 'semantic': return <Eye className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Resultados da Análise Comparativa</h3>
              <p className="text-sm text-gray-600 mt-1">
                Análise realizada em {new Date(analysisResult.timestamp).toLocaleString('pt-BR')}
              </p>
              <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                <span>Texto fonte: {analysisResult.sourceLength} caracteres</span>
                <span>Texto simplificado: {analysisResult.targetLength} caracteres</span>
                <span>Redução: {analysisResult.compressionRatio}%</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => onExport('pdf')}
              disabled={isExporting}
              className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-1"
            >
              {isExporting ? (
                <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Download className="w-3 h-3" />
              )}
              Exportar PDF
            </button>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', label: 'Visão Geral', icon: BarChart3 },
            { id: 'comparison', label: 'Comparação', icon: FileText },
            { id: 'strategies', label: 'Estratégias', icon: Target },
            { id: 'metrics', label: 'Métricas', icon: TrendingUp },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveSection(id)}
              className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeSection === id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content Sections */}
      <div className="space-y-6">
        {/* Overview Section */}
        {activeSection === 'overview' && (
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Resumo Executivo</h4>
            
            {/* Overall Score */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h5 className="font-medium text-gray-900">Qualidade da Simplificação</h5>
                <div className="flex items-center gap-2">
                  <div className={`px-2 py-1 rounded text-sm font-medium ${
                    analysisResult.overallScore >= 80 ? 'bg-green-100 text-green-800' :
                    analysisResult.overallScore >= 60 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {analysisResult.overallScore}/100
                  </div>
                </div>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    analysisResult.overallScore >= 80 ? 'bg-green-500' :
                    analysisResult.overallScore >= 60 ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${analysisResult.overallScore}%` }}
                />
              </div>
              
              <p className="text-sm text-gray-600 mt-2">
                {analysisResult.overallAssessment}
              </p>
            </div>

            {/* Key Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                {
                  label: 'Preservação Semântica',
                  value: `${analysisResult.semanticPreservation}%`,
                  color: analysisResult.semanticPreservation >= 90 ? 'green' : 
                         analysisResult.semanticPreservation >= 70 ? 'yellow' : 'red'
                },
                {
                  label: 'Melhoria da Legibilidade',
                  value: `+${analysisResult.readabilityImprovement}pts`,
                  color: analysisResult.readabilityImprovement >= 10 ? 'green' : 
                         analysisResult.readabilityImprovement >= 5 ? 'yellow' : 'red'
                },
                {
                  label: 'Estratégias Identificadas',
                  value: analysisResult.strategiesCount,
                  color: 'blue'
                }
              ].map((metric, index) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">{metric.label}</div>
                  <div className={`text-2xl font-semibold mt-1 ${
                    metric.color === 'green' ? 'text-green-600' :
                    metric.color === 'yellow' ? 'text-yellow-600' :
                    metric.color === 'red' ? 'text-red-600' :
                    'text-blue-600'
                  }`}>
                    {metric.value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Side-by-side Comparison */}
        {activeSection === 'comparison' && (
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Comparação Lado a Lado</h4>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Source Text */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-gray-500" />
                  <h5 className="font-medium text-gray-900">Texto Fonte (Original)</h5>
                </div>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                    {analysisResult.sourceText}
                  </pre>
                </div>
              </div>

              {/* Target Text */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-green-600" />
                  <h5 className="font-medium text-gray-900">Texto Simplificado</h5>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                    {analysisResult.targetText}
                  </pre>
                </div>
              </div>
            </div>

            {/* Highlighted Differences */}
            {analysisResult.highlightedDifferences && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h5 className="font-medium text-gray-900 mb-3">Principais Diferenças Identificadas</h5>
                <div className="space-y-2">
                  {analysisResult.highlightedDifferences.map((diff, index) => (
                    <div key={index} className="flex items-start gap-3 p-2 bg-yellow-50 rounded">
                      <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                      <div className="text-sm">
                        <span className="font-medium text-yellow-800">{diff.type}:</span>
                        <span className="text-yellow-700 ml-1">{diff.description}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Simplification Strategies */}
        {activeSection === 'strategies' && (
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Estratégias de Simplificação Identificadas</h4>
            
            <div className="space-y-3">
              {analysisResult.simplificationStrategies?.map((strategy, index) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-full ${getSeverityColor(strategy.impact)}`}>
                      {getStrategyIcon(strategy)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h5 className="font-medium text-gray-900">{strategy.name}</h5>
                          <p className="text-sm text-gray-600 mt-1">{strategy.description}</p>
                        </div>
                        <div className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(strategy.impact)}`}>
                          {strategy.impact} impacto
                        </div>
                      </div>
                      
                      {strategy.examples && strategy.examples.length > 0 && (
                        <div className="mt-3">
                          <h6 className="text-sm font-medium text-gray-700 mb-2">Exemplos:</h6>
                          <div className="space-y-1">
                            {strategy.examples.map((example, exIndex) => (
                              <div key={exIndex} className="text-sm bg-gray-50 p-2 rounded">
                                <span className="text-red-600">"{example.before}"</span>
                                <span className="text-gray-500 mx-2">→</span>
                                <span className="text-green-600">"{example.after}"</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Detailed Metrics */}
        {activeSection === 'metrics' && (
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Métricas Detalhadas</h4>
            
            {/* Readability Metrics */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h5 className="font-medium text-gray-900 mb-4">Métricas de Legibilidade</h5>
              <div className="space-y-3">
                {analysisResult.readabilityMetrics && Object.entries(analysisResult.readabilityMetrics).map(([metric, data]) => (
                  <div key={metric} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{data.label}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-red-600">{data.source}</span>
                      <span className="text-gray-400">→</span>
                      <span className="text-sm text-green-600">{data.target}</span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        data.improvement > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {data.improvement > 0 ? '+' : ''}{data.improvement}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Lexical Analysis */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <button
                onClick={() => toggleSection('lexical')}
                className="flex items-center justify-between w-full"
              >
                <h5 className="font-medium text-gray-900">Análise Lexical</h5>
                {expandedSections.lexical ? 
                  <ChevronDown className="w-4 h-4 text-gray-500" /> : 
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                }
              </button>
              
              {expandedSections.lexical && analysisResult.lexicalAnalysis && (
                <div className="mt-4 space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600">Vocabulário Único</div>
                      <div className="flex items-center gap-2">
                        <span className="text-red-600">{analysisResult.lexicalAnalysis.sourceUniqueWords}</span>
                        <span className="text-gray-400">→</span>
                        <span className="text-green-600">{analysisResult.lexicalAnalysis.targetUniqueWords}</span>
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Complexidade Média</div>
                      <div className="flex items-center gap-2">
                        <span className="text-red-600">{analysisResult.lexicalAnalysis.sourceComplexity}</span>
                        <span className="text-gray-400">→</span>
                        <span className="text-green-600">{analysisResult.lexicalAnalysis.targetComplexity}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComparativeResultsDisplay;
