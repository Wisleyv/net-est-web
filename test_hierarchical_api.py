#!/usr/bin/env python3
"""
Test script to verify hierarchical output feature is working correctly
"""

import requests
import json

def test_hierarchical_api():
    """Test the hierarchical output API functionality"""

    # API endpoint
    url = "http://localhost:8000/api/v1/comparative-analysis/"

    # Test data
    payload = {
        "source_text": "Este é um texto complexo com várias frases. Contém conceitos técnicos e vocabulário avançado que precisa ser simplificado.",
        "target_text": "Este é um texto simples com frases curtas. Usa palavras fáceis e ideias claras para ajudar a entender.",
        "analysis_options": {
            "include_lexical_analysis": False,
            "include_syntactic_analysis": False,
            "include_semantic_analysis": False,
            "include_readability_metrics": False,
            "include_strategy_identification": False
        }
    }

    print("Testing hierarchical output API...")

    # Test 1: Default behavior (should include hierarchical with feature flag enabled)
    print("\n1. Testing default behavior (feature flag enabled):")
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get('hierarchical_analysis'):
            print("✅ SUCCESS: Hierarchical analysis included by default")
            print(f"   Hierarchy version: {data['hierarchical_analysis']['hierarchy_version']}")
            print(f"   Source paragraphs: {len(data['hierarchical_analysis']['source_paragraphs'])}")
            print(f"   Target paragraphs: {len(data['hierarchical_analysis']['target_paragraphs'])}")
        else:
            print("❌ FAIL: Hierarchical analysis not included")
    else:
        print(f"❌ FAIL: API returned status {response.status_code}")

    # Test 2: Explicit hierarchical_output=true
    print("\n2. Testing explicit hierarchical_output=true:")
    response = requests.post(url, json=payload, params={"hierarchical_output": True})

    if response.status_code == 200:
        data = response.json()
        if data.get('hierarchical_analysis'):
            print("✅ SUCCESS: Hierarchical analysis included with query param")
        else:
            print("❌ FAIL: Hierarchical analysis not included with query param")
    else:
        print(f"❌ FAIL: API returned status {response.status_code}")

    # Test 3: Explicit hierarchical_output=false (should override feature flag)
    print("\n3. Testing explicit hierarchical_output=false:")
    response = requests.post(url, json=payload, params={"hierarchical_output": False})

    if response.status_code == 200:
        data = response.json()
        if data.get('hierarchical_analysis') is None:
            print("✅ SUCCESS: Hierarchical analysis correctly disabled with query param")
        else:
            print("❌ FAIL: Hierarchical analysis still included despite query param")
    else:
        print(f"❌ FAIL: API returned status {response.status_code}")

    print("\n🎉 Hierarchical output feature test completed!")

if __name__ == "__main__":
    test_hierarchical_api()