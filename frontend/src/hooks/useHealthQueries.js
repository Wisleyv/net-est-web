/**
 * Health Check API Hooks
 * React Query hooks for system health monitoring
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys, handleQueryError } from './queryClient';
import { healthAPI } from '../services/api';
import useAppStore from '../stores/useAppStore';

// Health Check Query
export const useHealthCheck = (options = {}) => {
  const setSystemStatus = useAppStore((state) => state.setSystemStatus);
  const setGlobalError = useAppStore((state) => state.setGlobalError);

  return useQuery({
    queryKey: queryKeys.health,
    queryFn: async () => {
      try {
        const response = await healthAPI.check();
        setSystemStatus(response.data);
        return response.data;
      } catch (error) {
        const errorMessage = handleQueryError(error, 'Falha na verificação de saúde do sistema');
        setGlobalError(errorMessage);
        throw error;
      }
    },
    refetchInterval: 60000, // Check every minute
    ...options,
  });
};

// System Status Query (detailed health)
export const useSystemStatus = (options = {}) => {
  return useQuery({
    queryKey: queryKeys.healthStatus,
    queryFn: async () => {
      try {
        const response = await healthAPI.status();
        return response.data;
      } catch (error) {
        const errorMessage = handleQueryError(error, 'Falha ao obter status detalhado do sistema');
        throw new Error(errorMessage);
      }
    },
    ...options,
  });
};

// Manual Health Check Mutation
export const useHealthCheckMutation = () => {
  const queryClient = useQueryClient();
  const setSystemStatus = useAppStore((state) => state.setSystemStatus);
  const setGlobalError = useAppStore((state) => state.setGlobalError);
  const clearGlobalError = useAppStore((state) => state.clearGlobalError);

  return useMutation({
    mutationFn: async () => {
      const response = await healthAPI.check();
      return response.data;
    },
    onSuccess: (data) => {
      setSystemStatus(data);
      clearGlobalError();
      
      // Invalidate and refetch health queries
      queryClient.invalidateQueries({ queryKey: queryKeys.health });
    },
    onError: (error) => {
      const errorMessage = handleQueryError(error, 'Falha na verificação manual de saúde');
      setGlobalError(errorMessage);
    },
  });
};
