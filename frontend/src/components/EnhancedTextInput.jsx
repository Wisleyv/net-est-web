/**
 * EnhancedTextInput.jsx - Enhanced Text Input Component
 * Combines input functionality with results display for the NET-EST system
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import DualTextInputComponent from './DualTextInputComponent';
import ComparativeResultsDisplay from './ComparativeResultsDisplay';
import api from '../services/api';

const EnhancedTextInput = ({ onTextProcessed, onError }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentView, setCurrentView] = useState('input'); // 'input' or 'results' - Start with input for clean state

  // Handle comparative analysis request
  const handleComparativeAnalysis = async (inputData) => {
    setIsAnalyzing(true);
    setCurrentView('input'); // Stay on input view during processing
    
    try {
      // Prepare the request data as JSON
      const requestData = {
        source_text: inputData.sourceText,
        target_text: inputData.targetText,
        analysis_options: {
          include_lexical_analysis: true,
          include_syntactic_analysis: true,
          include_semantic_analysis: true,
          include_readability_metrics: true,
          include_strategy_identification: true,
          include_salience: true
        },
        metadata: inputData.metadata || {}
      };
      
      // Call the comparative analysis API
      const response = await api.post('/api/v1/comparative-analysis/', requestData);
      
      const result = response.data;
      
      // Check if the response contains the expected analysis result fields
      if (result && result.analysis_id && result.overall_score !== undefined) {
        // Add the original texts to the result for display
        const enhancedResult = {
          ...result,
          sourceText: inputData.sourceText,
          targetText: inputData.targetText,
          timestamp: result.timestamp || new Date().toISOString(),
          // Map the API response structure to what the display component expects
          strategies_count: result.strategies_count || result.simplification_strategies?.length || 0,
          semantic_preservation: result.semantic_preservation || result.semantic_analysis?.semantic_similarity || 0,
          readability_improvement: result.readability_improvement || 0,
        };
        
        setAnalysisData(enhancedResult);
        setCurrentView('results');
        
        // Call the callback
        if (onTextProcessed) {
          onTextProcessed(enhancedResult);
        }
      } else {
        throw new Error('Invalid analysis response format');
      }
      
    } catch (error) {
      console.error('Comparative analysis error:', error);
      
      // Call error callback
      if (onError) {
        onError(error);
      }
      
      // You could also show an error state here
      throw error; // Re-throw to let DualTextInputComponent handle it
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle export functionality
  const handleExport = async (format) => {
    if (!analysisData) return;
    
    try {
      const exportData = {
        analysis: analysisData,
        format: format,
        timestamp: new Date().toISOString()
      };
      
      // This could be extended to call an export API endpoint
      // For now, we'll create a simple JSON download
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `net-est-analysis-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Export failed:', error);
      if (onError) {
        onError(error);
      }
    }
  };

  // Handle navigation back to input
  const handleBackToInput = () => {
    setCurrentView('input');
  };

  // Handle starting a new analysis
  const handleNewAnalysis = () => {
    setAnalysisData(null);
    setCurrentView('input');
  };

  return (
    <div className="space-y-6">
      {/* Navigation breadcrumb when showing results */}
      {currentView === 'results' && analysisData && (
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <button
            onClick={handleBackToInput}
            className="text-blue-600 hover:text-blue-800 underline"
          >
            ← Voltar para entrada
          </button>
          <span>/</span>
          <span>Resultados da análise</span>
          <button
            onClick={handleNewAnalysis}
            className="ml-4 px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200"
          >
            Nova Análise
          </button>
        </div>
      )}

      {/* Input View */}
      {currentView === 'input' && (
        <DualTextInputComponent
          onComparativeAnalysis={handleComparativeAnalysis}
          className={isAnalyzing ? 'opacity-75 pointer-events-none' : ''}
        />
      )}

      {/* Loading State */}
      {isAnalyzing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="text-blue-800 font-medium">Analisando textos...</span>
          </div>
          <div className="mt-2 text-center text-sm text-blue-600">
            Aplicando algoritmos de detecção de estratégias de simplificação
          </div>
        </div>
      )}

      {/* Results View */}
      {currentView === 'results' && analysisData && (
        <ComparativeResultsDisplay
          analysisResult={analysisData}
          onExport={handleExport}
          isExporting={false}
        />
      )}

      {/* Error State - Could be enhanced */}
      {currentView === 'input' && !isAnalyzing && (
        <div className="text-xs text-gray-500 text-center">
          Sistema NET-EST para análise de estratégias de simplificação textual
        </div>
      )}
    </div>
  );
};

export default EnhancedTextInput;