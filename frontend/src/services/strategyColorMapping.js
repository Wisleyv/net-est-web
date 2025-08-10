/**
 * Strategy Color Mapping Configuration for NET-EST
 * Maps each of the 14 simplification strategies to a distinct, accessible color
 */

// Strategy color mapping with accessibility considerations
export const STRATEGY_COLORS = {
  'AS+': '#FF6B6B',  // Red - Alteração de Sentido
  'DL+': '#4ECDC4',  // Teal - Reorganização Posicional  
  'EXP+': '#45B7D1', // Blue - Explicitação e Detalhamento
  'IN+': '#96CEB4',  // Green - Manejo de Inserções
  'MOD+': '#FFEAA7', // Yellow - Reinterpretação Perspectiva
  'MT+': '#DDA0DD',  // Plum - Otimização de Títulos
  'OM+': '#F0F0F0',  // Light Gray - Supressão Seletiva (special handling)
  'PRO+': '#FFB347', // Orange - Desvio Semântico (manual only)
  'RF+': '#FF8A80',  // Light Red - Reescrita Global
  'RD+': '#80CBC4',  // Light Teal - Estruturação de Conteúdo
  'RP+': '#81C784',  // Light Green - Fragmentação Sintática
  'SL+': '#64B5F6',  // Light Blue - Adequação de Vocabulário
  'TA+': '#BA68C8',  // Purple - Clareza Referencial
  'MV+': '#FFD54F'   // Amber - Alteração da Voz Verbal
};

// Alternative colorblind-friendly palette
export const STRATEGY_COLORS_COLORBLIND = {
  'AS+': '#E69F00',  // Orange
  'DL+': '#56B4E9',  // Sky Blue
  'EXP+': '#009E73', // Bluish Green
  'IN+': '#F0E442',  // Yellow
  'MOD+': '#0072B2', // Blue
  'MT+': '#D55E00',  // Vermillion
  'OM+': '#F5F5F5',  // Light Gray (special)
  'PRO+': '#CC79A7', // Reddish Purple
  'RF+': '#E31A1C',  // Red
  'RD+': '#1F78B4',  // Blue
  'RP+': '#33A02C',  // Green
  'SL+': '#A6CEE3',  // Light Blue
  'TA+': '#B2DF8A',  // Light Green
  'MV+': '#FDBF6F'   // Light Orange
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

// Utility functions for color management
export const getStrategyColor = (strategyCode, useColorblindFriendly = false) => {
  const colorMap = useColorblindFriendly ? STRATEGY_COLORS_COLORBLIND : STRATEGY_COLORS;
  return colorMap[strategyCode] || '#CCCCCC'; // Default gray for unknown strategies
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

// Generate CSS for strategy highlighting
export const generateStrategyCSSClasses = (useColorblindFriendly = false) => {
  const colors = getAllStrategyColors(useColorblindFriendly);
  
  return Object.entries(colors).map(([code, color]) => {
    const className = getStrategyClassName(code);
    return `
.${className} {
  background-color: ${color};
  color: ${getContrastingTextColor(color)};
  padding: 2px 4px;
  border-radius: 3px;
  border: 1px solid ${darkenColor(color, 20)};
  display: inline;
  position: relative;
}

.${className}:hover {
  background-color: ${darkenColor(color, 10)};
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.${className}.selected {
  outline: 2px solid #333;
  outline-offset: 1px;
}
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
