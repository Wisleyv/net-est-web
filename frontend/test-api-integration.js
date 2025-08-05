// Test script to verify frontend integration
// Open browser console and run this to test the API directly

async function testComparativeAnalysis() {
  const sourceText = "Este é um texto complexo que utiliza terminologia técnica e estruturas sintáticas elaboradas, com vocabulário erudito e períodos extensos que dificultam a compreensão por parte de leitores com menor proficiência linguística.";
  const targetText = "Este é um texto simples que usa palavras fáceis e frases curtas que todos podem entender.";
  
  try {
    const response = await fetch('/api/v1/comparative-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        source_text: sourceText,
        target_text: targetText,
        analysis_options: {
          include_lexical_analysis: true,
          include_syntactic_analysis: true,
          include_semantic_analysis: true,
          include_readability_metrics: true,
          include_strategy_identification: true,
        }
      })
    });
    
    const data = await response.json();
    console.log('API Response:', data);
    console.log('Strategies found:', data.simplification_strategies);
    console.log('Strategy count:', data.strategies_count);
    
    return data;
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Run the test
testComparativeAnalysis();

/*
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
*/
