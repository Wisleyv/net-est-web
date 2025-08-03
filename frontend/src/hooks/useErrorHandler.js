/**
 * Error Handling Hook
 * Centralized error processing and user feedback
 */

import { useCallback } from 'react';
import useAppStore from '../stores/useAppStore';

export const useErrorHandler = () => {
  const { addNotification } = useAppStore();

  const handleError = useCallback((error, context = {}) => {
    console.error(`Error in ${context.component || 'unknown component'}:`, error);

    // Determine error type and message
    let errorMessage = 'Ocorreu um erro inesperado.';
    let errorTitle = 'Erro';
    let isNetworkError = false;

    if (error?.response) {
      // API Error Response
      const status = error.response.status;
      const data = error.response.data;
      
      switch (status) {
        case 400:
          errorTitle = 'Dados Inválidos';
          errorMessage = data?.detail || 'Os dados fornecidos são inválidos.';
          break;
        case 401:
          errorTitle = 'Não Autorizado';
          errorMessage = 'Você não tem permissão para realizar esta ação.';
          break;
        case 403:
          errorTitle = 'Acesso Negado';
          errorMessage = 'Acesso negado para este recurso.';
          break;
        case 404:
          errorTitle = 'Não Encontrado';
          errorMessage = 'O recurso solicitado não foi encontrado.';
          break;
        case 422:
          errorTitle = 'Erro de Validação';
          errorMessage = data?.detail || 'Erro na validação dos dados.';
          break;
        case 429:
          errorTitle = 'Muitas Requisições';
          errorMessage = 'Você está fazendo muitas requisições. Tente novamente em alguns momentos.';
          break;
        case 500:
          errorTitle = 'Erro do Servidor';
          errorMessage = 'Erro interno do servidor. Nossa equipe foi notificada.';
          break;
        case 502:
        case 503:
        case 504:
          errorTitle = 'Serviço Indisponível';
          errorMessage = 'O serviço está temporariamente indisponível. Tente novamente em alguns momentos.';
          isNetworkError = true;
          break;
        default:
          errorTitle = 'Erro HTTP';
          errorMessage = data?.detail || `Erro ${status}: ${error.response.statusText}`;
      }
    } else if (error?.code === 'NETWORK_ERROR' || !error?.response) {
      // Network Error
      errorTitle = 'Erro de Conexão';
      errorMessage = 'Não foi possível conectar ao servidor. Verifique sua conexão de internet.';
      isNetworkError = true;
    } else if (error?.message) {
      // JavaScript Error
      errorMessage = error.message;
    }

    // Add contextual information
    if (context.operation) {
      errorMessage = `Erro ao ${context.operation}: ${errorMessage}`;
    }

    // Show notification
    addNotification({
      type: 'error',
      title: errorTitle,
      message: errorMessage,
      duration: isNetworkError ? 8000 : 6000, // Longer duration for network errors
      persistent: context.persistent || false,
    });

    // Log additional context in development
    if (process.env.NODE_ENV === 'development') {
      console.group('🚨 Error Context');
      console.log('Component:', context.component);
      console.log('Operation:', context.operation);
      console.log('Error Object:', error);
      console.log('Is Network Error:', isNetworkError);
      console.groupEnd();
    }

    return {
      message: errorMessage,
      title: errorTitle,
      isNetworkError,
      handled: true,
    };
  }, [addNotification]);

  const handleSuccess = useCallback((message, title = 'Sucesso') => {
    addNotification({
      type: 'success',
      title,
      message,
      duration: 4000,
    });
  }, [addNotification]);

  const handleWarning = useCallback((message, title = 'Atenção') => {
    addNotification({
      type: 'warning',
      title,
      message,
      duration: 6000,
    });
  }, [addNotification]);

  const handleInfo = useCallback((message, title = 'Informação') => {
    addNotification({
      type: 'info',
      title,
      message,
      duration: 5000,
    });
  }, [addNotification]);

  return {
    handleError,
    handleSuccess,
    handleWarning,
    handleInfo,
  };
};

export default useErrorHandler;
