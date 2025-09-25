/**
 * HierarchicalStrategyMenu.jsx - Phase 0: Dual Menu System Architecture
 * 
 * Hierarchical strategy selection menu organized by 6 categories with all sub-strategies.
 * Provides accessible navigation through strategy categories and individual strategy selection.
 * 
 * @created 2025-09-25
 * @phase Phase 0: Complete Interactive Foundation
 */

import React, { useState, useCallback, useEffect } from 'react';
import { ChevronRight, ChevronDown, Search, Tag } from 'lucide-react';
import { useAnnotationMenu } from '../../contexts/AnnotationMenuContext.jsx';
import { calculateHierarchicalMenuPosition } from '../../utils/menuPositionCalculator.js';
import { AccessibilityMenuWrapper, MenuButton, MenuSeparator } from '../accessibility/AccessibilityMenuWrapper.jsx';
import { getStrategyColor } from '../../services/strategyColorMapping.js';
import './HierarchicalStrategyMenu.css';

/**
 * Strategy categories with Portuguese labels and metadata - CANONICAL VERSION
 * Based on strategies_menu_tree.md specifications (user's selected structure)
 */
const STRATEGY_CATEGORIES = {
  lexical: {
    label: 'Léxico',
    description: 'Estratégias de adequação vocabular',
    icon: '📖'
  },
  syntactic: {
    label: 'Sintaxe', 
    description: 'Estratégias de estrutura sintática',
    icon: '🔗'
  },
  semantic: {
    label: 'Semântica',
    description: 'Estratégias de sentido e significado',
    icon: '💭'
  },
  content: {
    label: 'Conteúdo',
    description: 'Estratégias de gestão de informação',
    icon: '📋'
  },
  discourse: {
    label: 'Discurso',
    description: 'Estratégias de organização discursiva',
    icon: '🗣️'
  },
  exceptions: {
    label: 'Exceções (Somente Humanos)',
    description: 'Estratégias especiais e casos manuais',
    icon: '⚠️'
  }
};

/**
 * CANONICAL strategy organization based on strategies_menu_tree.md specifications
 * This matches exactly the tree structure provided by the user in the selected text
 */
function getStrategiesByCategory() {
  return {
    lexical: [
      { code: 'SL+', label: 'Adequação de Vocabulário', description: 'Substituição de termos menos frequentes por outros mais acessíveis' }
    ],
    syntactic: [
      { code: 'RP+', label: 'Fragmentação Sintática', description: 'Split/merge de sentenças; resegmentação' },
      { code: 'MV+', label: 'Alteração da Voz Verbal', description: 'Mudança entre voz ativa e passiva' }
    ],
    semantic: [
      { code: 'AS+', label: 'Alteração de Sentido', description: 'Modificação semântica do conteúdo' },
      { code: 'MOD+', label: 'Reinterpretação Perspectiva', description: 'Mudança de força/ênfase/ponto de vista' },
      { code: 'RF+', label: 'Reescrita Global', description: 'Reescrita macro que preserva ideia; pode agregar operações micro' },
      { code: 'TA+', label: 'Clareza Referencial', description: 'Melhoria na clareza de referências textuais' }
    ],
    content: [
      { code: 'EXP+', label: 'Explicitação e Detalhamento', description: 'Inserção de glossas, parênteses explicativos ou paráfrases' },
      { code: 'IN+', label: 'Inserção', description: 'Adição de material novo — exemplos, justificativas, conectores ideacionais' }
    ],
    discourse: [
      { code: 'RD+', label: 'Reorganização Discursiva', description: 'Mudança na lógica/ordem das ideias; troca/adição de conectores; reordenação de parágrafos' },
      { code: 'MT+', label: 'Mudança de Título', description: 'Alteração de cabeçalhos refletindo reestruturação de conteúdo' }
    ],
    exceptions: [
      { code: 'OM+', label: 'Omissão Seletiva', description: 'Supressão de segmentos significativos do texto original (apenas anotação humana)' },
      { code: 'PRO+', label: 'Desvio Semântico', description: 'Problema ou erro semântico identificado (apenas humana)' }
    ]
  };
}

/**
 * HierarchicalStrategyMenu - Category-organized strategy selection menu
 */
export function HierarchicalStrategyMenu() {
  const [expandedCategories, setExpandedCategories] = useState(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [menuPosition, setMenuPosition] = useState(null);

  const {
    isVisible,
    activeMenu,
    selectionRange,
    hideMenu,
    // Stub functions for now
    setSelectedStrategy: setContextStrategy = () => console.log('Context strategy selection not implemented'),
    confirmStrategySelection = () => console.log('Strategy confirmation not implemented')
  } = useAnnotationMenu();

  const strategiesByCategory = getStrategiesByCategory();

  // Calculate menu position based on selection or target element
  useEffect(() => {
    if (isVisible && activeMenu === 'hierarchical' && selectionRange) {
      const coords = calculateHierarchicalMenuPosition(selectionRange, {
        width: 320,
        height: 450
      });

      setMenuPosition({
        top: coords.y,
        left: coords.x,
        width: coords.adjustedWidth || 320,
        height: coords.adjustedHeight || 450,
        fitsOriginalSize: coords.fitsOriginalSize
      });
    } else {
      setMenuPosition(null);
    }
  }, [isVisible, activeMenu, selectionRange]);

  // Toggle category expansion
  const toggleCategory = useCallback((categoryKey) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(categoryKey)) {
        newSet.delete(categoryKey);
      } else {
        newSet.add(categoryKey);
      }
      return newSet;
    });
  }, []);

  // Handle strategy selection
  const handleStrategySelect = useCallback((strategyCode) => {
    setSelectedStrategy(strategyCode);
    setContextStrategy(strategyCode);
    
    console.log('🏷️ Strategy selected:', strategyCode);
  }, [setContextStrategy]);

  // Confirm strategy application
  const handleConfirmStrategy = useCallback(() => {
    if (selectedStrategy && selectionRange) {
      console.log('✅ Strategy confirmed:', {
        strategy: selectedStrategy,
        text: selectionRange.text,
        position: { x: selectionRange.x, y: selectionRange.y }
      });
      
      // TODO: Integrate with backend API to create new strategy annotation
      // For now, show user feedback and close menu
      console.info(`🎯 Applied strategy ${selectedStrategy} to selected text. Backend integration pending.`);
      
      // Call the context confirmation (even if it's a stub)
      confirmStrategySelection(selectedStrategy);
      
      // Close the menu
      hideMenu();
      
      // Clear the browser selection to provide visual feedback
      setTimeout(() => {
        const selection = window.getSelection();
        if (selection) {
          selection.removeAllRanges();
        }
      }, 100);
    } else {
      console.warn('Cannot confirm strategy: missing strategy or selection range');
    }
  }, [selectedStrategy, selectionRange, confirmStrategySelection, hideMenu]);

  // Filter strategies by search term
  const filterStrategies = useCallback((strategies) => {
    if (!searchTerm.trim()) return strategies;
    
    const term = searchTerm.toLowerCase();
    return strategies.filter(strategy => 
      strategy.code.toLowerCase().includes(term) ||
      strategy.label.toLowerCase().includes(term) ||
      strategy.description.toLowerCase().includes(term)
    );
  }, [searchTerm]);

  // Render strategy item
  const renderStrategyItem = useCallback((strategy) => {
    const isSelected = selectedStrategy === strategy.code;
    const color = getStrategyColor(strategy.code);
    
    return (
      <MenuButton
        key={strategy.code}
        onClick={() => handleStrategySelect(strategy.code)}
        className={`strategy-item ${isSelected ? 'selected' : ''}`}
        role="menuitemradio"
        ariaLabel={`${strategy.code} - ${strategy.label}`}
        ariaDescribedBy={`${strategy.code}-desc`}
        aria-checked={isSelected}
      >
        <div className="strategy-header">
          <div 
            className="strategy-color-indicator"
            style={{ backgroundColor: color }}
            aria-hidden="true"
          />
          <div className="strategy-info">
            <span className="strategy-full-label">
              <span className="strategy-code">{strategy.code}</span>
              <span className="strategy-separator"> </span>
              <span className="strategy-name">{strategy.label}</span>
            </span>
          </div>
          {isSelected && <Tag className="selection-indicator" size={16} />}
        </div>
        <div 
          id={`${strategy.code}-desc`}
          className="strategy-description sr-only"
        >
          {strategy.description}
        </div>
      </MenuButton>
    );
  }, [selectedStrategy, handleStrategySelect]);

  // Don't render if not visible or wrong menu type
  if (!isVisible || activeMenu !== 'hierarchical' || !menuPosition) {
    return null;
  }

  const menuStyle = {
    position: 'fixed',
    top: `${menuPosition.top}px`,
    left: `${menuPosition.left}px`,
    width: `${menuPosition.width}px`,
    height: `${menuPosition.height}px`,
    zIndex: 1000
  };

  return (
    <AccessibilityMenuWrapper
      menuType="hierarchical"
      ariaLabel="Menu hierárquico de seleção de estratégias"
      className="hierarchical-strategy-menu-wrapper"
    >
      <div
        className="hierarchical-strategy-menu"
        style={menuStyle}
      >
        {/* Menu Header */}
        <div className="menu-header">
          <h3 className="menu-title">Selecionar Estratégia</h3>
          
          {/* Selected Text Preview */}
          {selectionRange?.text && (
            <div className="selected-text-preview">
              <span className="preview-label">Texto selecionado:</span>
              <span className="preview-text">
                "{selectionRange.text.length > 80 
                  ? selectionRange.text.substring(0, 80) + '...' 
                  : selectionRange.text}"
              </span>
            </div>
          )}
          
          {/* Search Input */}
          <div className="search-container">
            <Search className="search-icon" size={16} />
            <input
              type="text"
              placeholder="Buscar estratégia..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
              aria-label="Buscar estratégias por código, nome ou descrição"
            />
          </div>
        </div>

        {/* Strategy Categories */}
        <div className="menu-content">
          {Object.entries(STRATEGY_CATEGORIES).map(([categoryKey, category]) => {
            const strategies = filterStrategies(strategiesByCategory[categoryKey] || []);
            const isExpanded = expandedCategories.has(categoryKey);
            const hasVisibleStrategies = strategies.length > 0;

            if (!hasVisibleStrategies && searchTerm.trim()) {
              return null; // Hide empty categories when searching
            }

            return (
              <div key={categoryKey} className="strategy-category">
                <MenuButton
                  onClick={() => toggleCategory(categoryKey)}
                  className="category-header"
                  role="menuitem"
                  ariaLabel={`${category.label} - ${category.description}`}
                  aria-expanded={isExpanded}
                  aria-controls={`category-${categoryKey}`}
                >
                  <span className="category-icon" aria-hidden="true">
                    {category.icon}
                  </span>
                  <span className="category-label">{category.label}</span>
                  <span className="strategy-count">({strategies.length})</span>
                  {isExpanded ? (
                    <ChevronDown className="expand-icon" size={16} />
                  ) : (
                    <ChevronRight className="expand-icon" size={16} />
                  )}
                </MenuButton>

                {isExpanded && (
                  <div
                    id={`category-${categoryKey}`}
                    className="category-strategies"
                    role="group"
                    aria-labelledby={`category-${categoryKey}-label`}
                  >
                    {strategies.map(renderStrategyItem)}
                    
                    {strategies.length === 0 && (
                      <div className="no-strategies">
                        Nenhuma estratégia encontrada
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Action Buttons */}
        <div className="menu-actions">
          <MenuSeparator />
          
          <div className="action-buttons">
            <MenuButton
              onClick={hideMenu}
              className="action-button secondary"
            >
              Cancelar
            </MenuButton>
            
            <MenuButton
              onClick={handleConfirmStrategy}
              className="action-button primary"
              disabled={!selectedStrategy}
              ariaLabel={selectedStrategy ? 
                `Aplicar estratégia ${selectedStrategy}` : 
                'Selecione uma estratégia para confirmar'
              }
            >
              {selectedStrategy ? `Aplicar ${selectedStrategy}` : 'Selecionar'}
            </MenuButton>
          </div>
        </div>
      </div>
    </AccessibilityMenuWrapper>
  );
}

export default HierarchicalStrategyMenu;