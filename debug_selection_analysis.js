// DOM Selection Analysis Test
// This will help analyze the handleTextSelection function behavior

// Sample text with duplicate "mulher" for testing
const sampleTargetText = `A mulher estava caminhando na rua. Ela viu outra pessoa. A segunda mulher também estava andando. Ambas as mulheres se cumprimentaram. A primeira mulher sorriu para a outra mulher.`;

console.log('=== SAMPLE TEXT ANALYSIS ===');
console.log('Full text:', sampleTargetText);
console.log('Text length:', sampleTargetText.length);

// Find all occurrences of "mulher"
const searchWord = 'mulher';
const occurrences = [];
let index = sampleTargetText.indexOf(searchWord);
while (index !== -1) {
  occurrences.push({
    word: searchWord,
    position: index,
    endPosition: index + searchWord.length,
    context: sampleTargetText.substring(Math.max(0, index - 20), index + searchWord.length + 20)
  });
  index = sampleTargetText.indexOf(searchWord, index + 1);
}

console.log('\n=== ALL OCCURRENCES OF "' + searchWord + '" ===');
occurrences.forEach((occ, i) => {
  console.log(`Occurrence ${i + 1}:`);
  console.log(`  Position: ${occ.position}-${occ.endPosition}`);
  console.log(`  Context: "${occ.context}"`);
  console.log(`  Sentence: ${Math.floor(occ.position / 50) + 1} (approximate)`);
});

console.log('\n=== EXPECTED BEHAVIOR ===');
console.log('When user selects "mulher" in different sentences:');
occurrences.forEach((occ, i) => {
  console.log(`Selection ${i + 1} should map to position ${occ.position}, not position ${occurrences[0].position}`);
});