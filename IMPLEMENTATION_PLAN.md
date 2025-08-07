# NET-EST Implementation Plan - Text Simplification Analysis Pipeline

This document outlines the comprehensive implementation plan for the NET-EST text simplification analysis pipeline, focusing on visual analysis, human-in-the-loop interaction, and strategy detection improvements.

## Project Context

**Goal**: Create a streamlined pipeline for analyzing intralingual translation texts to identify simplification strategies, display them visually with color coding, and enable human-in-the-loop corrections.

**Current Status**:

- ✅ Step 1 of Hybrid Model completed (lightweight semantic model)
- ✅ Backend API functional with comparative analysis
- ✅ Basic frontend with dual text input working
- 🚧 Frontend needs simplification and enhanced visualization

## Implementation Phases

### **Phase 1: Cleanup and Foundation** ✅

#### **Step 1.1: Remove Unnecessary Components**

- **Objective**: Simplify UI by removing outdated/unnecessary features
- **Actions**:
  - ✅ Remove "File Upload Test" button and component
  - ✅ Remove "Semantic Alignment" button and component (outdated)
  - ✅ Keep only "Input" and "About" tabs
  - ✅ Simplify navigation header
- **Files to Modify**:
  - `frontend/src/App.jsx`
  - Remove: `frontend/src/components/FileUploadTestPage.jsx`
  - Remove: `frontend/src/components/SemanticAlignment.jsx`

#### **Step 1.2: Update Application Header**

- **Objective**: Professional, focused application branding
- **Actions**:
  - ✅ Update title to focus on main goal
  - ✅ Remove phase references and technical jargon
  - ✅ Clean, professional appearance
- **Files to Modify**: `frontend/src/App.jsx`

### **Phase 2: Enhanced Analysis Pipeline** 🚧

#### **Step 2.1: Improve Strategy Detection Backend**
- **Objective**: Implement Steps 2-3 of Hybrid Model approach
- **Actions**:
  - ✅ Implement Step 2: Re-architect heuristics as feature extractors
  - ✅ Implement Step 3: Create evidence-based classifier
  - ✅ Enhance confidence scoring for each strategy
  - ✅ Add position tracking for strategy locations in text
- **Files to Modify**: 
  - `backend/src/services/strategy_detector.py`
  - `backend/src/models/strategy_models.py`

#### **Step 2.2: Create Color-Coding System**
- **Objective**: Visual strategy identification system
- **Actions**:
  - ✅ Define 14 distinct colors for the 14 simplification strategies
  - ✅ Create color mapping configuration
  - ✅ Ensure accessibility (colorblind-friendly options)
  - ✅ Create color legend component
- **Strategy Color Mapping**:
  ```javascript
  {
    'AS+': '#FF6B6B', // Red - Alteração de Sentido
    'DL+': '#4ECDC4', // Teal - Reorganização Posicional
    'EXP+': '#45B7D1', // Blue - Explicitação e Detalhamento
    'IN+': '#96CEB4', // Green - Manejo de Inserções
    'MOD+': '#FFEAA7', // Yellow - Reinterpretação Perspectiva
    'MT+': '#DDA0DD', // Plum - Otimização de Títulos
    'OM+': '#F0F0F0', // Light Gray - Supressão Seletiva (special)
    'PRO+': '#FFB347', // Orange - Desvio Semântico (manual only)
    'RF+': '#FF8A80', // Light Red - Reescrita Global
    'RD+': '#80CBC4', // Light Teal - Estruturação de Conteúdo
    'RP+': '#81C784', // Light Green - Fragmentação Sintática
    'SL+': '#64B5F6', // Light Blue - Adequação de Vocabulário
    'TA+': '#BA68C8', // Purple - Clareza Referencial
    'MV+': '#FFD54F'  // Amber - Alteração da Voz Verbal
  }
  ```

### **Phase 3: Side-by-Side Text Display** ✅

#### **Step 3.1: Create Side-by-Side Layout Component**
- **Objective**: Responsive comparative text display
- **Actions**:
  - ✅ Responsive design (side-by-side on desktop, stacked on mobile)
  - ✅ Source text panel with color highlighting
  - ✅ Target text panel with color highlighting + tags
  - ✅ Synchronized scrolling between panels
  - ✅ Integrated into ComparativeResultsDisplay as "Análise Visual" tab
- **Component**: `frontend/src/components/SideBySideTextDisplay.jsx`

#### **Step 3.2: Implement Text Highlighting System**
- **Objective**: Visual strategy mapping on text
- **Actions**:
  - ✅ Text segmentation and mapping
  - ✅ Color application based on strategy detection
  - ✅ Hover effects for strategy information
  - ✅ Strategy tooltip on hover
  - ✅ Interactive color legend with strategy selection
  - ✅ Accessibility improvements (button elements for interactions)
- **Technical Requirements**:
  - ✅ Segment text by character/word positions
  - ✅ Apply CSS classes for color highlighting
  - ✅ Handle overlapping strategies
  - ✅ Maintain text readability

#### **Step 3.3: Implement Tag System for Target Text**
- **Objective**: Superscript strategy tags on target text
- **Actions**:
  - ✅ Superscript tag display (AS+, SL+, RF+, etc.)
  - ✅ Clickable tags with strategy selection
  - ✅ Visual feedback for selected strategies
  - ✅ Strategy information panel with statistics
  - ✅ Special handling for OM+ and PRO+ tags per guidelines
- **Special Tag Rules**:
  - ✅ **OM+**: Marked as special with warning icon
  - ✅ **PRO+**: Marked as special with warning icon
  - ✅ Special strategies highlighted in color legend

### **Phase 4: Human-in-the-Loop Interaction** 🚧

#### **Step 4.1: Context Menu System**
- **Objective**: Interactive tag management
- **Actions**:
  - ✅ Right-click context menu on target text tags
  - ✅ Strategy selection dropdown
  - ✅ Tag removal option
  - ✅ Visual feedback for changes
- **Component**: `frontend/src/components/TagContextMenu.jsx`

#### **Step 4.2: Tag Management Following Guidelines**
- **Objective**: Compliance with simplification strategy guidelines
- **Actions**:
  - ✅ **OM+**: Disabled by default, available in context menu for manual activation
  - ✅ **PRO+**: Never auto-generated, only available for manual selection
  - ✅ All other tags: Auto-generated with manual override capability
- **Reference**: `docs/Tabela Simplificação Textual.md`

#### **Step 4.3: Feedback Collection System**
- **Objective**: Capture human corrections for ML improvement
- **Actions**:
  - ✅ Store human corrections for ML training
  - ✅ Track tag changes and reasoning
  - ✅ Export feedback data for model improvement
- **Backend Endpoint**: `POST /api/v1/feedback`

## Implementation Priority Schedule

### **Week 1-2: Immediate Priority**
1. **UI Cleanup** - Remove unnecessary buttons and components
2. **Implement Step 2 of Hybrid Model** - Feature extractors instead of decision makers
3. **Create color coding system** - 14 colors for strategies
4. **Build side-by-side layout** - Responsive text comparison view

### **Week 3-4: High Priority**
5. **Text highlighting system** - Color mapping on both texts
6. **Tag display system** - Superscript tags on target text
7. **Context menu functionality** - Tag editing capabilities
8. **OM+ and PRO+ special handling** - Following guidelines

### **Week 5-6: Medium Priority**
9. **Enhanced confidence scoring** - Better strategy detection accuracy
10. **Feedback collection system** - Store human corrections
11. **Accessibility improvements** - Colorblind support, keyboard navigation
12. **Performance optimization** - Fast rendering of large texts

## Technical Architecture

### **Frontend Structure**
```
frontend/src/
├── components/
│   ├── DualTextInputComponent.jsx (existing)
│   ├── SideBySideTextDisplay.jsx (new)
│   ├── TextHighlighting.jsx (new)
│   ├── StrategyTagSystem.jsx (new)
│   ├── TagContextMenu.jsx (new)
│   ├── ColorLegend.jsx (new)
│   └── ComparativeResultsDisplay.jsx (update)
├── services/
│   ├── strategyColorMapping.js (new)
│   └── feedbackService.js (new)
└── hooks/
    └── useTextHighlighting.js (new)
```

### **Backend Enhancements**
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

## Quality Assurance

### **Testing Requirements**
- Unit tests for strategy detection accuracy
- Integration tests for frontend-backend communication
- User acceptance testing for tag management
- Accessibility testing for color coding system
- Performance testing with large texts

### **Success Metrics**
- Strategy detection accuracy > 85%
- UI responsiveness < 100ms for tag interactions
- Color accessibility compliance (WCAG 2.1 AA)
- User task completion rate > 90%

## References

- [Hybrid Model Approach](./docs_dev/hybrid_model_approch.md)
- [Simplification Strategies Table](./docs/Tabela%20Simplificação%20Textual.md)
- [Architecture Documentation](./ARCHITECTURE.md)
- [Development Guidelines](./DEVELOPMENT.md)

/*
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
*/
Get-ChildItem -Path . -Recurse -Directory -Name '__pycache__' | ForEach-Object { Remove-Item -Path $_ -Recurse -Force }Get-ChildItem -Path . -Recurse -Directory -Name '__pycache__' | ForEach-Object { Remove-Item -Path $_ -Recurse -Force }Get-ChildItem -Path . -Recurse -Directory -Name '__pycache__' | ForEach-Object { Remove-Item -Path $_ -Recurse -Force }Get-ChildItem -Path . -Recurse -Directory -Name '__pycache__' | ForEach-Object { Remove-Item -Path $_ -Recurse -Force }Get-ChildItem -Path . -Recurse -Directory -Name '__pycache__' | ForEach-Object { Remove-Item -Path $_ -Recurse -Force }