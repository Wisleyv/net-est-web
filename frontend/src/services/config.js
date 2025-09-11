/**
 * Configurações centralizadas do frontend
 */

// Support running under Vitest/Node where import.meta.env may be undefined
const env = (typeof import.meta !== 'undefined' && import.meta.env)
  ? import.meta.env
  : (typeof process !== 'undefined' && process.env ? process.env : {});

const config = {
  API_BASE_URL: env.VITE_API_BASE_URL || 'http://localhost:8000',
  APP_NAME: env.VITE_APP_NAME || 'NET-EST',
  VERSION: env.VITE_VERSION || '1.0.0',
  DEBUG: (env.VITE_DEBUG === 'true') || false,

  // Limites de interface
  MAX_WORDS_WARNING: 2000,
  MAX_FILE_SIZE_MB: 10,

  // Timeouts
  API_TIMEOUT: 120000, // 120 segundos (increased for large text analysis)

  // URLs de documentação
  DOCS_URL: 'https://github.com/net-est/docs',
  REPO_URL: 'https://github.com/net-est/net-est',
};

export default config;
