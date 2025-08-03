/**
 * Analysis State Store
 * Manages text processing data, analysis results, and processing history
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

const useAnalysisStore = create(
  devtools(
    (set, get) => ({
      // Current Analysis Data
      currentAnalysis: {
        id: null,
        originalText: '',
        simplifiedText: '',
        inputMethod: null, // 'typed' | 'file'
        fileName: null,
        fileType: null,
        processingStatus: 'idle', // 'idle' | 'processing' | 'completed' | 'error'
        createdAt: null,
        completedAt: null,
      },

      // Processing Results
      preprocessingResults: null,
      alignmentResults: null,
      analysisMetrics: null,

      // Historical Data (in-memory for current session)
      analysisHistory: [],
      
      // Processing State
      isProcessing: false,
      processingStep: null, // 'preprocessing' | 'alignment' | 'analysis'
      processingProgress: 0,
      processingError: null,

      // Actions - Text Input
      setInputText: (text, method = 'typed', fileName = null, fileType = null) => {
        const analysisId = `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        set(
          (_state) => ({
            currentAnalysis: {
              id: analysisId,
              originalText: text,
              simplifiedText: '',
              inputMethod: method,
              fileName,
              fileType,
              processingStatus: 'idle',
              createdAt: new Date().toISOString(),
              completedAt: null,
            },
            preprocessingResults: null,
            alignmentResults: null,
            analysisMetrics: null,
            processingError: null,
          }),
          false,
          'setInputText'
        );

        return analysisId;
      },

      setSimplifiedText: (text) =>
        set(
          (state) => ({
            currentAnalysis: {
              ...state.currentAnalysis,
              simplifiedText: text,
            },
          }),
          false,
          'setSimplifiedText'
        ),

      // Actions - Processing State
      startProcessing: (step) =>
        set(
          (state) => ({
            isProcessing: true,
            processingStep: step,
            processingProgress: 0,
            processingError: null,
            currentAnalysis: {
              ...state.currentAnalysis,
              processingStatus: 'processing',
            },
          }),
          false,
          'startProcessing'
        ),

      updateProcessingProgress: (progress) =>
        set(
          (_state) => ({
            processingProgress: Math.max(0, Math.min(100, progress)),
          }),
          false,
          'updateProcessingProgress'
        ),

      completeProcessing: () =>
        set(
          (state) => ({
            isProcessing: false,
            processingStep: null,
            processingProgress: 100,
            currentAnalysis: {
              ...state.currentAnalysis,
              processingStatus: 'completed',
              completedAt: new Date().toISOString(),
            },
          }),
          false,
          'completeProcessing'
        ),

      setProcessingError: (error) =>
        set(
          (state) => ({
            isProcessing: false,
            processingStep: null,
            processingError: error,
            currentAnalysis: {
              ...state.currentAnalysis,
              processingStatus: 'error',
            },
          }),
          false,
          'setProcessingError'
        ),

      // Actions - Results
      setPreprocessingResults: (results) =>
        set(
          (_state) => ({
            preprocessingResults: results,
          }),
          false,
          'setPreprocessingResults'
        ),

      setAlignmentResults: (results) =>
        set(
          (_state) => ({
            alignmentResults: results,
          }),
          false,
          'setAlignmentResults'
        ),

      setAnalysisMetrics: (metrics) =>
        set(
          (_state) => ({
            analysisMetrics: metrics,
          }),
          false,
          'setAnalysisMetrics'
        ),

      // Actions - History Management
      saveToHistory: () => {
        const { currentAnalysis, preprocessingResults, alignmentResults, analysisMetrics } = get();
        
        if (!currentAnalysis.id) return;

        const historyEntry = {
          ...currentAnalysis,
          results: {
            preprocessing: preprocessingResults,
            alignment: alignmentResults,
            metrics: analysisMetrics,
          },
          savedAt: new Date().toISOString(),
        };

        set(
          (state) => ({
            analysisHistory: [historyEntry, ...state.analysisHistory.slice(0, 49)], // Keep last 50
          }),
          false,
          'saveToHistory'
        );

        return historyEntry;
      },

      loadFromHistory: (historyId) => {
        const { analysisHistory } = get();
        const historyEntry = analysisHistory.find(entry => entry.id === historyId);
        
        if (!historyEntry) return false;

        set(
          (_state) => ({
            currentAnalysis: {
              id: historyEntry.id,
              originalText: historyEntry.originalText,
              simplifiedText: historyEntry.simplifiedText,
              inputMethod: historyEntry.inputMethod,
              fileName: historyEntry.fileName,
              fileType: historyEntry.fileType,
              processingStatus: historyEntry.processingStatus,
              createdAt: historyEntry.createdAt,
              completedAt: historyEntry.completedAt,
            },
            preprocessingResults: historyEntry.results?.preprocessing || null,
            alignmentResults: historyEntry.results?.alignment || null,
            analysisMetrics: historyEntry.results?.metrics || null,
            isProcessing: false,
            processingStep: null,
            processingProgress: 0,
            processingError: null,
          }),
          false,
          'loadFromHistory'
        );

        return true;
      },

      clearHistory: () =>
        set(
          (_state) => ({
            analysisHistory: [],
          }),
          false,
          'clearHistory'
        ),

      // Actions - Reset
      resetCurrentAnalysis: () =>
        set(
          (_state) => ({
            currentAnalysis: {
              id: null,
              originalText: '',
              simplifiedText: '',
              inputMethod: null,
              fileName: null,
              fileType: null,
              processingStatus: 'idle',
              createdAt: null,
              completedAt: null,
            },
            preprocessingResults: null,
            alignmentResults: null,
            analysisMetrics: null,
            isProcessing: false,
            processingStep: null,
            processingProgress: 0,
            processingError: null,
          }),
          false,
          'resetCurrentAnalysis'
        ),

      // Getters
      hasValidInput: () => {
        const { currentAnalysis } = get();
        return currentAnalysis.originalText.trim().length > 0;
      },

      hasValidTexts: () => {
        const { currentAnalysis } = get();
        return (
          currentAnalysis.originalText.trim().length > 0 &&
          currentAnalysis.simplifiedText.trim().length > 0
        );
      },

      getCurrentResults: () => {
        const { preprocessingResults, alignmentResults, analysisMetrics } = get();
        return {
          preprocessing: preprocessingResults,
          alignment: alignmentResults,
          metrics: analysisMetrics,
        };
      },
    }),
    {
      name: 'analysis-store',
    }
  )
);

export default useAnalysisStore;
