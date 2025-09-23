// Test script to verify frontend highlighting
// Run this in the browser console at http://localhost:5173

async function testHighlighting() {
  console.log('🧪 Testing frontend highlighting...');
  
  // Test data
  const sourceText = "O estudo demonstra que os resultados obtidos através da utilização de métodos estatísticos avançados confirmam a hipótese inicial proposta pelos pesquisadores.";
  const targetText = "O estudo mostra que os resultados conseguidos com métodos estatísticos simples confirmam a ideia inicial dos pesquisadores.";
  
  // Fill the form programmatically
  const sourceInput = document.querySelector('textarea[placeholder*="texto original"]');
  const targetInput = document.querySelector('textarea[placeholder*="texto simplificado"]');
  
  if (sourceInput && targetInput) {
    sourceInput.value = sourceText;
    targetInput.value = targetText;
    
    // Trigger change events
    sourceInput.dispatchEvent(new Event('input', { bubbles: true }));
    targetInput.dispatchEvent(new Event('input', { bubbles: true }));
    
    console.log('✅ Form filled');
    
    // Find and click the analyze button
    const analyzeButton = document.querySelector('button[type="submit"], button:contains("Analisar")');
    if (analyzeButton) {
      analyzeButton.click();
      console.log('✅ Analysis started');
    } else {
      console.log('❌ Could not find analyze button');
    }
  } else {
    console.log('❌ Could not find text inputs');
  }
}

// Run the test
testHighlighting();