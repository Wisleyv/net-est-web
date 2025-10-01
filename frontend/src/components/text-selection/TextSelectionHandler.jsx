/**
 * TextSelectionHandler.jsx - Phase 0: Text Selection Integration
 * 
 * Detects text selection in the target text panel and triggers hierarchical menu
 * for new strategy annotation creation. Integrates with existing annotation context.
 * 
 * @created 2025-09-25
 * @phase Phase 0: Complete Interactive Foundation
 */

import React, { useCallback, useEffect, useRef } from 'react';
import { useAnnotationMenu } from '../../contexts/AnnotationMenuContext.jsx';
import './TextSelectionHandler.css';

/**
 * Configuration for text selection behavior
 */
const SELECTION_CONFIG = {
  MIN_SELECTION_LENGTH: 3, // Minimum characters to trigger menu
  MAX_SELECTION_LENGTH: 500, // Maximum characters to prevent accidental selections
  DEBOUNCE_DELAY: 200, // Delay before processing selection to avoid excessive calls (increased)
  STABILITY_DELAY: 300, // Additional delay to ensure selection is stable (new)
  MENU_OFFSET_Y: 10 // Vertical offset from selection for menu positioning
};

/**
 * TextSelectionHandler - Wraps target text and handles selection events
 * 
 * Features:
 * - Detects text selection within target text area
 * - Validates selection boundaries and length
 * - Triggers hierarchical menu for strategy selection
 * - Prevents interference with existing strategy markers
 * - Provides visual feedback during selection process
 */
export function TextSelectionHandler({ children, disabled = false }) {
  const selectionTimeoutRef = useRef(null);
  const lastSelectionRef = useRef(null);
  const containerRef = useRef(null);
  const isMouseDownRef = useRef(false);
  const { showHierarchicalMenu, isVisible, activeMenu, hideMenu } = useAnnotationMenu();

  /**
   * Clears current text selection
   */
  const clearSelection = useCallback(() => {
    const selection = window.getSelection();
    if (selection) {
      selection.removeAllRanges();
    }
    lastSelectionRef.current = null;
  }, []);

  /**
   * Validates if a text selection is appropriate for strategy annotation
   */
  const validateSelection = useCallback((selection, range) => {
    // Check basic selection criteria
    const text = selection.toString().trim();
    if (text.length < SELECTION_CONFIG.MIN_SELECTION_LENGTH) {
      return { valid: false, reason: 'Selection too short' };
    }
    
    if (text.length > SELECTION_CONFIG.MAX_SELECTION_LENGTH) {
      return { valid: false, reason: 'Selection too long' };
    }

    // Check if selection contains existing strategy markers
    const tempDiv = document.createElement('div');
    try {
      range.cloneContents().childNodes.forEach(node => {
        tempDiv.appendChild(node.cloneNode(true));
      });

      // Remove zero-width superscript markers so adjacency remains selectable
      tempDiv.querySelectorAll('.strategy-marker').forEach(markerNode => markerNode.remove());

      const hasStrategyHighlights = tempDiv.querySelector('[data-strategy-codes]');
      if (hasStrategyHighlights) {
        console.info('💡 Selection overlaps with existing annotations. Select unmarked text to add new strategies.');
        return { valid: false, reason: 'Selection overlaps with existing strategy highlights' };
      }
    } catch (error) {
      console.warn('Selection validation error:', error);
      return { valid: false, reason: 'Selection validation failed' };
    }

    return { valid: true, text, range };
  }, []);

  /**
   * Calculates optimal position for hierarchical menu based on selection
   */
  const calculateMenuPosition = useCallback((range) => {
    try {
      const rect = range.getBoundingClientRect();
      const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
      const scrollY = window.pageYOffset || document.documentElement.scrollTop;
      
      // Position menu at center of selection, slightly below
      return {
        x: rect.left + scrollX + (rect.width / 2),
        y: rect.bottom + scrollY + SELECTION_CONFIG.MENU_OFFSET_Y
      };
    } catch (error) {
      console.warn('Menu position calculation error:', error);
      // Fallback to cursor position
      return { x: 0, y: 0 };
    }
  }, []);

  /**
   * Handles text selection events with debouncing and menu interference prevention
   */
  const handleSelectionChange = useCallback(() => {
    console.debug('🔍 Selection change detected, processing...');
    
    // Clear existing timeout
    if (selectionTimeoutRef.current) {
      clearTimeout(selectionTimeoutRef.current);
    }

    // Debounce selection processing
    selectionTimeoutRef.current = setTimeout(() => {
      if (disabled) {
        console.debug('Selection handler disabled, skipping');
        return;
      }

      const selection = window.getSelection();
      if (!selection || selection.rangeCount === 0) {
        console.debug('No selection or no ranges, clearing last selection');
        lastSelectionRef.current = null;
        return;
      }

      const range = selection.getRangeAt(0);
      const selectionText = selection.toString().trim();

      console.debug('📝 Selection text:', { text: selectionText, length: selectionText.length });

      // Avoid processing same selection repeatedly
      if (lastSelectionRef.current === selectionText) {
        console.debug('Same selection as before, skipping');
        return;
      }
      lastSelectionRef.current = selectionText;

      // Don't show menu if selection is collapsed
      if (selection.isCollapsed) {
        console.debug('Selection collapsed, skipping menu');
        return;
      }

      // Validate selection
      const validation = validateSelection(selection, range);
      if (!validation.valid) {
        console.debug('❌ Selection validation failed:', validation.reason);
        return;
      }
      console.debug('✅ Selection validation passed');

      // Check if selection is within target text area
      const targetTextContainer = range.commonAncestorContainer;
      const strategyLayer = targetTextContainer.nodeType === Node.TEXT_NODE 
        ? targetTextContainer.parentElement?.closest('.strategy-superscript-layer')
        : targetTextContainer.closest?.('.strategy-superscript-layer');

      console.debug('🎯 Target container check:', { 
        nodeType: targetTextContainer.nodeType, 
        hasStrategyLayer: !!strategyLayer,
        containerName: targetTextContainer.nodeName 
      });

      if (!strategyLayer) {
        console.debug('❌ Selection not within target text area');
        return;
      }

      // Don't show menu if another menu is already visible
      if (isVisible && activeMenu) {
        console.debug('❌ Menu already visible, skipping selection menu');
        return;
      }

      console.debug('🚀 Proceeding to show menu after stability delay...');

      // Additional delay to ensure selection is stable before showing menu
      setTimeout(() => {
        // Re-check selection is still valid after delay
        const currentSelection = window.getSelection();
        if (!currentSelection || currentSelection.toString().trim() !== validation.text) {
          console.debug('Selection changed during stability delay, cancelling menu');
          return;
        }

        // Final check - ensure selection is still stable
        if (isMouseDownRef.current) {
          console.debug('Selection still in progress during stability check, cancelling menu');
          return;
        }

        // Calculate menu position and trigger hierarchical menu
        const position = calculateMenuPosition(range);
        const selectionRange = {
          x: position.x,
          y: position.y,
          text: validation.text,
          range: range.cloneRange() // Clone range for later use
        };

        console.log('🎯 Text selection detected:', {
          text: validation.text,
          position,
          length: validation.text.length
        });

        console.log('📞 Calling showHierarchicalMenu with:', { selectionRange, position });

        // Trigger hierarchical menu for strategy selection
        showHierarchicalMenu(selectionRange, position);
      }, SELECTION_CONFIG.STABILITY_DELAY); // Additional delay to prevent interference

    }, SELECTION_CONFIG.DEBOUNCE_DELAY);
  }, [disabled, validateSelection, calculateMenuPosition, showHierarchicalMenu, isVisible, activeMenu]);

  /**
   * Handles mouse down events to track selection state
   */
  const handleMouseDown = useCallback((event) => {
    if (containerRef.current && containerRef.current.contains(event.target)) {
      isMouseDownRef.current = true;
    }
  }, []);

  /**
   * Handles mouse up events to detect end of selection
   */
  const handleMouseUp = useCallback((event) => {
    if (isMouseDownRef.current) {
      console.debug('🖱️ Mouse up detected, clearing mouse down flag');
      isMouseDownRef.current = false;
      // Give selection time to stabilize, then trigger handler if there's a valid selection
      setTimeout(() => {
        if (!disabled) {
          const selection = window.getSelection();
          if (selection && !selection.isCollapsed && selection.toString().trim().length > 0) {
            console.debug('🖱️ Mouse up with valid selection, triggering handler');
            handleSelectionChange();
          } else {
            console.debug('🖱️ Mouse up but no valid selection found');
          }
        }
      }, 100);
    }
  }, [disabled, handleSelectionChange]);

  /**
   * Handles click outside selection area to clear selection
   */
  const handleClickOutside = useCallback((event) => {
    if (containerRef.current && !containerRef.current.contains(event.target)) {
      if (lastSelectionRef.current) {
        clearSelection();
      }
    }
  }, [clearSelection]);

  /**
   * Setup and cleanup selection event listeners
   */
  useEffect(() => {
    if (disabled) return;

    // Add selection change listener (but with reduced frequency)
    document.addEventListener('selectionchange', handleSelectionChange);
    
    // Add mouse tracking listeners
    document.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mouseup', handleMouseUp);
    
    // Add click outside listener
    document.addEventListener('mousedown', handleClickOutside);

    // Cleanup
    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
      document.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('mousedown', handleClickOutside);
      if (selectionTimeoutRef.current) {
        clearTimeout(selectionTimeoutRef.current);
      }
    };
  }, [handleSelectionChange, handleMouseDown, handleMouseUp, handleClickOutside, disabled]);

  /**
   * Clear selection when hierarchical menu becomes visible
   */
  useEffect(() => {
    if (isVisible && activeMenu === 'hierarchical') {
      // Clear selection after menu appears to avoid visual confusion
      setTimeout(clearSelection, 100);
    }
  }, [isVisible, activeMenu, clearSelection]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (selectionTimeoutRef.current) {
        clearTimeout(selectionTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div 
      ref={containerRef}
      className="text-selection-handler" 
      data-testid="text-selection-handler"
      data-selection-enabled={!disabled}
    >
      {children}
    </div>
  );
}

export default TextSelectionHandler;