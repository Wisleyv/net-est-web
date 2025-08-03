/**
 * Session State Store
 * Manages user session, analytics tracking, and session-specific data
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useSessionStore = create(
  devtools(
    persist(
      (set, get) => ({
        // Session Data
        sessionId: null,
        sessionStartTime: null,
        sessionActive: false,
        sessionAnalytics: null,

        // User Context
        userPreferences: {
          theme: 'light',
          language: 'pt-BR',
          autoSaveInterval: 30000, // 30 seconds
          showAdvancedOptions: false,
        },

        // Session Metrics (in-memory tracking)
        sessionMetrics: {
          textInputCount: 0,
          alignmentRequestCount: 0,
          processingTime: 0,
          errorsEncountered: 0,
          lastActivity: null,
        },

        // Actions
        startSession: () => {
          const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          const startTime = new Date().toISOString();
          
          set(
            (_state) => ({
              sessionId,
              sessionStartTime: startTime,
              sessionActive: true,
              sessionMetrics: {
                textInputCount: 0,
                alignmentRequestCount: 0,
                processingTime: 0,
                errorsEncountered: 0,
                lastActivity: startTime,
              },
            }),
            false,
            'startSession'
          );

          return sessionId;
        },

        endSession: () =>
          set(
            (_state) => ({
              sessionActive: false,
              sessionMetrics: {
                textInputCount: 0,
                alignmentRequestCount: 0,
                processingTime: 0,
                errorsEncountered: 0,
                lastActivity: null,
              },
            }),
            false,
            'endSession'
          ),

        updateSessionAnalytics: (analytics) =>
          set(
            (_state) => ({
              sessionAnalytics: analytics,
            }),
            false,
            'updateSessionAnalytics'
          ),

        updateUserPreferences: (preferences) =>
          set(
            (state) => ({
              userPreferences: {
                ...state.userPreferences,
                ...preferences,
              },
            }),
            false,
            'updateUserPreferences'
          ),

        // Metrics tracking
        incrementTextInput: () =>
          set(
            (state) => ({
              sessionMetrics: {
                ...state.sessionMetrics,
                textInputCount: state.sessionMetrics.textInputCount + 1,
                lastActivity: new Date().toISOString(),
              },
            }),
            false,
            'incrementTextInput'
          ),

        incrementAlignmentRequest: () =>
          set(
            (state) => ({
              sessionMetrics: {
                ...state.sessionMetrics,
                alignmentRequestCount: state.sessionMetrics.alignmentRequestCount + 1,
                lastActivity: new Date().toISOString(),
              },
            }),
            false,
            'incrementAlignmentRequest'
          ),

        addProcessingTime: (timeMs) =>
          set(
            (state) => ({
              sessionMetrics: {
                ...state.sessionMetrics,
                processingTime: state.sessionMetrics.processingTime + timeMs,
                lastActivity: new Date().toISOString(),
              },
            }),
            false,
            'addProcessingTime'
          ),

        incrementError: () =>
          set(
            (state) => ({
              sessionMetrics: {
                ...state.sessionMetrics,
                errorsEncountered: state.sessionMetrics.errorsEncountered + 1,
                lastActivity: new Date().toISOString(),
              },
            }),
            false,
            'incrementError'
          ),

        // Getters
        getSessionDuration: () => {
          const { sessionStartTime } = get();
          if (!sessionStartTime) return 0;
          return Date.now() - new Date(sessionStartTime).getTime();
        },

        getSessionData: () => {
          const {
            sessionId,
            sessionStartTime,
            sessionActive,
            sessionMetrics,
            getSessionDuration,
          } = get();

          return {
            sessionId,
            sessionStartTime,
            sessionActive,
            sessionDuration: getSessionDuration(),
            metrics: sessionMetrics,
          };
        },
      }),
      {
        name: 'session-store',
        // Only persist user preferences, not session data
        partialize: (state) => ({
          userPreferences: state.userPreferences,
        }),
      }
    ),
    {
      name: 'session-store',
    }
  )
);

export default useSessionStore;
