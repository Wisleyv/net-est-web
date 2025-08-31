#!/usr/bin/env python3
"""
Simple Debug Script - No Unicode Issues
"""

import sys
import os
import subprocess
import requests
import json

def check_processes():
    """Check running processes"""
    print("CHECKING FOR RUNNING PYTHON PROCESSES...")

    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], capture_output=True, text=True)
        print("Python processes:")
        print(result.stdout)
    except Exception as e:
        print(f"Could not check processes: {e}")

def check_directories():
    """Check directories"""
    print("\nCHECKING DIRECTORIES...")

    dirs_to_check = [
        ".",
        "./backend",
        "c:/net/backend"
    ]

    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"Directory exists: {dir_path}")
            confidence_file = os.path.join(dir_path, "src", "services", "confidence_engine.py")
            if os.path.exists(confidence_file):
                print(f"  Found confidence_engine.py at: {confidence_file}")
                with open(confidence_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "min_sentence_count_ratio" in content:
                        print("  SUCCESS: Our fix IS present in the file")
                    else:
                        print("  PROBLEM: Our fix is NOT present in the file")
            else:
                print("  PROBLEM: confidence_engine.py NOT found")
        else:
            print(f"Directory does not exist: {dir_path}")

def test_api():
    """Test the API"""
    print("\nTESTING API...")

    test_payload = {
        "source_text": "Este e um texto complexo. Ele tem muitas ideias. Os pesquisadores fizeram estudo. Foram feitas analises. Os resultados mostram tendencias.",
        "target_text": "Este e um texto simples. Ele tem ideias. Os pesquisadores fizeram estudo. Foram feitas analises. Os resultados mostram tendencias. Esta e uma ideia extra. Mais uma informacao. Uma terceira ideia.",
        "analysis_options": {
            "include_strategy_identification": True
        }
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/comparative-analysis",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"API Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            strategies = data.get('simplification_strategies', [])
            print(f"Strategies detected: {len(strategies)}")

            for strategy in strategies:
                print(f"  - {strategy.get('code', 'UNKNOWN')}: {strategy.get('confidence', 0):.3f}")

            if len(strategies) == 0:
                print("PROBLEM: NO STRATEGIES DETECTED!")
                return False
            else:
                print("SUCCESS: Strategies detected!")
                return True
        else:
            print(f"API Error: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("PROBLEM: Cannot connect to server at localhost:8000")
        return False
    except Exception as e:
        print(f"API test failed: {e}")
        return False

def main():
    """Main function"""
    print("PRODUCTION SYSTEM DEBUG")
    print("=" * 40)

    check_processes()
    check_directories()
    api_works = test_api()

    print("\n" + "=" * 40)
    print("DEBUG COMPLETE")

    if not api_works:
        print("\nNEXT STEPS:")
        print("1. Check if server is running")
        print("2. Verify our changes are in the correct files")
        print("3. Restart server if needed")
        print("4. Check server logs for errors")

if __name__ == "__main__":
    main()