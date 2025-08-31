#!/usr/bin/env python3
"""
Frontend API Test - Exact same call the frontend makes
"""

import requests
import json

def test_frontend_exact_call():
    """Test the exact API call the frontend makes"""

    # This is the EXACT payload format the frontend sends
    payload = {
        "source_text": "Texto original complexo com muitas frases elaboradas. Este parágrafo contém informações detalhadas sobre o tema principal. Os pesquisadores realizaram um estudo aprofundado da questão. Foram analisadas diversas variáveis importantes no processo. Os resultados indicam tendências significativas na área. Além disso, foram identificadas correlações relevantes entre os fatores. O estudo contribui para o avanço do conhecimento científico. Novos métodos foram desenvolvidos durante a pesquisa. A metodologia aplicada mostrou-se eficaz para os objetivos. Os dados coletados suportam as hipóteses iniciais do trabalho.",
        "target_text": "Texto simplificado com frases mais simples. Este parágrafo tem informações básicas sobre o tema. Os pesquisadores fizeram um estudo da questão. Foram analisadas algumas variáveis no processo. Os resultados mostram tendências na área. Também foram encontradas relações entre os fatores. O estudo ajuda o conhecimento científico. Novos métodos foram criados na pesquisa. A metodologia usada foi boa para os objetivos. Os dados coletados apoiam as ideias iniciais do trabalho. Esta é uma frase adicional para aumentar o tamanho. Mais uma informação importante foi incluída aqui. Outra ideia relevante para completar o texto.",
        "analysis_options": {
            "include_lexical_analysis": True,
            "include_syntactic_analysis": True,
            "include_semantic_analysis": True,
            "include_strategy_identification": True,
            "include_readability_metrics": True
        }
    }

    print("TESTING EXACT FRONTEND API CALL")
    print("=" * 50)
    print(f"Source text sentences: {len(payload['source_text'].split('. '))}")
    print(f"Target text sentences: {len(payload['target_text'].split('. '))}")
    print()

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/comparative-analysis",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Check strategies
            strategies = data.get('simplification_strategies', [])
            print(f"Strategies detected: {len(strategies)}")

            if len(strategies) == 0:
                print("❌ NO STRATEGIES DETECTED!")
                print("\nFull response structure:")
                for key in data.keys():
                    print(f"  {key}: {type(data[key])}")
                return False

            # Show each strategy
            print("\nDetected Strategies:")
            for i, strategy in enumerate(strategies):
                code = strategy.get('code', strategy.get('sigla', 'UNKNOWN'))
                confidence = strategy.get('confidence', strategy.get('confianca', 0))
                print(f"  {i+1}. {code}: {confidence:.3f}")

                # Check if strategy has position info
                if 'targetPosition' in strategy:
                    print(f"     Target Position: {strategy['targetPosition']}")
                if 'sourcePosition' in strategy:
                    print(f"     Source Position: {strategy['sourcePosition']}")

            # Check hierarchical analysis
            if 'hierarchical_analysis' in data and data['hierarchical_analysis']:
                print(f"\nHierarchical analysis present: {bool(data['hierarchical_analysis'])}")

            print("\n✅ SUCCESS: Strategies detected!")
            return True

        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_with_user_text():
    """Test with text that should definitely trigger strategies"""

    # Text designed to trigger multiple strategies
    payload = {
        "source_text": "Este é um texto muito complexo e elaborado com vocabulário técnico avançado. Os pesquisadores especializados realizaram uma investigação científica detalhada. Foram implementadas metodologias sofisticadas de análise estatística. Os resultados obtidos demonstram correlações significativas entre as variáveis estudadas.",
        "target_text": "Este é um texto simples e fácil de entender com palavras comuns. Os pesquisadores fizeram uma pesquisa simples. Foram usadas maneiras fáceis de analisar os dados. Os resultados mostram relações importantes entre as coisas estudadas. Esta é uma frase extra para tornar o texto maior. Mais uma ideia foi adicionada aqui. Outra informação relevante foi incluída.",
        "analysis_options": {
            "include_strategy_identification": True
        }
    }

    print("\nTESTING WITH USER-LIKE TEXT")
    print("=" * 50)

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/comparative-analysis",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            strategies = data.get('simplification_strategies', [])

            print(f"Strategies: {len(strategies)}")
            for strategy in strategies:
                code = strategy.get('code', strategy.get('sigla', 'UNKNOWN'))
                confidence = strategy.get('confidence', strategy.get('confianca', 0))
                print(f"  {code}: {confidence:.3f}")

            return len(strategies) > 0
        else:
            print(f"API Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_frontend_exact_call()
    success2 = test_with_user_text()

    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Frontend-style test: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"User-like test: {'✅ PASS' if success2 else '❌ FAIL'}")

    if not success1 or not success2:
        print("\n🔍 DEBUGGING NEEDED:")
        print("1. Check if server is running on correct port")
        print("2. Verify API endpoint is accessible")
        print("3. Check server logs for errors")
        print("4. Test with curl: curl -X POST http://localhost:8000/api/v1/comparative-analysis -H 'Content-Type: application/json' -d '{\"source_text\":\"test\",\"target_text\":\"test2\"}'")