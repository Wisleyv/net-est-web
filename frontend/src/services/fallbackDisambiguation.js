// fallbackDisambiguation.js
// Provides a context-aware fallback for mapping a selected substring to the correct
// occurrence inside a full text when duplicates exist.

function isBoundaryChar(ch) {
  if (!ch) return true; // start or end of string counts as boundary
  return /[\s\.,;:!\?\)\(\[\]\{\}"'\-]/.test(ch);
}

function findAllOccurrences(fullText, needle) {
  const occurrences = [];
  if (!needle || needle.length === 0) return occurrences;
  let idx = 0;
  while (true) {
    const found = fullText.indexOf(needle, idx);
    if (found === -1) break;
    occurrences.push(found);
    idx = found + 1; // allow overlapping occurrences
  }
  return occurrences;
}

function disambiguateWithContext(fullText, selectedString, approximatePosition = null) {
  if (typeof fullText !== 'string' || typeof selectedString !== 'string') return null;
  const occurrences = findAllOccurrences(fullText, selectedString);
  if (occurrences.length === 0) return null;

  // If no approximate position provided, prefer the last occurrence (heuristic for selections near end)
  let bestIdx = null;
  if (typeof approximatePosition === 'number' && !Number.isNaN(approximatePosition)) {
    let bestDist = Infinity;
    for (const occ of occurrences) {
      const dist = Math.abs(occ - approximatePosition);
      if (dist < bestDist) { bestDist = dist; bestIdx = occ; }
    }
  } else {
    bestIdx = occurrences[occurrences.length - 1];
  }

  // Validate boundary of the chosen occurrence; if invalid, try next-closest occurrence
  const ordered = occurrences
    .map(o => ({ o, dist: Math.abs(o - (approximatePosition ?? fullText.length)) }))
    .sort((a, b) => a.dist - b.dist)
    .map(x => x.o);

  for (const occ of ordered) {
    const before = fullText[occ - 1];
    const after = fullText[occ + selectedString.length];
    if (isBoundaryChar(before) && isBoundaryChar(after)) {
      return { start: occ, end: occ + selectedString.length };
    }
  }

  // If no occurrence had clean boundaries, return the bestIdx match anyway
  return { start: bestIdx, end: bestIdx + selectedString.length };
}

export { disambiguateWithContext };
