/**
 * menuPositionCalculator.js - Phase 0: Dual Menu System Architecture
 * 
 * Utility functions for calculating optimal menu positions that remain within viewport bounds.
 * Handles both circular hover menus and hierarchical strategy menus with responsive positioning.
 * 
 * @created 2025-09-25
 * @phase Phase 0: Complete Interactive Foundation
 */

// Menu dimension constants
export const MENU_DIMENSIONS = {
  CIRCULAR: {
    width: 120,
    height: 120,
    radius: 60
  },
  HIERARCHICAL: {
    width: 320,
    height: 450,
    maxHeight: 500
  },
  TOOLTIP: {
    width: 200,
    height: 80
  }
};

// Position preferences and offsets
export const POSITION_CONFIG = {
  HOVER_OFFSET: 10, // Distance from trigger element
  EDGE_MARGIN: 20, // Minimum distance from viewport edges (increased)
  SELECTION_OFFSET: 10, // Distance from text selection (increased)
  CIRCULAR_RADIUS: 80 // Distance from tag center for circular menu
};

/**
 * Gets current viewport dimensions
 * @returns {Object} Viewport width and height
 */
export function getViewportDimensions() {
  return {
    width: window.innerWidth,
    height: window.innerHeight
  };
}

/**
 * Calculates optimal position for circular hover menu around a tag
 * @param {HTMLElement} tagElement - The superscript tag element
 * @param {Object} menuDimensions - Menu width/height dimensions
 * @returns {Object} Optimal position coordinates
 */
export function calculateCircularMenuPosition(tagElement, menuDimensions = MENU_DIMENSIONS.CIRCULAR) {
  if (!tagElement) {
    console.warn('calculateCircularMenuPosition: tagElement is required');
    return { x: 0, y: 0 };
  }

  const tagRect = tagElement.getBoundingClientRect();
  const viewport = getViewportDimensions();
  
  // Calculate tag center
  const tagCenterX = tagRect.left + tagRect.width / 2;
  const tagCenterY = tagRect.top + tagRect.height / 2;
  
  // Default position: centered on tag
  let x = tagCenterX - menuDimensions.width / 2;
  let y = tagCenterY - menuDimensions.height / 2;
  
  // Ensure menu stays within viewport bounds
  x = Math.max(POSITION_CONFIG.EDGE_MARGIN, 
      Math.min(x, viewport.width - menuDimensions.width - POSITION_CONFIG.EDGE_MARGIN));
  
  y = Math.max(POSITION_CONFIG.EDGE_MARGIN, 
      Math.min(y, viewport.height - menuDimensions.height - POSITION_CONFIG.EDGE_MARGIN));
  
  return { x, y };
}

/**
 * Calculates optimal position for hierarchical strategy menu
 * @param {Object} selectionCoords - Text selection coordinates
 * @param {Object} menuDimensions - Menu width/height dimensions
 * @returns {Object} Optimal position coordinates with adjustment info
 */
export function calculateHierarchicalMenuPosition(selectionCoords, menuDimensions = MENU_DIMENSIONS.HIERARCHICAL) {
  if (!selectionCoords) {
    console.warn('calculateHierarchicalMenuPosition: selectionCoords is required');
    return { x: 0, y: 0 };
  }

  const viewport = getViewportDimensions();
  let { x, y } = selectionCoords;
  
  // Start with menu dimensions, might be adjusted
  let adjustedWidth = menuDimensions.width;
  let adjustedHeight = menuDimensions.height;
  
  // Primary position: below selection end, centered horizontally
  let finalX = x - adjustedWidth / 2;
  let finalY = y + POSITION_CONFIG.SELECTION_OFFSET;
  
  // Horizontal bounds checking with priority order
  if (finalX < POSITION_CONFIG.EDGE_MARGIN) {
    // Too far left - align to left edge with margin
    finalX = POSITION_CONFIG.EDGE_MARGIN;
  } else if (finalX + adjustedWidth > viewport.width - POSITION_CONFIG.EDGE_MARGIN) {
    // Too far right - check if we can fit by aligning to right edge
    const rightAlignedX = viewport.width - adjustedWidth - POSITION_CONFIG.EDGE_MARGIN;
    if (rightAlignedX >= POSITION_CONFIG.EDGE_MARGIN) {
      finalX = rightAlignedX;
    } else {
      // Screen too narrow - reduce width and center
      adjustedWidth = viewport.width - 2 * POSITION_CONFIG.EDGE_MARGIN;
      finalX = POSITION_CONFIG.EDGE_MARGIN;
    }
  }
  
  // Vertical bounds checking with smart repositioning
  const availableSpaceBelow = viewport.height - finalY - POSITION_CONFIG.EDGE_MARGIN;
  const availableSpaceAbove = y - POSITION_CONFIG.SELECTION_OFFSET - POSITION_CONFIG.EDGE_MARGIN;
  
  if (adjustedHeight <= availableSpaceBelow) {
    // Fits below - keep current position
  } else if (adjustedHeight <= availableSpaceAbove) {
    // Doesn't fit below but fits above - position above selection
    finalY = y - adjustedHeight - POSITION_CONFIG.SELECTION_OFFSET;
  } else {
    // Doesn't fit in either direction - use the larger space and adjust height
    if (availableSpaceBelow >= availableSpaceAbove) {
      // Use space below
      adjustedHeight = Math.max(300, availableSpaceBelow); // Minimum usable height
      finalY = y + POSITION_CONFIG.SELECTION_OFFSET;
    } else {
      // Use space above
      adjustedHeight = Math.max(300, availableSpaceAbove); // Minimum usable height
      finalY = POSITION_CONFIG.EDGE_MARGIN;
    }
  }
  
  // Final safety check - ensure menu doesn't go off screen
  finalY = Math.max(POSITION_CONFIG.EDGE_MARGIN, finalY);
  finalY = Math.min(finalY, viewport.height - adjustedHeight - POSITION_CONFIG.EDGE_MARGIN);
  
  console.log('Menu positioning:', {
    original: { x, y },
    final: { x: finalX, y: finalY },
    viewport,
    adjustedDimensions: { width: adjustedWidth, height: adjustedHeight },
    availableSpaceBelow,
    availableSpaceAbove
  });
  
  return { 
    x: finalX, 
    y: finalY, 
    adjustedWidth, 
    adjustedHeight,
    fitsOriginalSize: adjustedWidth === menuDimensions.width && adjustedHeight === menuDimensions.height
  };
}

/**
 * Calculates pointer corridor geometry for stable hover interactions
 * Used to prevent menu dismissal during diagonal cursor movement
 * @param {HTMLElement} triggerElement - The element that triggers the menu
 * @param {HTMLElement} menuElement - The menu element
 * @returns {Object} Corridor geometry for hover stability
 */
export function calculatePointerCorridor(triggerElement, menuElement) {
  if (!triggerElement || !menuElement) {
    return null;
  }

  const triggerRect = triggerElement.getBoundingClientRect();
  const menuRect = menuElement.getBoundingClientRect();
  
  // Create expanded bounding box that includes both elements plus margin
  const corridor = {
    left: Math.min(triggerRect.left, menuRect.left) - POSITION_CONFIG.HOVER_OFFSET,
    right: Math.max(triggerRect.right, menuRect.right) + POSITION_CONFIG.HOVER_OFFSET,
    top: Math.min(triggerRect.top, menuRect.top) - POSITION_CONFIG.HOVER_OFFSET,
    bottom: Math.max(triggerRect.bottom, menuRect.bottom) + POSITION_CONFIG.HOVER_OFFSET
  };
  
  return corridor;
}

/**
 * Checks if a point is within the pointer corridor
 * @param {Object} point - Point with x, y coordinates
 * @param {Object} corridor - Corridor bounds from calculatePointerCorridor
 * @returns {boolean} Whether point is within corridor
 */
export function isPointInCorridor(point, corridor) {
  if (!point || !corridor) {
    return false;
  }
  
  return point.x >= corridor.left && 
         point.x <= corridor.right && 
         point.y >= corridor.top && 
         point.y <= corridor.bottom;
}

/**
 * Gets text selection coordinates from browser Selection API
 * @returns {Object|null} Selection coordinates or null if no selection
 */
export function getSelectionCoordinates() {
  const selection = window.getSelection();
  if (!selection.rangeCount || selection.isCollapsed) {
    return null;
  }
  
  const range = selection.getRangeAt(0);
  const rect = range.getBoundingClientRect();
  
  // Return coordinates at end of selection
  return {
    x: rect.right,
    y: rect.bottom,
    width: rect.width,
    height: rect.height,
    startX: rect.left,
    startY: rect.top
  };
}

/**
 * Adjusts position to avoid overlapping with existing menus or UI elements
 * @param {Object} position - Current position
 * @param {Array} avoidElements - Elements to avoid overlapping
 * @returns {Object} Adjusted position
 */
export function adjustPositionToAvoidOverlap(position, avoidElements = []) {
  if (!avoidElements.length) {
    return position;
  }
  
  let adjustedPosition = { ...position };
  
  for (const element of avoidElements) {
    const elementRect = element.getBoundingClientRect();
    
    // Simple collision detection and adjustment
    if (position.x < elementRect.right + POSITION_CONFIG.EDGE_MARGIN &&
        position.x + MENU_DIMENSIONS.HIERARCHICAL.width > elementRect.left - POSITION_CONFIG.EDGE_MARGIN &&
        position.y < elementRect.bottom + POSITION_CONFIG.EDGE_MARGIN &&
        position.y + MENU_DIMENSIONS.HIERARCHICAL.height > elementRect.top - POSITION_CONFIG.EDGE_MARGIN) {
      
      // Move to the right of the overlapping element
      adjustedPosition.x = elementRect.right + POSITION_CONFIG.EDGE_MARGIN;
      
      // If that pushes it off-screen, move to the left instead
      if (adjustedPosition.x + MENU_DIMENSIONS.HIERARCHICAL.width > window.innerWidth - POSITION_CONFIG.EDGE_MARGIN) {
        adjustedPosition.x = elementRect.left - MENU_DIMENSIONS.HIERARCHICAL.width - POSITION_CONFIG.EDGE_MARGIN;
      }
    }
  }
  
  return adjustedPosition;
}

export default {
  MENU_DIMENSIONS,
  POSITION_CONFIG,
  getViewportDimensions,
  calculateCircularMenuPosition,
  calculateHierarchicalMenuPosition,
  calculatePointerCorridor,
  isPointInCorridor,
  getSelectionCoordinates,
  adjustPositionToAvoidOverlap
};