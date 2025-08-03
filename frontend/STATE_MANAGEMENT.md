# Frontend State Management Setup

## Overview

This document outlines the state management strategy for the NET-EST frontend application, preparing for future scalability requirements.

## Current State

The frontend currently manages state through React's built-in `useState` and `useEffect` hooks. This works well for the current scope but may need enhancement as the application grows.

## Recommended State Management Architecture

### State Categories

1. **UI State**: Component-level state (form inputs, modal visibility, loading states)
2. **Server State**: Data from API calls (analysis results, user preferences)
3. **Global State**: Application-wide state (user session, theme, language)

### Recommended Libraries

#### For Immediate Implementation
```json
{
  "dependencies": {
    "zustand": "^4.4.0",
    "@tanstack/react-query": "^5.0.0"
  }
}
```

#### Future Considerations (when needed)
```json
{
  "devDependencies": {
    "@reduxjs/toolkit": "^2.0.0",
    "redux-persist": "^6.0.0"
  }
}
```

## Implementation Plan

### Phase 1: Zustand for Global State

Create a simple, lightweight store for application-wide state:

```javascript
// src/stores/useAppStore.js
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

const useAppStore = create()(
  devtools(
    persist(
      (set, get) => ({
        // UI State
        isLoading: false,
        currentPage: 'home',
        sidebarOpen: false,
        theme: 'light',
        
        // User State
        sessionId: null,
        preferences: {
          language: 'pt-BR',
          analysisHistory: true,
          autoSave: true,
        },
        
        // Analysis State
        currentAnalysis: null,
        analysisHistory: [],
        
        // Actions
        setLoading: (loading) => set({ isLoading: loading }),
        setCurrentPage: (page) => set({ currentPage: page }),
        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        setTheme: (theme) => set({ theme }),
        
        // Session Actions
        initSession: (sessionId) => set({ sessionId }),
        updatePreferences: (prefs) => set((state) => ({
          preferences: { ...state.preferences, ...prefs }
        })),
        
        // Analysis Actions
        setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),
        addToHistory: (analysis) => set((state) => ({
          analysisHistory: [analysis, ...state.analysisHistory.slice(0, 9)] // Keep last 10
        })),
        clearHistory: () => set({ analysisHistory: [] }),
      }),
      {
        name: 'net-est-storage',
        partialize: (state) => ({
          preferences: state.preferences,
          theme: state.theme,
          analysisHistory: state.analysisHistory,
        }),
      }
    ),
    {
      name: 'NET-EST Store',
    }
  )
)

export default useAppStore
```

### Phase 2: React Query for Server State

Implement efficient server state management:

```javascript
// src/hooks/useAnalysisQuery.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'

export const useAnalysisQuery = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.get('/health'),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
  })
}

export const useTextAnalysisMutation = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data) => api.post('/analyze/text-input', data),
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['analysis'] })
      
      // Optionally cache the result
      queryClient.setQueryData(['analysis', data.id], data)
    },
  })
}

export const useSemanticAlignmentMutation = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data) => api.post('/analyze/semantic-alignment', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analysis'] })
    },
  })
}
```

### Phase 3: Enhanced Error Handling

```javascript
// src/stores/useErrorStore.js
import { create } from 'zustand'

const useErrorStore = create((set) => ({
  errors: [],
  
  addError: (error) => set((state) => ({
    errors: [...state.errors, {
      id: Date.now(),
      message: error.message || 'An error occurred',
      type: error.type || 'error',
      timestamp: new Date().toISOString(),
    }]
  })),
  
  removeError: (id) => set((state) => ({
    errors: state.errors.filter(error => error.id !== id)
  })),
  
  clearErrors: () => set({ errors: [] }),
}))

export default useErrorStore
```

## Integration Examples

### Using in Components

```jsx
// Example: Using the app store in a component
import useAppStore from '../stores/useAppStore'
import { useTextAnalysisMutation } from '../hooks/useAnalysisQuery'

const TextInputComponent = () => {
  const { 
    isLoading, 
    setLoading, 
    currentAnalysis, 
    setCurrentAnalysis,
    addToHistory 
  } = useAppStore()
  
  const analysisMutation = useTextAnalysisMutation()
  
  const handleSubmit = async (data) => {
    setLoading(true)
    try {
      const result = await analysisMutation.mutateAsync(data)
      setCurrentAnalysis(result)
      addToHistory(result)
    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div>
      {isLoading && <div>Processing...</div>}
      {currentAnalysis && (
        <div>Analysis Result: {currentAnalysis.result}</div>
      )}
      {/* Component JSX */}
    </div>
  )
}
```

## Performance Considerations

### State Optimization
- Use `shallow` comparison for Zustand subscriptions when needed
- Implement selector functions to prevent unnecessary re-renders
- Use React Query's built-in caching and background updates

### Memory Management  
- Limit history arrays to reasonable sizes (e.g., last 10 analyses)
- Implement cleanup for unused cached data
- Use React Query's garbage collection features

## Migration Strategy

### Step 1: Install Dependencies
```bash
npm install zustand @tanstack/react-query
```

### Step 2: Setup Providers
```jsx
// src/main.jsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

// Wrap your app
<QueryClientProvider client={queryClient}>
  <App />
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

### Step 3: Gradual Migration
1. Start with global UI state (theme, sidebar, loading)
2. Move API calls to React Query
3. Implement persistent state for user preferences
4. Add error handling and notifications

## Future Enhancements

### When Application Grows
- **Redux Toolkit**: For complex state logic and time-travel debugging
- **Redux Persist**: For advanced persistence requirements
- **Recoil/Jotai**: For fine-grained reactivity if needed

### Performance Monitoring
- React Developer Tools Profiler
- React Query DevTools
- Zustand DevTools

## Success Metrics

- **Reduced prop drilling**: Easier component communication
- **Better UX**: Persistent user preferences and analysis history
- **Improved performance**: Efficient server state caching
- **Developer experience**: Easier state debugging and management

This setup provides a solid foundation for state management that can scale with the application's growth while maintaining good performance and developer experience.
