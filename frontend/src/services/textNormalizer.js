// textNormalizer.js
// Core normalization and hashing utilities for selection offset calculation

function normalizeTextForOffsets(text) {
  if (typeof text !== 'string') return '';
  // Remove bracketed markers like [OM+], [SL-], [RF+], etc.
  let s = text.replace(/\[[^\]]+\]/g, '');
  // Remove common invisible/zero-width characters
  s = s.replace(/[\u200B-\u200F\uFEFF]/g, '');
  // Normalize whitespace to single space and trim
  s = s.replace(/\s+/g, ' ').trim();
  return s;
}

async function computeSHA256Hex(str) {
  if (typeof str !== 'string') str = String(str || '');

  // Prefer Web Crypto if available (browser environments)
  if (typeof globalThis !== 'undefined' && globalThis.crypto && globalThis.crypto.subtle && typeof globalThis.crypto.subtle.digest === 'function') {
    const enc = new TextEncoder();
    const data = enc.encode(str);
    const hash = await globalThis.crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  // Fallback: Node's crypto module if available
  try {
    // dynamic require to avoid bundler issues
    // eslint-disable-next-line global-require
    const nodeCrypto = require('crypto');
    return nodeCrypto.createHash('sha256').update(str, 'utf8').digest('hex');
  } catch (e) {
    // Last-resort: non-cryptographic checksum (not recommended for production but safe for telemetry)
    let h = 0;
    for (let i = 0; i < str.length; i++) {
      h = (h << 5) - h + str.charCodeAt(i);
      h |= 0;
    }
    return (h >>> 0).toString(16);
  }
}

export { normalizeTextForOffsets, computeSHA256Hex };
