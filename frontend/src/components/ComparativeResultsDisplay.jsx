/**
 * ComparativeResultsDisplay.jsx - Phase 2.B.5 + Phase 4 Implementation
 * Display component for comparative analysis results with feedback collection
 */

import React, { useState } from 'react';
import { 
  FileText, 
  TrendingUp, 
  BarChart3, 
  Target, 
  Eye,
  ChevronDown,
  ChevronRight,
  AlertCircle,
  Info
} from 'lucide-react';
import SideBySideTextDisplay from './SideBySideTextDisplay';
import FeedbackCollection from './FeedbackCollection';

const ComparativeResultsDisplay = ({ 
  analysisResult, 
  sessionId = null,
  className = "" 
}) => {
  const [activeSection, setActiveSection] = useState('visual');
  const [expandedSections, setExpandedSections] = useState({
    lexical: true,
    syntactic: false,
    strategies: true,
    readability: false,
  });

  const handleFeedbackSubmitted = (feedbackData) => {
    console.log('Feedback submitted:', feedbackData);
    // You can add additional logic here, like showing a success message
  };

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
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Resultados da Análise Comparativa</h3>
            <p className="text-sm text-gray-600 mt-1">
              Análise realizada em {new Date(analysisResult.timestamp || Date.now()).toLocaleString('pt-BR')}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="overflow-x-auto">
          <nav className="flex space-x-1 min-w-max px-4 sm:px-0">
            {[
              { id: 'overview', label: 'Visão Geral', icon: BarChart3 },
              { id: 'visual', label: 'Análise Visual', icon: Eye },
              { id: 'comparison', label: 'Comparação', icon: FileText },
              { id: 'strategies', label: 'Estratégias', icon: Target },
              { id: 'metrics', label: 'Métricas', icon: TrendingUp },
              { id: 'feedback', label: 'Feedback', icon: Info },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveSection(id)}
                className={`flex items-center gap-2 py-3 px-4 rounded-t-lg border-b-2 font-medium text-sm whitespace-nowrap transition-all duration-200 ${
                  activeSection === id
                    ? 'border-blue-500 text-blue-600 bg-blue-50 shadow-sm'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50 hover:border-gray-300 border border-gray-200 border-b-transparent bg-gray-25'
                }`}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="hidden sm:inline">{label}</span>
                <span className="sm:hidden text-xs">{label.split(' ')[0]}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content Sections */}
      <div className="space-y-6">
        {/* Phase 4: Feedback Collection Section */}
        {activeSection === 'feedback' && (
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Feedback da Análise</h4>
            <p className="text-sm text-gray-600">
              Sua avaliação nos ajuda a melhorar a qualidade das análises comparativas.
            </p>
            
            <FeedbackCollection
              analysisId={analysisResult.analysis_id || `analysis_${Date.now()}`}
              sessionId={sessionId}
              expectedResult={null} // Could be populated with user expectations
              actualResult={JSON.stringify({
                source_text: analysisResult.source_text,
                target_text: analysisResult.target_text,
                strategies: analysisResult.simplification_strategies || []
              })}
              onFeedbackSubmitted={handleFeedbackSubmitted}
              className="max-w-md"
            />
          </div>
        )}

        {/* Overview Section */}
        {activeSection === 'overview' && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              <h4 className="font-medium text-gray-900">Resumo</h4>
            </div>
            
            {/* Text Characteristics */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-gray-600" />
                  <h5 className="font-medium text-gray-900">Estatísticas</h5>
                </div>
              </div>
              
              {(() => {
                // Calculate word counts instead of character counts
                const sourceWords = analysisResult.source_text ? 
                  analysisResult.source_text.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
                const targetWords = analysisResult.target_text ? 
                  analysisResult.target_text.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
                const reduction = sourceWords > 0 ? ((sourceWords - targetWords) / sourceWords) * 100 : 0;
                const reductionRounded = Math.round(reduction * 10) / 10;
                
                return (
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Redução de palavras:</span>
                      <span className={`text-sm font-medium ${
                        reductionRounded > 0 ? 'text-green-600' : 
                        reductionRounded < 0 ? 'text-orange-600' : 'text-gray-600'
                      }`}>
                        {reductionRounded > 0 ? `-${reductionRounded}%` : 
                         reductionRounded < 0 ? `+${Math.abs(reductionRounded)}%` : '0%'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Palavras fonte:</span>
                      <span className="text-sm font-medium">{sourceWords.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Palavras alvo:</span>
                      <span className="text-sm font-medium">{targetWords.toLocaleString()}</span>
                    </div>
                  </div>
                );
              })()}
              
              <p className="text-sm text-gray-600 mt-3">
                {(() => {
                  const strategiesCount = analysisResult.strategies?.length || 0;
                  if (strategiesCount === 0) {
                    return "Nenhuma estratégia de simplificação específica foi identificada automaticamente.";
                  } else if (strategiesCount === 1) {
                    return `Foi identificada 1 estratégia de simplificação principal.`;
                  } else {
                    return `Foram identificadas ${strategiesCount} estratégias de simplificação.`;
                  }
                })()}
              </p>
            </div>

            {/* Key Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                {
                  label: 'Preservação Semântica',
                  value: `${analysisResult.semantic_preservation?.toFixed(1) || '0.0'}%`,
                  color: (analysisResult.semantic_preservation || 0) >= 90 ? 'green' : 
                         (analysisResult.semantic_preservation || 0) >= 70 ? 'yellow' : 'red',
                  tooltip: 'Porcentagem do significado original preservado na simplificação'
                },
                {
                  label: 'Melhoria da Legibilidade',
                  value: `+${analysisResult.readability_improvement?.toFixed(1) || '0.0'}pts`,
                  color: (analysisResult.readability_improvement || 0) >= 10 ? 'green' : 
                         (analysisResult.readability_improvement || 0) >= 5 ? 'yellow' : 'red',
                  tooltip: (() => {
                    const improvement = analysisResult.readability_improvement || 0;
                    if (improvement >= 15) return 'Melhoria excelente! Texto adequado para leitores do Ensino Fundamental (6-14 anos)';
                    if (improvement >= 10) return 'Boa melhoria! Texto adequado para leitores do Ensino Médio (15-17 anos)';
                    if (improvement >= 5) return 'Melhoria moderada. Texto adequado para leitores do Ensino Superior (18+ anos)';
                    return 'Melhoria limitada detectada. Texto ainda pode apresentar dificuldades de compreensão';
                  })(),
                  description: (() => {
                    const improvement = analysisResult.readability_improvement || 0;
                    if (improvement >= 15) return 'Ensino Fundamental';
                    if (improvement >= 10) return 'Ensino Médio';
                    if (improvement >= 5) return 'Ensino Superior';
                    return 'Limitado';
                  })()
                },
                {
                  label: 'Estratégias Identificadas',
                  value: analysisResult.strategies_count || 0,
                  color: 'blue',
                  tooltip: 'Número de estratégias de simplificação detectadas automaticamente'
                }
              ].map((metric, index) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 relative group">
                  <div className="text-sm text-gray-600">{metric.label}</div>
                  <div className={`text-2xl font-semibold mt-1 ${
                    metric.color === 'green' ? 'text-green-600' :
                    metric.color === 'yellow' ? 'text-yellow-600' :
                    metric.color === 'red' ? 'text-red-600' :
                    'text-blue-600'
                  }`}>
                    {metric.value}
                  </div>
                  {metric.description && (
                    <div className={`text-xs mt-2 font-medium ${
                      metric.color === 'green' ? 'text-green-700' :
                      metric.color === 'yellow' ? 'text-yellow-700' :
                      metric.color === 'red' ? 'text-red-700' :
                      'text-blue-700'
                    }`}>
                      Adequado para: {metric.description}
                    </div>
                  )}
                  {metric.tooltip && (
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 whitespace-nowrap">
                      {metric.tooltip}
                      <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Visual Analysis Section */}
        {activeSection === 'visual' && (
          <div className="space-y-4">
            <SideBySideTextDisplay
              sourceText={analysisResult.source_text}
              targetText={analysisResult.target_text}
              analysisResults={analysisResult}
              onTagChange={(changes) => {
                void changes;
              }}
            />
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
                    {analysisResult.source_text}
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
                    {analysisResult.target_text}
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
              {analysisResult.simplification_strategies?.map((strategy, index) => (
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
                {analysisResult.readability_metrics && Object.entries(analysisResult.readability_metrics).map(([metric, data]) => (
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
              
              {expandedSections.lexical && analysisResult.lexical_analysis && (
                <div className="mt-4 space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600">Vocabulário Único</div>
                      <div className="flex items-center gap-2">
                        <span className="text-red-600">{analysisResult.lexical_analysis.source_unique_words}</span>
                        <span className="text-gray-400">→</span>
                        <span className="text-green-600">{analysisResult.lexical_analysis.target_unique_words}</span>
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Complexidade Média</div>
                      <div className="flex items-center gap-2">
                        <span className="text-red-600">{analysisResult.lexical_analysis.source_complexity?.toFixed(2)}</span>
                        <span className="text-gray-400">→</span>
                        <span className="text-green-600">{analysisResult.lexical_analysis.target_complexity?.toFixed(2)}</span>
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
