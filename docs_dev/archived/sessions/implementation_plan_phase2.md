# Implementation Plan Phase 2 - Text Simplification Analysis Pipeline

**Status**: 🚧 In Progress  
**Priority**: High  
**Estimated Completion**: 6 weeks  
**Dependencies**: Phase 1 Foundation Layer

## Overview

This document outlines the implementation plan for enhancing the NET-EST text simplification analysis pipeline with visual analysis, human-in-the-loop interaction, and improved strategy detection.

### Objectives

1. **UI Simplification**: Remove unnecessary components and focus on core functionality
2. **Visual Strategy Analysis**: Implement color-coded side-by-side text display
3. **Interactive Tag Management**: Enable human corrections with special handling for OM+ and PRO+ tags
4. **Enhanced Detection**: Implement Steps 2-3 of the Hybrid Model approach

## Current System State

### ✅ Completed Components
- Step 1 of Hybrid Model (lightweight semantic model with MiniLM)
- Backend API with comparative analysis endpoints
- Basic frontend with dual text input functionality
- 14 simplification strategies defined and documented
- **✅ NEW: UI Cleanup completed - unnecessary components removed**
- **✅ NEW: Professional header and navigation implemented**

### 🚧 Components Requiring Enhancement
- Strategy detection backend (needs feature extractors and evidence-based classification)
- Visual representation system (needs color coding and highlighting)
- Human-in-the-loop interaction (needs tag management and feedback collection)

## Implementation Phases

### Phase 2A: UI Cleanup and Foundation (Week 1-2)

#### Priority 1: Component Removal and Simplification

**Target Files:**
- `frontend/src/App.jsx` - Main navigation cleanup
- `frontend/src/components/FileUploadTestPage.jsx` - Remove (deprecated)
- `frontend/src/components/SemanticAlignment.jsx` - Remove (outdated)

**Actions:**
1. Remove "File Upload Test" navigation tab and component
2. Remove "Semantic Alignment" navigation tab and component
3. Simplify navigation to focus on "Input" and "About" tabs only
4. Update application header for professional appearance

#### Priority 2: Strategy Detection Enhancement

**Target Files:**
- `backend/src/services/strategy_detector.py`
- `backend/src/models/strategy_models.py`

**Actions:**
1. Implement Step 2: Re-architect heuristics as feature extractors
2. Implement Step 3: Create evidence-based classifier
3. Add position tracking for strategy locations in text
4. Enhance confidence scoring for each detected strategy

### Phase 2B: Visual Analysis System (Week 3-4)

#### Priority 3: Color Coding System

**Strategy Color Mapping:**
```javascript
const STRATEGY_COLORS = {
  'AS+': '#FF6B6B',  // Red - Alteração de Sentido
  'DL+': '#4ECDC4',  // Teal - Reorganização Posicional
  'EXP+': '#45B7D1', // Blue - Explicitação e Detalhamento
  'IN+': '#96CEB4',  // Green - Manejo de Inserções
  'MOD+': '#FFEAA7', // Yellow - Reinterpretação Perspectiva
  'MT+': '#DDA0DD',  // Plum - Otimização de Títulos
  'OM+': '#F0F0F0',  // Light Gray - Supressão Seletiva (special)
  'PRO+': '#FFB347', // Orange - Desvio Semântico (manual only)
  'RF+': '#FF8A80',  // Light Red - Reescrita Global
  'RD+': '#80CBC4',  // Light Teal - Estruturação de Conteúdo
  'RP+': '#81C784',  // Light Green - Fragmentação Sintática
  'SL+': '#64B5F6',  // Light Blue - Adequação de Vocabulário
  'TA+': '#BA68C8',  // Purple - Clareza Referencial
  'MV+': '#FFD54F'   // Amber - Alteração da Voz Verbal
};
```

**New Components:**
- `frontend/src/components/SideBySideTextDisplay.jsx`
- `frontend/src/components/TextHighlighting.jsx`
- `frontend/src/services/strategyColorMapping.js`

#### Priority 4: Side-by-Side Layout

**Requirements:**
- Responsive design (side-by-side on desktop, stacked on mobile)
- Synchronized scrolling between source and target text panels
- Color highlighting for detected strategies on both texts
- Hover effects with strategy information tooltips

### Phase 2C: Interactive Tag Management (Week 5-6)

#### Priority 5: Tag System Implementation

**Special Tag Handling Rules:**
- **OM+ (Supressão Seletiva)**: Disabled by default, manual activation only
- **PRO+ (Desvio Semântico)**: Never auto-generated, manual selection only
- **All Other Tags**: Auto-generated with manual override capability

**New Components:**
- `frontend/src/components/StrategyTagSystem.jsx`
- `frontend/src/components/TagContextMenu.jsx`
- `frontend/src/hooks/useTextHighlighting.js`

#### Priority 6: Feedback Collection

**Backend Enhancements:**
- `backend/src/services/feedback_collection_service.py`
- `backend/src/models/feedback_models.py`
- `backend/src/api/feedback.py`

**Functionality:**
- Capture human corrections for machine learning improvement
- Track tag changes and reasoning
- Export feedback data for model training

## Technical Implementation Details

### Frontend Architecture Changes

```
frontend/src/
├── components/
│   ├── DualTextInputComponent.jsx (existing - update)
│   ├── SideBySideTextDisplay.jsx (new)
│   ├── TextHighlighting.jsx (new)
│   ├── StrategyTagSystem.jsx (new)
│   ├── TagContextMenu.jsx (new)
│   ├── ColorLegend.jsx (new)
│   └── ComparativeResultsDisplay.jsx (update)
├── services/
│   ├── strategyColorMapping.js (new)
│   └── feedbackService.js (new)
├── hooks/
│   └── useTextHighlighting.js (new)
└── utils/
    └── textSegmentation.js (new)
```

### Backend Architecture Changes

```
backend/src/
├── services/
│   ├── strategy_detector.py (update - hybrid model steps 2-3)
│   ├── feature_extraction_service.py (update)
│   └── feedback_collection_service.py (new)
├── models/
│   ├── strategy_models.py (update - position tracking)
│   └── feedback_models.py (new)
└── api/
    └── feedback.py (new)
```

## Quality Assurance Requirements

### Testing Strategy
- **Unit Tests**: Strategy detection accuracy validation
- **Integration Tests**: Frontend-backend communication
- **User Acceptance Tests**: Tag management workflows
- **Accessibility Tests**: Color coding compliance (WCAG 2.1 AA)
- **Performance Tests**: Large text handling and responsiveness

### Success Metrics
- Strategy detection accuracy > 85%
- UI interaction responsiveness < 100ms
- Color accessibility compliance achieved
- User task completion rate > 90%

## Risk Assessment

### High Risk
- **Color Accessibility**: Ensuring colorblind-friendly design
- **Performance**: Maintaining responsiveness with large texts
- **Tag Guidelines Compliance**: Proper OM+ and PRO+ handling

### Medium Risk
- **User Experience**: Intuitive tag management interface
- **Data Accuracy**: Feedback collection reliability

### Mitigation Strategies
- Early accessibility testing with colorblind simulation tools
- Performance testing with progressively larger text samples
- Clear documentation and user guidance for tag management rules

## Dependencies and Prerequisites

### External Dependencies
- Sentence-transformers (MiniLM model)
- React Query for async state management
- Zustand for global state management

### Internal Dependencies
- Completion of Phase 1 Foundation Layer
- Backend API endpoints operational
- Strategy definitions from `docs/Tabela Simplificação Textual.md`

## Deliverables Timeline

### Week 1-2 Deliverables
- ✅ UI cleanup completed
- ✅ Enhanced strategy detection backend
- ✅ Color coding system implemented

### Week 3-4 Deliverables
- ✅ Side-by-side text display functional
- ✅ Text highlighting system operational
- ✅ Color legend and accessibility features

### Week 5-6 Deliverables
- ✅ Tag management system with context menus
- ✅ OM+ and PRO+ special handling implemented
- ✅ Feedback collection system operational

## References and Documentation

- [Simplification Strategies Table](../docs/Tabela%20Simplificação%20Textual.md)
- [Hybrid Model Approach](./hybrid_model_approach.md)
- [Foundation Layer Status](../docs/STATUS_FOUNDATION_LAYER.md)
- [Project Architecture](../ARCHITECTURE.md)

---

**Next Steps**: Begin with Phase 2A component removal and UI simplification, followed by strategy detection enhancement implementation.

/*
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
*/
