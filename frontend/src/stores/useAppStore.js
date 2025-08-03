/**
 * Global Application State Store
 * Manages system status, UI state, and general app configuration
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

const useAppStore = create(
  devtools(
    (set, get) => ({
      // System Status
      systemStatus: null,
      systemHealthy: false,
      lastHealthCheck: null,

      // UI State
      currentPhase: 'input', // 'input' | 'processed' | 'alignment' | 'results'
      loading: false,
      globalError: null,
      notifications: [],

      // App Configuration
      config: {
        apiTimeout: 30000,
        maxFileSize: 10 * 1024 * 1024, // 10MB
        supportedFormats: ['txt', 'md', 'docx', 'odt', 'pdf'],
        autoSave: true,
      },

      // Actions
      setSystemStatus: (status) =>
        set(
          (_state) => ({
            systemStatus: status,
            systemHealthy: status?.status === 'healthy',
            lastHealthCheck: new Date().toISOString(),
          }),
          false,
          'setSystemStatus'
        ),

      setCurrentPhase: (phase) =>
        set(
          (_state) => ({
            currentPhase: phase,
          }),
          false,
          'setCurrentPhase'
        ),

      setLoading: (loading) =>
        set(
          (_state) => ({
            loading,
          }),
          false,
          'setLoading'
        ),

      setGlobalError: (error) =>
        set(
          (_state) => ({
            globalError: error,
          }),
          false,
          'setGlobalError'
        ),

      clearGlobalError: () =>
        set(
          (_state) => ({
            globalError: null,
          }),
          false,
          'clearGlobalError'
        ),

      addNotification: (notification) =>
        set(
          (state) => ({
            notifications: [
              ...state.notifications,
              {
                id: Date.now(),
                timestamp: new Date().toISOString(),
                ...notification,
              },
            ],
          }),
          false,
          'addNotification'
        ),

      removeNotification: (id) =>
        set(
          (state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          }),
          false,
          'removeNotification'
        ),

      clearNotifications: () =>
        set(
          (_state) => ({
            notifications: [],
          }),
          false,
          'clearNotifications'
        ),

      // Navigation helpers
      navigateToPhase: (phase) => {
        const { setCurrentPhase, clearGlobalError } = get();
        clearGlobalError();
        setCurrentPhase(phase);
      },

      resetApp: () =>
        set(
          (_state) => ({
            currentPhase: 'input',
            loading: false,
            globalError: null,
            notifications: [],
          }),
          false,
          'resetApp'
        ),
    }),
    {
      name: 'app-store',
    }
  )
);

export default useAppStore;
