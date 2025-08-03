/**
 * Text Input API Hooks
 * React Query hooks for text input processing
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys, handleQueryError } from './queryClient';
import { textInputAPI } from '../services/api';
import useAnalysisStore from '../stores/useAnalysisStore';
import useSessionStore from '../stores/useSessionStore';
import useAppStore from '../stores/useAppStore';

// Process Typed Text Mutation
export const useProcessTypedText = () => {
  const queryClient = useQueryClient();
  const { setInputText, startProcessing, completeProcessing, setProcessingError, setPreprocessingResults } = useAnalysisStore();
  const { incrementTextInput, addProcessingTime } = useSessionStore();
  const { addNotification } = useAppStore();

  return useMutation({
    mutationFn: async (textData) => {
      const startTime = Date.now();
      const response = await textInputAPI.processTyped(textData);
      const processingTime = Date.now() - startTime;
      addProcessingTime(processingTime);
      
      return response.data;
    },
    onMutate: (textData) => {
      // Optimistic update
      const analysisId = setInputText(textData.text, 'typed');
      startProcessing('preprocessing');
      incrementTextInput();
      
      return { analysisId };
    },
    onSuccess: (data, _variables, _context) => {
      setPreprocessingResults(data);
      completeProcessing();
      
      addNotification({
        type: 'success',
        title: 'Texto processado com sucesso',
        message: 'O texto foi analisado e está pronto para alinhamento semântico.',
      });

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.textInput });
    },
    onError: (error, _variables, _context) => {
      const errorMessage = handleQueryError(error, 'Falha ao processar texto digitado');
      setProcessingError(errorMessage);
      
      addNotification({
        type: 'error',
        title: 'Erro no processamento',
        message: errorMessage,
      });
    },
  });
};

// Process File Upload Mutation
export const useProcessFileUpload = () => {
  const queryClient = useQueryClient();
  const { setInputText, startProcessing, completeProcessing, setProcessingError, setPreprocessingResults } = useAnalysisStore();
  const { incrementTextInput, addProcessingTime } = useSessionStore();
  const { addNotification } = useAppStore();

  return useMutation({
    mutationFn: async (fileData) => {
      const startTime = Date.now();
      const formData = new FormData();
      formData.append('file', fileData.file);
      
      const response = await textInputAPI.processFile(formData);
      const processingTime = Date.now() - startTime;
      addProcessingTime(processingTime);
      
      return response.data;
    },
    onMutate: (fileData) => {
      // Optimistic update
      const analysisId = setInputText(
        'Carregando arquivo...', 
        'file', 
        fileData.file.name,
        fileData.file.type
      );
      startProcessing('preprocessing');
      incrementTextInput();
      
      return { analysisId };
    },
    onSuccess: (data, variables, _context) => {
      // Update with actual processed text
      setInputText(data.original_text, 'file', variables.file.name, variables.file.type);
      setPreprocessingResults(data);
      completeProcessing();
      
      addNotification({
        type: 'success',
        title: 'Arquivo processado com sucesso',
        message: `O arquivo "${variables.file.name}" foi analisado e está pronto para alinhamento semântico.`,
      });

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.textInput });
    },
    onError: (error, variables, _context) => {
      const errorMessage = handleQueryError(error, 'Falha ao processar arquivo');
      setProcessingError(errorMessage);
      
      addNotification({
        type: 'error',
        title: 'Erro no upload',
        message: `Falha ao processar o arquivo "${variables.file.name}": ${errorMessage}`,
      });
    },
  });
};

// Validate Text Mutation
export const useValidateText = () => {
  return useMutation({
    mutationFn: async (textData) => {
      const response = await textInputAPI.validate(textData);
      return response.data;
    },
    onError: (error) => {
      const errorMessage = handleQueryError(error, 'Falha na validação do texto');
      throw new Error(errorMessage);
    },
  });
};

// Text Input History Query
export const useTextInputHistory = (options = {}) => {
  return useQuery({
    queryKey: queryKeys.textInputHistory,
    queryFn: async () => {
      try {
        const response = await textInputAPI.getHistory();
        return response.data;
      } catch (error) {
        const errorMessage = handleQueryError(error, 'Falha ao carregar histórico de textos');
        throw new Error(errorMessage);
      }
    },
    ...options,
  });
};

// Get Text Input by ID Query
export const useTextInputById = (id, options = {}) => {
  return useQuery({
    queryKey: ['text-input', id],
    queryFn: async () => {
      if (!id) throw new Error('ID é obrigatório');
      
      try {
        const response = await textInputAPI.getById(id);
        return response.data;
      } catch (error) {
        const errorMessage = handleQueryError(error, 'Falha ao carregar texto');
        throw new Error(errorMessage);
      }
    },
    enabled: !!id,
    ...options,
  });
};

// Update Text Input Mutation
export const useUpdateTextInput = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useAppStore();

  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await textInputAPI.update(id, data);
      return response.data;
    },
    onSuccess: (data, variables) => {
      addNotification({
        type: 'success',
        title: 'Texto atualizado',
        message: 'As alterações foram salvas com sucesso.',
      });

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.textInput });
      queryClient.invalidateQueries({ queryKey: ['text-input', variables.id] });
    },
    onError: (error) => {
      const errorMessage = handleQueryError(error, 'Falha ao atualizar texto');
      const { addNotification } = useAppStore.getState();
      
      addNotification({
        type: 'error',
        title: 'Erro na atualização',
        message: errorMessage,
      });
    },
  });
};

// Delete Text Input Mutation
export const useDeleteTextInput = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useAppStore();

  return useMutation({
    mutationFn: async (id) => {
      await textInputAPI.delete(id);
      return id;
    },
    onSuccess: (deletedId) => {
      addNotification({
        type: 'success',
        title: 'Texto removido',
        message: 'O texto foi removido com sucesso.',
      });

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.textInput });
      queryClient.removeQueries({ queryKey: ['text-input', deletedId] });
    },
    onError: (error) => {
      const errorMessage = handleQueryError(error, 'Falha ao remover texto');
      const { addNotification } = useAppStore.getState();
      
      addNotification({
        type: 'error',
        title: 'Erro na remoção',
        message: errorMessage,
      });
    },
  });
};
