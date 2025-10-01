/**
 * CircularContextMenu.jsx - Phase 0: Dual Menu System Architecture
 * 
 * Circular context menu for existing annotation tags with 4 actions:
 * Validate, Replace, Delete, Edit Range. Provides hover stability with
 * pointer corridor and accessible keyboard navigation.
 * 
 * @created 2025-09-25
 * @phase Phase 0: Complete Interactive Foundation
 */

import React, { useEffect, useRef, useCallback, useState } from 'react';
import { Check, Edit, Trash2, Replace } from 'lucide-react';
import { useAnnotationMenu } from '../../contexts/AnnotationMenuContext.jsx';
import { calculateCircularMenuPosition } from '../../utils/menuPositionCalculator.js';
import { AccessibilityMenuWrapper, MenuButton } from '../accessibility/AccessibilityMenuWrapper.jsx';
import './CircularContextMenu.css';

/**
 * CircularContextMenu - 4-button circular menu for existing tag actions
 * Layout: Top(Validate), Right(Replace), Bottom(Delete), Left(Edit Range)
 */
export function CircularContextMenu() {
  const menuRef = useRef(null);
  const corridorRef = useRef(null);
  const [menuPosition, setMenuPosition] = useState(null);
  const [isStable, setIsStable] = useState(false);
  
  const {
    isVisible,
    activeMenu,
    selectedAnnotation,
    hideMenu,
    showHierarchicalMenu,
    // These functions will be implemented in later phases
    setRationaleDialog = () => console.log('Rationale dialog not yet implemented'),
    updateAnnotationTag = () => console.log('Update annotation not yet implemented'),
    deleteAnnotation = () => console.log('Delete annotation not yet implemented'),
    setSelectionMode = () => console.log('Selection mode not yet implemented')
  } = useAnnotationMenu();
  
  // Calculate menu position based on selected annotation
  useEffect(() => {
    if (isVisible && activeMenu === 'circular' && selectedAnnotation) {
      const { element, tagType, text, range } = selectedAnnotation;
      
      if (element) {
        const coords = calculateCircularMenuPosition(element, {
          width: 120,
          height: 120
        });
        
        const position = {
          top: coords.y,
          left: coords.x,
          corridor: null // Will be added if needed for hover stability
        };
        
        setMenuPosition(position);
        setIsStable(true);
      }
    } else {
      setMenuPosition(null);
      setIsStable(false);
    }
  }, [isVisible, activeMenu, selectedAnnotation]);
  
  // Handle mouse leave with delay for pointer corridor stability
  const handleMouseLeave = useCallback(() => {
    // Small delay to allow movement through pointer corridor
    setTimeout(() => {
      if (menuRef.current && !menuRef.current.matches(':hover')) {
        hideMenu();
      }
    }, 150);
  }, [hideMenu]);
  
  // Action handlers
  const handleValidate = useCallback(() => {
    if (!selectedAnnotation) return;
    
    setRationaleDialog({
      isOpen: true,
      action: 'validate',
      annotation: selectedAnnotation,
      title: 'Validate Strategy Tag',
      message: `Confirm that the "${selectedAnnotation.tagType}" tag is correctly applied to this text.`,
      placeholder: 'Optional: Add validation notes or context...'
    });
  }, [selectedAnnotation, setRationaleDialog]);
  
  const handleReplace = useCallback(() => {
    if (!selectedAnnotation || !showHierarchicalMenu) return;
    
    // Create a selection range object for hierarchical menu positioning
    const element = selectedAnnotation.element;
    const rect = element.getBoundingClientRect();
    const selectionRange = {
      x: rect.left + window.scrollX + rect.width / 2, // Center of the tag
      y: rect.bottom + window.scrollY + 5 // Below the tag
    };
    
    // Hide circular menu and show hierarchical menu for replacement
    hideMenu();
    
    setTimeout(() => {
      showHierarchicalMenu(selectionRange, {
        x: rect.left + window.scrollX,
        y: rect.bottom + window.scrollY + 5
      });
      
      console.log('🔄 Switching to hierarchical menu for replacement');
    }, 100);
  }, [selectedAnnotation, showHierarchicalMenu, hideMenu]);
  
  const handleDelete = useCallback(() => {
    if (!selectedAnnotation) return;
    
    setRationaleDialog({
      isOpen: true,
      action: 'delete',
      annotation: selectedAnnotation,
      title: 'Delete Strategy Tag',
      message: `Remove the "${selectedAnnotation.tagType}" tag from this text?`,
      placeholder: 'Optional: Explain why this tag should be removed...',
      confirmText: 'Delete Tag',
      confirmStyle: 'danger'
    });
  }, [selectedAnnotation, setRationaleDialog]);
  
  const handleEditRange = useCallback(() => {
    if (!selectedAnnotation) return;
    
    // Enter selection mode to adjust tag boundaries
    setSelectionMode({
      active: true,
      mode: 'edit_range',
      originalAnnotation: selectedAnnotation,
      instructions: 'Drag to adjust the boundaries of this strategy tag'
    });
    
    hideMenu();
  }, [selectedAnnotation, setSelectionMode, hideMenu]);
  
  // Menu actions configuration with Portuguese labels for consistency
  const menuActions = [
    {
      id: 'validate',
      label: 'Validar',
      icon: Check,
      action: handleValidate,
      position: 'top',
      ariaLabel: `Validar tag ${selectedAnnotation?.tagType || ''}`,
      description: 'Confirmar que esta tag está corretamente aplicada'
    },
    {
      id: 'replace',
      label: 'Substituir',
      icon: Replace,
      action: handleReplace,
      position: 'right',
      ariaLabel: `Substituir tag ${selectedAnnotation?.tagType || ''}`,
      description: 'Alterar para uma tag de estratégia diferente'
    },
    {
      id: 'delete',
      label: 'Excluir',
      icon: Trash2,
      action: handleDelete,
      position: 'bottom',
      ariaLabel: `Excluir tag ${selectedAnnotation?.tagType || ''}`,
      description: 'Remover esta tag completamente'
    },
    {
      id: 'edit-range',
      label: 'Editar Alcance',
      icon: Edit,
      action: handleEditRange,
      position: 'left',
      ariaLabel: `Editar alcance da tag ${selectedAnnotation?.tagType || ''}`,
      description: 'Ajustar os limites de texto desta tag'
    }
  ];
  
  // Don't render if not visible or wrong menu type
  if (!isVisible || activeMenu !== 'circular' || !menuPosition) {
    return null;
  }
  
  const menuStyle = {
    position: 'fixed',
    top: `${menuPosition.top}px`,
    left: `${menuPosition.left}px`,
    zIndex: 1000,
    transform: 'translate(-50%, -50%)' // Center the circular menu
  };
  
  return (
    <>
      {/* Pointer corridor for hover stability */}
      {menuPosition.corridor && (
        <div
          ref={corridorRef}
          className="menu-pointer-corridor"
          style={{
            position: 'fixed',
            left: `${menuPosition.corridor.left}px`,
            top: `${menuPosition.corridor.top}px`,
            width: `${menuPosition.corridor.width}px`,
            height: `${menuPosition.corridor.height}px`,
            background: 'transparent',
            zIndex: 999,
            pointerEvents: 'auto'
          }}
        />
      )}
      
      {/* Circular menu */}
      <AccessibilityMenuWrapper
        menuType="circular"
        ariaLabel={`Context menu for ${selectedAnnotation?.tagType || ''} strategy tag`}
        className="circular-context-menu-wrapper"
      >
        <div
          ref={menuRef}
          className={`circular-context-menu ${isStable ? 'stable' : 'entering'}`}
          style={menuStyle}
          onMouseLeave={handleMouseLeave}
        >
          {/* Central indicator */}
          <div className="menu-center">
            <span className="menu-center-tag">
              {selectedAnnotation?.tagType || '?'}
            </span>
          </div>
          
          {/* Action buttons in circular layout */}
          {menuActions.map((action) => (
            <div
              key={action.id}
              className={`menu-action menu-action-${action.position}`}
              title={action.description}
            >
              <MenuButton
                onClick={action.action}
                ariaLabel={action.ariaLabel}
                ariaDescribedBy={`${action.id}-description`}
                icon={action.icon}
                className={`circular-menu-button ${action.position}`}
              >
                {action.label}
              </MenuButton>
              
              {/* Hidden description for screen readers */}
              <div
                id={`${action.id}-description`}
                className="sr-only"
              >
                {action.description}
              </div>
            </div>
          ))}
          
          {/* Visual connection lines */}
          <svg className="menu-connections" width="120" height="120">
            <circle
              cx="60"
              cy="60"
              r="45"
              fill="none"
              stroke="var(--menu-border-color, #e2e8f0)"
              strokeWidth="1"
              strokeDasharray="2,2"
              opacity="0.3"
            />
          </svg>
        </div>
      </AccessibilityMenuWrapper>
    </>
  );
}

export default CircularContextMenu;