// Browser test script for HITL functionality
// Paste this in browser console at http://localhost:5174

async function testHITLWorkflow() {
  console.log('🧪 Testing HITL workflow...');
  
  // 1. Fill form with test data
  const sourceTextarea = document.querySelector('textarea[name="sourceText"]') || 
                         document.querySelector('textarea[placeholder*="original"]') ||
                         document.querySelector('textarea:first-of-type');
  
  const targetTextarea = document.querySelector('textarea[name="targetText"]') || 
                         document.querySelector('textarea[placeholder*="simplificado"]') ||
                         document.querySelector('textarea:last-of-type');
  
  const sourceText = "O estudo demonstra que os resultados obtidos através da utilização de métodos estatísticos avançados confirmam a hipótese inicial proposta pelos pesquisadores.";
  const targetText = "O estudo mostra que os resultados conseguidos com métodos estatísticos simples confirmam a ideia inicial dos pesquisadores.";
  
  if (sourceTextarea && targetTextarea) {
    sourceTextarea.value = sourceText;
    targetTextarea.value = targetText;
    
    // Trigger React events
    ['input', 'change'].forEach(eventType => {
      sourceTextarea.dispatchEvent(new Event(eventType, { bubbles: true }));
      targetTextarea.dispatchEvent(new Event(eventType, { bubbles: true }));
    });
    
    console.log('✅ Form filled with test data');
    
    // 2. Find and click analyze button
    const buttons = document.querySelectorAll('button');
    const analyzeButton = Array.from(buttons).find(btn => 
      btn.textContent.includes('Analisar') || 
      btn.textContent.includes('Comparar') ||
      btn.type === 'submit'
    );
    
    if (analyzeButton) {
      console.log('🚀 Starting analysis...');
      analyzeButton.click();
      
      // Wait for analysis to complete and check for results
      setTimeout(() => {
        const debugElement = document.querySelector('[style*="background: red"]');
        if (debugElement) {
          console.log('✅ Results view loaded - HITL functionality should be active');
          console.log('📝 Now test:');
          console.log('  1. Select text in "Texto Simplificado" area');
          console.log('  2. Right-click should show custom menu (not browser menu)');
          console.log('  3. Click on any highlighted tag to see inline editor');
        } else {
          console.log('❌ Results view not loaded yet or analysis failed');
        }
      }, 5000);
      
    } else {
      console.log('❌ Analyze button not found');
      console.log('Available buttons:', Array.from(buttons).map(b => b.textContent));
    }
  } else {
    console.log('❌ Text areas not found');
    console.log('Available textareas:', document.querySelectorAll('textarea').length);
  }
}

// Run the test
testHITLWorkflow();