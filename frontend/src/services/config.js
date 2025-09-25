/**
 * Configurações centralizadas do frontend
 */

const config = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
  APP_NAME: import.meta.env.VITE_APP_NAME || 'NET-EST',
  VERSION: import.meta.env.VITE_VERSION || '1.0.0',
  DEBUG: import.meta.env.VITE_DEBUG === 'true' || false,

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
