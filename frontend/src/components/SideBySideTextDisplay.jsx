/**
 * Side-by-Side Text Display Component
 * Displays source and target texts with color-coded strategy highlighting and interactive tags
 */

import React, { useState, useRef } from 'react';
import { Eye, EyeOff, Maximize2, Minimize2, Info } from 'lucide-react';
import { 
  getStrategyColor, 
  getStrategyDescription, 
  getAllStrategies,
  isSpecialStrategy 
} from '../services/strategyColorMapping';

const SideBySideTextDisplay = ({ 
  sourceText, 
  targetText, 
  analysisResults, 
  onTagChange: _onTagChange,
  className = '' 
}) => {
  // Component state
  const [isExpanded, setIsExpanded] = useState(false);
  const [showColorLegend, setShowColorLegend] = useState(true);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [hoveredTag, setHoveredTag] = useState(null);
  
  // Refs for synchronized scrolling
  const sourceScrollRef = useRef(null);
  const targetScrollRef = useRef(null);
  const isScrollSyncing = useRef(false);

  // Handle synchronized scrolling
  const handleScroll = (scrollElement, targetElement) => {
    if (isScrollSyncing.current) return;
    
    isScrollSyncing.current = true;
    if (targetElement && scrollElement) {
      const scrollPercentage = scrollElement.scrollTop / (scrollElement.scrollHeight - scrollElement.clientHeight);
      targetElement.scrollTop = scrollPercentage * (targetElement.scrollHeight - targetElement.clientHeight);
    }
    setTimeout(() => {
      isScrollSyncing.current = false;
    }, 50);
  };

  // Process analysis results for highlighting
  const processTextWithHighlighting = (text, results, isTarget = false) => {
    if (!text || !results?.strategies) return [{ text, type: 'text' }];

    const segments = [];
    let currentIndex = 0;

    // Sort strategies by position to avoid overlapping issues
    const sortedStrategies = [...results.strategies].sort((a, b) => a.start_pos - b.start_pos);

    sortedStrategies.forEach((strategy, index) => {
      // Add text before the strategy
      if (strategy.start_pos > currentIndex) {
        segments.push({
          text: text.slice(currentIndex, strategy.start_pos),
          type: 'text'
        });
      }

      // Add the highlighted strategy text
      const strategyText = text.slice(strategy.start_pos, strategy.end_pos);
      segments.push({
        text: strategyText,
        type: 'strategy',
        strategy: strategy.strategy_type,
        confidence: strategy.confidence,
        position: { start: strategy.start_pos, end: strategy.end_pos },
        isTarget,
        index
      });

      currentIndex = strategy.end_pos;
    });

    // Add remaining text
    if (currentIndex < text.length) {
      segments.push({
        text: text.slice(currentIndex),
        type: 'text'
      });
    }

    return segments;
  };

  // Render text segment with highlighting
  const renderTextSegment = (segment, segmentIndex) => {
    if (segment.type === 'text') {
      return <span key={segmentIndex}>{segment.text}</span>;
    }

    if (segment.type === 'strategy') {
      const isHovered = hoveredTag === `${segment.strategy}-${segmentIndex}`;
      const isSelected = selectedStrategy === segment.strategy;
      
      return (
        <button
          key={segmentIndex}
          type="button"
          className={`relative inline-block px-1 rounded transition-all duration-200 cursor-pointer border-0 bg-transparent ${
            isHovered ? 'shadow-lg z-10' : ''
          } ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
          style={{
            backgroundColor: `${getStrategyColor(segment.strategy)}40`, // 40 = 25% opacity in hex
            borderLeft: `3px solid ${getStrategyColor(segment.strategy)}`,
            transform: isHovered ? 'scale(1.02)' : 'scale(1)',
          }}
          onMouseEnter={() => setHoveredTag(`${segment.strategy}-${segmentIndex}`)}
          onMouseLeave={() => setHoveredTag(null)}
          onClick={() => setSelectedStrategy(isSelected ? null : segment.strategy)}
          title={`${segment.strategy}: ${getStrategyDescription(segment.strategy)} (${Math.round(segment.confidence * 100)}% confiança)`}
        >
          {segment.text}
          {segment.isTarget && (
            <sup className="ml-1 text-xs font-bold px-1 py-0.5 rounded text-white"
                 style={{ backgroundColor: getStrategyColor(segment.strategy) }}>
              {segment.strategy}
            </sup>
          )}
        </button>
      );
    }

    return null;
  };

  // Color legend component
  const ColorLegend = () => (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-medium text-gray-900 flex items-center gap-2">
          <Info className="w-4 h-4" />
          Legenda de Estratégias
        </h4>
        <button
          onClick={() => setShowColorLegend(!showColorLegend)}
          className="text-gray-500 hover:text-gray-700"
        >
          {showColorLegend ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </button>
      </div>
      
      {showColorLegend && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 text-xs">
          {getAllStrategies().map((strategy) => (
            <button
              key={strategy.code}
              type="button"
              className={`flex items-center gap-2 p-2 rounded cursor-pointer transition-all border-0 ${
                selectedStrategy === strategy.code ? 'ring-2 ring-blue-500 bg-white' : 'hover:bg-white bg-transparent'
              }`}
              onClick={() => setSelectedStrategy(selectedStrategy === strategy.code ? null : strategy.code)}
              title={strategy.description}
            >
              <div
                className="w-3 h-3 rounded border"
                style={{ backgroundColor: strategy.color }}
              />
              <span className={`font-mono ${strategy.isSpecial ? 'font-bold text-orange-600' : ''}`}>
                {strategy.code}
              </span>
              {strategy.isSpecial && (
                <span className="text-orange-500" title="Estratégia especial - ativação manual">⚠️</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );

  // Process texts for display
  const sourceSegments = processTextWithHighlighting(sourceText, analysisResults, false);
  const targetSegments = processTextWithHighlighting(targetText, analysisResults, true);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header with controls */}
      <div className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
            <span className="text-white text-xs font-bold">3</span>
          </div>
          <div>
            <h3 className="font-medium text-blue-900">Análise Comparativa Visual</h3>
            <p className="text-sm text-blue-800 mt-1">
              Visualização lado a lado com destaque colorido das estratégias de simplificação detectadas.
            </p>
          </div>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-2 text-blue-600 hover:bg-blue-100 rounded-md transition-colors"
          title={isExpanded ? "Minimizar" : "Expandir"}
        >
          {isExpanded ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
        </button>
      </div>

      {/* Color Legend */}
      <ColorLegend />

      {/* Side-by-side text display */}
      <div className={`grid gap-4 ${isExpanded ? 'min-h-[80vh]' : 'min-h-[400px]'} 
                      ${window.innerWidth >= 1024 ? 'lg:grid-cols-2' : 'grid-cols-1'}`}>
        
        {/* Source Text Panel */}
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="bg-red-50 border-b border-red-200 px-4 py-3">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <h4 className="font-medium text-red-900">Texto Original (Complexo)</h4>
              <span className="text-sm text-red-600">• Fonte</span>
            </div>
          </div>
          <div
            ref={sourceScrollRef}
            className={`p-4 overflow-y-auto ${isExpanded ? 'h-[70vh]' : 'h-80'} text-sm leading-relaxed`}
            onScroll={(e) => handleScroll(e.target, targetScrollRef.current)}
          >
            <div className="prose max-w-none">
              {sourceSegments.map((segment, index) => renderTextSegment(segment, index))}
            </div>
          </div>
        </div>

        {/* Target Text Panel */}
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="bg-green-50 border-b border-green-200 px-4 py-3">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <h4 className="font-medium text-green-900">Texto Simplificado (Tradução)</h4>
              <span className="text-sm text-green-600">• Simplificado</span>
            </div>
          </div>
          <div
            ref={targetScrollRef}
            className={`p-4 overflow-y-auto ${isExpanded ? 'h-[70vh]' : 'h-80'} text-sm leading-relaxed`}
            onScroll={(e) => handleScroll(e.target, sourceScrollRef.current)}
          >
            <div className="prose max-w-none">
              {targetSegments.map((segment, index) => renderTextSegment(segment, index))}
            </div>
          </div>
        </div>
      </div>

      {/* Strategy Information Panel */}
      {selectedStrategy && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-3 mb-3">
            <div
              className="w-4 h-4 rounded"
              style={{ backgroundColor: getStrategyColor(selectedStrategy) }}
            />
            <h4 className="font-medium text-gray-900">
              Estratégia Selecionada: {selectedStrategy}
            </h4>
            {isSpecialStrategy(selectedStrategy) && (
              <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">
                Manual Only
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600 mb-3">
            {getStrategyDescription(selectedStrategy)}
          </p>
          
          {/* Strategy statistics */}
          {analysisResults?.strategies && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-500">
              <div>
                <span className="font-medium">Ocorrências:</span>{' '}
                {analysisResults.strategies.filter(s => s.strategy_type === selectedStrategy).length}
              </div>
              <div>
                <span className="font-medium">Confiança Média:</span>{' '}
                {Math.round(
                  analysisResults.strategies
                    .filter(s => s.strategy_type === selectedStrategy)
                    .reduce((sum, s) => sum + s.confidence, 0) /
                  analysisResults.strategies.filter(s => s.strategy_type === selectedStrategy).length * 100
                )}%
              </div>
            </div>
          )}
        </div>
      )}

      {/* Instructions */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
        <p className="text-xs text-gray-600">
          <strong>Instruções:</strong> Clique em qualquer segmento destacado para selecionar uma estratégia. 
          Use a legenda para identificar as cores. Os textos sincronizam automaticamente ao rolar. 
          Tags com ⚠️ são especiais e requerem ativação manual.
        </p>
      </div>
    </div>
  );
};

export default SideBySideTextDisplay;

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código gerado por IA.
*/
