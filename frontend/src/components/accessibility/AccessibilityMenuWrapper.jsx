/**
 * AccessibilityMenuWrapper.jsx - Phase 0: Dual Menu System Architecture
 * 
 * Shared accessibility wrapper for annotation menus with keyboard navigation,
 * ARIA attributes, and focus management for screen reader compatibility.
 * 
 * @created 2025-09-25
 * @phase Phase 0: Complete Interactive Foundation
 */

import React, { useEffect, useRef, useCallback } from 'react';
import { useAnnotationMenu } from '../../contexts/AnnotationMenuContext.jsx';

/**
 * AccessibilityMenuWrapper - Base wrapper component for all annotation menus
 * Provides keyboard navigation, focus management, and ARIA attributes
 */
export function AccessibilityMenuWrapper({
  children,
  menuType, // 'circular' | 'hierarchical'
  ariaLabel,
  onEscape,
  onEnterKey,
  className = '',
  role = 'menu',
  trapFocus = true
}) {
  const menuRef = useRef(null);
  const { hideMenu, activeMenu, isVisible } = useAnnotationMenu();
  
  // Focus trap implementation for accessibility
  const handleKeyDown = useCallback((event) => {
    switch (event.key) {
      case 'Escape':
        event.preventDefault();
        if (onEscape) {
          onEscape();
        } else {
          hideMenu();
        }
        break;
        
      case 'Tab':
        if (trapFocus && menuRef.current) {
          event.preventDefault();
          handleTabNavigation(event.shiftKey);
        }
        break;
        
      case 'Enter':
      case ' ':
        if (onEnterKey) {
          event.preventDefault();
          onEnterKey(event);
        }
        break;
        
      case 'ArrowUp':
      case 'ArrowDown':
      case 'ArrowLeft':
      case 'ArrowRight':
        if (menuType === 'circular') {
          event.preventDefault();
          handleCircularNavigation(event.key);
        } else if (menuType === 'hierarchical') {
          event.preventDefault();
          handleHierarchicalNavigation(event.key);
        }
        break;
    }
  }, [onEscape, onEnterKey, hideMenu, menuType, trapFocus]);
  
  // Tab navigation within menu
  const handleTabNavigation = useCallback((isShiftKey) => {
    if (!menuRef.current) return;
    
    const focusableElements = menuRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length === 0) return;
    
    const currentFocusIndex = Array.from(focusableElements).findIndex(
      el => el === document.activeElement
    );
    
    let nextIndex;
    if (isShiftKey) {
      nextIndex = currentFocusIndex <= 0 ? focusableElements.length - 1 : currentFocusIndex - 1;
    } else {
      nextIndex = currentFocusIndex >= focusableElements.length - 1 ? 0 : currentFocusIndex + 1;
    }
    
    focusableElements[nextIndex]?.focus();
  }, []);
  
  // Circular menu navigation (4-button layout)
  const handleCircularNavigation = useCallback((key) => {
    if (!menuRef.current) return;
    
    const buttons = menuRef.current.querySelectorAll('[role="menuitem"]');
    if (buttons.length !== 4) return;
    
    const currentIndex = Array.from(buttons).findIndex(
      btn => btn === document.activeElement
    );
    
    let nextIndex;
    switch (key) {
      case 'ArrowUp':
        nextIndex = (currentIndex - 1 + 4) % 4;
        break;
      case 'ArrowDown':
        nextIndex = (currentIndex + 1) % 4;
        break;
      case 'ArrowLeft':
        nextIndex = (currentIndex - 1 + 4) % 4;
        break;
      case 'ArrowRight':
        nextIndex = (currentIndex + 1) % 4;
        break;
      default:
        return;
    }
    
    buttons[nextIndex]?.focus();
  }, []);
  
  // Hierarchical menu navigation (category/strategy tree)
  const handleHierarchicalNavigation = useCallback((key) => {
    if (!menuRef.current) return;
    
    const focusableItems = menuRef.current.querySelectorAll(
      '[role="menuitem"], [role="menuitemradio"]'
    );
    
    const currentIndex = Array.from(focusableItems).findIndex(
      item => item === document.activeElement
    );
    
    let nextIndex;
    switch (key) {
      case 'ArrowUp':
        nextIndex = currentIndex > 0 ? currentIndex - 1 : focusableItems.length - 1;
        break;
      case 'ArrowDown':
        nextIndex = currentIndex < focusableItems.length - 1 ? currentIndex + 1 : 0;
        break;
      case 'ArrowRight':
        // Expand category or select strategy
        const currentItem = focusableItems[currentIndex];
        if (currentItem?.getAttribute('aria-expanded') === 'false') {
          currentItem.click();
        }
        return;
      case 'ArrowLeft':
        // Collapse category or go back to parent
        const currentCategory = document.activeElement.closest('[role="group"]');
        if (currentCategory) {
          const categoryButton = currentCategory.querySelector('[aria-expanded="true"]');
          if (categoryButton) {
            categoryButton.click();
            categoryButton.focus();
          }
        }
        return;
      default:
        return;
    }
    
    focusableItems[nextIndex]?.focus();
  }, []);
  
  // Focus management on mount/unmount
  useEffect(() => {
    if (isVisible && menuRef.current) {
      // Focus first actionable item when menu opens
      const firstFocusable = menuRef.current.querySelector(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      if (firstFocusable) {
        // Small delay to ensure menu is fully rendered
        setTimeout(() => {
          firstFocusable.focus();
        }, 10);
      }
      
      // Add global keyboard listener
      document.addEventListener('keydown', handleKeyDown);
      
      return () => {
        document.removeEventListener('keydown', handleKeyDown);
      };
    }
  }, [isVisible, handleKeyDown]);
  
  // Return focus to trigger element when menu closes
  useEffect(() => {
    if (!isVisible) {
      // Focus management handled by parent components
      // as they know the specific trigger element
    }
  }, [isVisible]);
  
  // Don't render if menu is not visible or not the active menu type
  if (!isVisible || activeMenu !== menuType) {
    return null;
  }
  
  const combinedClassName = `accessibility-menu-wrapper ${className}`;
  
  return (
    <div
      ref={menuRef}
      role={role}
      aria-label={ariaLabel}
      aria-expanded="true"
      className={combinedClassName}
      data-menu-type={menuType}
      onKeyDown={handleKeyDown}
    >
      {children}
    </div>
  );
}

/**
 * MenuButton - Accessible button component for menu items
 */
export function MenuButton({
  children,
  onClick,
  disabled = false,
  ariaLabel,
  ariaDescribedBy,
  icon: Icon,
  className = '',
  role = 'menuitem',
  ...props
}) {
  const handleClick = useCallback((event) => {
    if (disabled) return;
    
    event.preventDefault();
    event.stopPropagation();
    
    if (onClick) {
      onClick(event);
    }
  }, [onClick, disabled]);
  
  const handleKeyDown = useCallback((event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      handleClick(event);
    }
  }, [handleClick]);
  
  return (
    <button
      role={role}
      tabIndex={disabled ? -1 : 0}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      aria-disabled={disabled}
      className={`menu-button ${className} ${disabled ? 'disabled' : ''}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      {...props}
    >
      {Icon && <Icon className="menu-button-icon" aria-hidden="true" />}
      <span className="menu-button-text">{children}</span>
    </button>
  );
}

/**
 * MenuSeparator - Accessible separator for menu sections
 */
export function MenuSeparator({ className = '' }) {
  return (
    <div
      role="separator"
      aria-orientation="horizontal"
      className={`menu-separator ${className}`}
    />
  );
}

export default AccessibilityMenuWrapper;