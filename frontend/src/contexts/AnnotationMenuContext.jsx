/**
 * AnnotationMenuContext.jsx - Phase 0: Dual Menu System Architecture
 * 
 * Centralized context for managing annotation menu state across the application.
 * Supports both circular hover menus (existing tags) and hierarchical strategy menus (new tags).
 * 
 * @created 2025-09-25
 * @phase Phase 0: Complete Interactive Foundation
 */

import React, { createContext, useContext, useReducer, useCallback } from 'react';

// Menu state structure as per implementation specification
const initialState = {
  activeMenu: null, // 'circular' | 'hierarchical' | null
  targetTag: null, // Strategy tag being operated on
  selectedAnnotation: null, // Full annotation object for circular menu
  selectionRange: null, // Text selection for new tag creation
  position: { x: 0, y: 0 }, // Menu positioning coordinates
  isVisible: false, // Menu visibility state
  hoveredElement: null, // Currently hovered element for circular menu
  selectedStrategy: null, // Selected strategy for hierarchical menu
  rationale: '', // User rationale input
  error: null // Error state for error handling
};

// Action types for state management
const ActionTypes = {
  SHOW_CIRCULAR_MENU: 'SHOW_CIRCULAR_MENU',
  SHOW_HIERARCHICAL_MENU: 'SHOW_HIERARCHICAL_MENU',
  HIDE_MENU: 'HIDE_MENU',
  SET_POSITION: 'SET_POSITION',
  SET_TARGET_TAG: 'SET_TARGET_TAG',
  SET_SELECTION_RANGE: 'SET_SELECTION_RANGE',
  SET_SELECTED_STRATEGY: 'SET_SELECTED_STRATEGY',
  SET_RATIONALE: 'SET_RATIONALE',
  SET_ERROR: 'SET_ERROR',
  RESET_STATE: 'RESET_STATE'
};

// Reducer for menu state management
function menuReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SHOW_CIRCULAR_MENU:
      return {
        ...state,
        activeMenu: 'circular',
        targetTag: action.payload.targetTag,
        selectedAnnotation: action.payload.annotation, // Add full annotation object
        position: action.payload.position,
        hoveredElement: action.payload.element,
        isVisible: true,
        error: null
      };

    case ActionTypes.SHOW_HIERARCHICAL_MENU:
      return {
        ...state,
        activeMenu: 'hierarchical',
        selectionRange: action.payload.selectionRange,
        position: action.payload.position,
        isVisible: true,
        error: null
      };

    case ActionTypes.HIDE_MENU:
      return {
        ...state,
        activeMenu: null,
        isVisible: false,
        hoveredElement: null,
        selectedStrategy: null,
        error: null
      };

    case ActionTypes.SET_POSITION:
      return {
        ...state,
        position: action.payload
      };

    case ActionTypes.SET_TARGET_TAG:
      return {
        ...state,
        targetTag: action.payload
      };

    case ActionTypes.SET_SELECTION_RANGE:
      return {
        ...state,
        selectionRange: action.payload
      };

    case ActionTypes.SET_SELECTED_STRATEGY:
      return {
        ...state,
        selectedStrategy: action.payload
      };

    case ActionTypes.SET_RATIONALE:
      return {
        ...state,
        rationale: action.payload
      };

    case ActionTypes.SET_ERROR:
      return {
        ...state,
        error: action.payload
      };

    case ActionTypes.RESET_STATE:
      return initialState;

    default:
      return state;
  }
}

// Context creation
const AnnotationMenuContext = createContext(null);

// Custom hook for using the annotation menu context
export function useAnnotationMenu() {
  const context = useContext(AnnotationMenuContext);
  if (!context) {
    throw new Error('useAnnotationMenu must be used within an AnnotationMenuProvider');
  }
  return context;
}

// Provider component
export function AnnotationMenuProvider({ children }) {
  const [state, dispatch] = useReducer(menuReducer, initialState);

  // Action creators with useCallback for performance optimization
  const showCircularMenu = useCallback((annotation, position, element) => {
    dispatch({
      type: ActionTypes.SHOW_CIRCULAR_MENU,
      payload: { 
        targetTag: annotation?.tagType, // Keep legacy field for compatibility
        annotation: annotation, // Full annotation object
        position, 
        element 
      }
    });
  }, []);

  const showHierarchicalMenu = useCallback((selectionRange, position) => {
    dispatch({
      type: ActionTypes.SHOW_HIERARCHICAL_MENU,
      payload: { selectionRange, position }
    });
  }, []);

  const hideMenu = useCallback(() => {
    dispatch({ type: ActionTypes.HIDE_MENU });
  }, []);

  const setPosition = useCallback((position) => {
    dispatch({ type: ActionTypes.SET_POSITION, payload: position });
  }, []);

  const setTargetTag = useCallback((tag) => {
    dispatch({ type: ActionTypes.SET_TARGET_TAG, payload: tag });
  }, []);

  const setSelectionRange = useCallback((range) => {
    dispatch({ type: ActionTypes.SET_SELECTION_RANGE, payload: range });
  }, []);

  const setSelectedStrategy = useCallback((strategy) => {
    dispatch({ type: ActionTypes.SET_SELECTED_STRATEGY, payload: strategy });
  }, []);

  const setRationale = useCallback((rationale) => {
    dispatch({ type: ActionTypes.SET_RATIONALE, payload: rationale });
  }, []);

  const setError = useCallback((error) => {
    dispatch({ type: ActionTypes.SET_ERROR, payload: error });
  }, []);

  const resetState = useCallback(() => {
    dispatch({ type: ActionTypes.RESET_STATE });
  }, []);

  // Context value
  const contextValue = {
    // State
    ...state,
    
    // Actions
    showCircularMenu,
    showHierarchicalMenu,
    hideMenu,
    setPosition,
    setTargetTag,
    setSelectionRange,
    setSelectedStrategy,
    setRationale,
    setError,
    resetState
  };

  return (
    <AnnotationMenuContext.Provider value={contextValue}>
      {children}
    </AnnotationMenuContext.Provider>
  );
}

export default AnnotationMenuContext;