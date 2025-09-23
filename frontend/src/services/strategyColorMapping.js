/**
 * Strategy Color Mapping Configuration for NET-EST
 * Maps each of the 14 simplification strategies to a distinct, accessible color
 */

// Strategy color mapping with accessibility considerations (WCAG AA compliant)
export const STRATEGY_COLORS = {
  'AS+': '#DC2626',  // Red-600 - Alteração de Sentido
  'DL+': '#059669',  // Emerald-600 - Reorganização Posicional  
  'EXP+': '#2563EB', // Blue-600 - Explicitação e Detalhamento
  'IN+': '#16A34A',  // Green-600 - Manejo de Inserções
  'MOD+': '#EA580C', // Orange-600 - Reinterpretação Perspectiva
  'MT+': '#9333EA',  // Violet-600 - Otimização de Títulos
  'OM+': '#6B7280',  // Gray-500 - Supressão Seletiva (special handling)
  'PRO+': '#C2410C', // Orange-700 - Desvio Semântico (manual only)
  'RF+': '#BE123C',  // Rose-700 - Reescrita Global
  'RD+': '#0D9488',  // Teal-600 - Estruturação de Conteúdo
  'RP+': '#65A30D',  // Lime-600 - Fragmentação Sintática
  'SL+': '#0284C7',  // Sky-600 - Adequação de Vocabulário
  'TA+': '#7C3AED',  // Violet-700 - Clareza Referencial
  'MV+': '#D97706'   // Amber-600 - Alteração da Voz Verbal
};

// Enhanced colorblind-friendly palette (protanopia/deuteranopia safe)
export const STRATEGY_COLORS_COLORBLIND = {
  'AS+': '#E69F00',  // Orange (distinct from blues/teals)
  'DL+': '#56B4E9',  // Sky Blue (distinct from oranges)
  'EXP+': '#009E73', // Bluish Green (distinct from reds)
  'IN+': '#F0E442',  // Yellow (high contrast)
  'MOD+': '#0072B2', // Blue (distinct from yellows)
  'MT+': '#D55E00',  // Vermillion (distinct from blues)
  'OM+': '#999999',  // Medium Gray (neutral)
  'PRO+': '#CC79A7', // Reddish Purple (distinct category)
  'RF+': '#E31A1C',  // Red (high contrast)
  'RD+': '#1F78B4',  // Blue (distinct from reds)
  'RP+': '#33A02C',  // Green (distinct from purples)
  'SL+': '#A6CEE3',  // Light Blue (accessible contrast)
  'TA+': '#B15928',  // Brown (distinct from blues/greens)
  'MV+': '#FFFF99'   // Light Yellow (high contrast background)
};

// Strategy metadata for display
export const STRATEGY_METADATA = {
  'AS+': {
    name: 'Alteração de Sentido',
    description: 'Mudança no sentido ou perspectiva do texto',
    type: 'semantic',
    autoDetect: true
  },
  'DL+': {
    name: 'Reorganização Posicional',
    description: 'Mudança na ordem ou posição dos elementos',
    type: 'structural',
    autoDetect: true
  },
  'EXP+': {
    name: 'Explicitação e Detalhamento',
    description: 'Adição de informações para maior clareza',
    type: 'content',
    autoDetect: true
  },
  'IN+': {
    name: 'Manejo de Inserções',
    description: 'Tratamento de conteúdo inserido ou parentético',
    type: 'structural',
    autoDetect: true
  },
  'MOD+': {
    name: 'Reinterpretação Perspectiva',
    description: 'Mudança de perspectiva mantendo o sentido',
    type: 'semantic',
    autoDetect: true
  },
  'MT+': {
    name: 'Otimização de Títulos',
    description: 'Melhoria na estrutura de títulos e subtítulos',
    type: 'structural',
    autoDetect: true
  },
  'OM+': {
    name: 'Supressão Seletiva',
    description: 'Remoção seletiva de conteúdo secundário',
    type: 'content',
    autoDetect: false, // Disabled by default per guidelines
    specialHandling: 'manual-activation'
  },
  'PRO+': {
    name: 'Desvio Semântico',
    description: 'Alteração significativa do sentido original',
    type: 'semantic',
    autoDetect: false, // Never auto-generated per guidelines
    specialHandling: 'manual-only'
  },
  'RF+': {
    name: 'Reescrita Global',
    description: 'Reescrita completa mantendo o sentido',
    type: 'semantic',
    autoDetect: true
  },
  'RD+': {
    name: 'Estruturação de Conteúdo',
    description: 'Reorganização da estrutura do conteúdo',
    type: 'structural',
    autoDetect: true
  },
  'RP+': {
    name: 'Fragmentação Sintática',
    description: 'Divisão de frases ou períodos complexos',
    type: 'syntactic',
    autoDetect: true
  },
  'SL+': {
    name: 'Adequação de Vocabulário',
    description: 'Substituição por vocabulário mais simples',
    type: 'lexical',
    autoDetect: true
  },
  'TA+': {
    name: 'Clareza Referencial',
    description: 'Substituição de pronomes por referências claras',
    type: 'semantic',
    autoDetect: true
  },
  'MV+': {
    name: 'Alteração da Voz Verbal',
    description: 'Mudança entre voz ativa e passiva',
    type: 'syntactic',
    autoDetect: true
  }
};

// Enhanced utility functions for accessibility and color management
export const getStrategyColor = (strategyCode, useColorblindFriendly = false) => {
  const colorMap = useColorblindFriendly ? STRATEGY_COLORS_COLORBLIND : STRATEGY_COLORS;
  return colorMap[strategyCode] || '#6B7280'; // Default gray-500 for unknown strategies
};

export const getAccessibleTextColor = (backgroundColor) => {
  const rgb = hexToRgb(backgroundColor);
  if (!rgb) return '#000000';
  
  // WCAG AA compliant contrast calculation
  const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
  
  // Return high contrast colors
  return luminance > 0.5 ? '#111827' : '#F9FAFB'; // gray-900 or gray-50
};

export const getStrategyPattern = (strategyCode, useColorblindFriendly = false) => {
  if (!useColorblindFriendly) return null;
  
  // CSS patterns for enhanced accessibility in colorblind mode
  const patterns = {
    'AS+': 'repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(255,255,255,0.3) 2px, rgba(255,255,255,0.3) 4px)',
    'DL+': 'repeating-linear-gradient(-45deg, transparent, transparent 2px, rgba(255,255,255,0.3) 2px, rgba(255,255,255,0.3) 4px)',
    'EXP+': 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.3) 1px, transparent 1px)',
    'IN+': 'linear-gradient(90deg, rgba(255,255,255,0.3) 50%, transparent 50%)',
    'MOD+': 'linear-gradient(0deg, rgba(255,255,255,0.3) 50%, transparent 50%)',
    'MT+': 'repeating-linear-gradient(90deg, transparent, transparent 3px, rgba(255,255,255,0.3) 3px, rgba(255,255,255,0.3) 6px)',
    'PRO+': 'repeating-conic-gradient(from 0deg, transparent 0deg, transparent 30deg, rgba(255,255,255,0.3) 30deg, rgba(255,255,255,0.3) 60deg)',
    'RF+': 'repeating-linear-gradient(135deg, transparent, transparent 1px, rgba(255,255,255,0.3) 1px, rgba(255,255,255,0.3) 3px)',
    'RD+': 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.3) 2px, rgba(255,255,255,0.3) 4px)',
    'RP+': 'repeating-linear-gradient(45deg, transparent, transparent 1px, rgba(255,255,255,0.3) 1px, rgba(255,255,255,0.3) 2px)',
    'SL+': 'linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.3) 40%, rgba(255,255,255,0.3) 60%, transparent 60%)',
    'TA+': 'repeating-radial-gradient(circle at 3px 3px, rgba(255,255,255,0.3) 1px, transparent 1px, transparent 4px)',
    'MV+': 'repeating-linear-gradient(-90deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px)' // Darker pattern for light yellow
  };
  
  return patterns[strategyCode] || null;
};

export const getStrategyInfo = (strategyCode) => {
  return STRATEGY_METADATA[strategyCode] || {
    name: 'Estratégia Desconhecida',
    description: 'Estratégia não identificada',
    type: 'unknown',
    autoDetect: false
  };
};

export const getAllStrategyColors = (useColorblindFriendly = false) => {
  return useColorblindFriendly ? STRATEGY_COLORS_COLORBLIND : STRATEGY_COLORS;
};

export const isHighContrastColor = (color) => {
  const rgb = hexToRgb(color);
  if (!rgb) return false;
  
  const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
  return luminance < 0.3 || luminance > 0.7; // High contrast if very dark or very light
};

// Utility functions for color management
export const getStrategyColor_OLD = (strategyCode, useColorblindFriendly = false) => {
  const colorMap = useColorblindFriendly ? STRATEGY_COLORS_COLORBLIND : STRATEGY_COLORS;
  return colorMap[strategyCode] || '#CCCCCC'; // Default gray for unknown strategies
};

export const getStrategyInfo_OLD = (strategyCode) => {
  return STRATEGY_METADATA[strategyCode] || {
    name: 'Estratégia Desconhecida',
    description: 'Estratégia não identificada',
    type: 'unknown',
    autoDetect: false
  };
};

export const getAllStrategyColors_OLD = (useColorblindFriendly = false) => {
  return useColorblindFriendly ? STRATEGY_COLORS_COLORBLIND : STRATEGY_COLORS;
};

export const getAutoDetectableStrategies = () => {
  return Object.keys(STRATEGY_METADATA).filter(
    code => STRATEGY_METADATA[code].autoDetect
  );
};

export const getManualOnlyStrategies = () => {
  return Object.keys(STRATEGY_METADATA).filter(
    code => !STRATEGY_METADATA[code].autoDetect
  );
};

// CSS class generator for strategy highlighting
export const getStrategyClassName = (strategyCode) => {
  return `strategy-highlight-${strategyCode.toLowerCase().replace('+', '-plus')}`;
};

// Generate CSS for strategy highlighting with enhanced accessibility
export const generateStrategyCSSClasses = (useColorblindFriendly = false) => {
  const colorMap = useColorblindFriendly ? STRATEGY_COLORS_COLORBLIND : STRATEGY_COLORS;
  
  return Object.entries(colorMap).map(([strategyCode, color]) => {
    const className = getStrategyClassName(strategyCode);
    const textColor = getAccessibleTextColor(color);
    const pattern = getStrategyPattern(strategyCode, useColorblindFriendly);
    const borderColor = darkenColor(color, 15);
    
    return `
.${className} {
  background-color: ${color};
  color: ${textColor};
  border: 2px solid ${borderColor};
  ${pattern ? `background-image: ${pattern};` : ''}
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 600;
  line-height: 1.2;
  display: inline-block;
  margin: 0 1px;
  position: relative;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
}

.${className}:hover {
  background-color: ${darkenColor(color, 8)};
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transform: translateY(-1px);
  cursor: pointer;
}

.${className}:focus {
  outline: 2px solid #2563EB;
  outline-offset: 2px;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

.${className}.active {
  outline: 3px solid #111827;
  outline-offset: 1px;
  box-shadow: 0 0 0 1px rgba(17, 24, 39, 0.1);
}

.${className}.accepted {
  box-shadow: 0 0 0 2px #16A34A, 0 2px 4px rgba(0,0,0,0.15);
}

.${className}.modified {
  box-shadow: 0 0 0 2px #D97706, 0 2px 4px rgba(0,0,0,0.15);
}

.${className}.created {
  box-shadow: 0 0 0 2px #2563EB, 0 2px 4px rgba(0,0,0,0.15);
}

${useColorblindFriendly ? `
.${className}::before {
  content: "";
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  background: ${pattern || 'none'};
  border-radius: 4px;
  z-index: -1;
}
` : ''}
    `;
  }).join('\n');
};

// Utility functions for color manipulation
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
}

function getContrastingTextColor(backgroundColor) {
  const rgb = hexToRgb(backgroundColor);
  if (!rgb) return '#000000';
  
  // Calculate luminance
  const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
  
  // Return black text for light backgrounds, white for dark
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
}

function darkenColor(color, percent) {
  const rgb = hexToRgb(color);
  if (!rgb) return color;
  
  const factor = (100 - percent) / 100;
  const r = Math.round(rgb.r * factor);
  const g = Math.round(rgb.g * factor);
  const b = Math.round(rgb.b * factor);
  
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
