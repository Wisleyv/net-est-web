#!/usr/bin/env python3
"""
RADICAL DEBUGGING: Production System Investigation
Bypassing all assumptions to find the REAL issue
"""

import sys
import os
import subprocess
import requests
import json
from pathlib import Path

def find_all_python_processes():
    """Find all running Python processes that might be the server"""
    print("🔍 SEARCHING FOR RUNNING PYTHON PROCESSES...")

    try:
        # Find all Python processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], capture_output=True, text=True)
        print("Python processes found:")
        print(result.stdout)

        # Also check for uvicorn/fastapi processes
        result2 = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq uvicorn.exe'], capture_output=True, text=True)
        print("Uvicorn processes found:")
        print(result2.stdout)

    except Exception as e:
        print(f"Could not check processes: {e}")

def check_server_directories():
    """Check what directories the server might be running from"""
    print("\n📁 CHECKING SERVER DIRECTORIES...")

    possible_dirs = [
        ".",
        "./backend",
        "../backend",
        "c:/net/backend",
        "c:/net",
        os.getcwd(),
        os.path.dirname(os.getcwd())
    ]

    for dir_path in possible_dirs:
        if os.path.exists(dir_path):
            print(f"Directory exists: {dir_path}")
            if os.path.exists(os.path.join(dir_path, "src")):
                print(f"  ✅ Has src/ directory: {os.path.join(dir_path, 'src')}")
                # Check if our modified files are there
                confidence_file = os.path.join(dir_path, "src", "services", "confidence_engine.py")
                if os.path.exists(confidence_file):
                    print(f"  ✅ confidence_engine.py found at: {confidence_file}")
                    # Check if our fix is in the file
                    with open(confidence_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "min_sentence_count_ratio" in content:
                            print("  ✅ Our fix IS present in the file")
                        else:
                            print("  ❌ Our fix is NOT present in the file")
                else:
                    print("  ❌ confidence_engine.py NOT found")
        else:
            print(f"Directory does not exist: {dir_path}")

def check_environment_variables():
    """Check environment and Python path"""
    print("\n🌍 CHECKING ENVIRONMENT...")

    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")

    print("\nPYTHONPATH:")
    pythonpath = os.environ.get('PYTHONPATH', '')
    if pythonpath:
        for path in pythonpath.split(os.pathsep):
            print(f"  {path}")
    else:
        print("  (not set)")

    print("\nPython sys.path:")
    for path in sys.path:
        print(f"  {path}")

def test_direct_api_call():
    """Test the API directly to see what it returns"""
    print("\n🌐 TESTING API DIRECTLY...")

    # Test data that should trigger RP+
    test_payload = {
        "source_text": "Este é um texto complexo com muitas ideias. Ele contém conceitos avançados. Os pesquisadores desenvolveram uma metodologia sofisticada. Foram realizadas análises estatísticas complexas. Os resultados mostram tendências importantes.",
        "target_text": "Este é um texto simples. Ele contém conceitos básicos. Os pesquisadores criaram um método. Foram feitas análises. Os resultados mostram tendências. Esta é uma ideia adicional. Mais uma informação foi incluída. Uma terceira ideia importante.",
        "analysis_options": {
            "include_strategy_identification": True,
            "include_lexical_analysis": True,
            "include_syntactic_analysis": True,
            "include_semantic_analysis": True
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
                print("❌ NO STRATEGIES DETECTED - This confirms the issue!")

                # Let's also check the raw response
                print("\nFull response keys:")
                for key in data.keys():
                    print(f"  {key}: {type(data[key])}")

        else:
            print(f"API Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at localhost:8000")
        print("The server might not be running or running on a different port")
    except Exception as e:
        print(f"API test failed: {e}")

def check_file_modification_times():
    """Check when files were last modified"""
    print("\n⏰ CHECKING FILE MODIFICATION TIMES...")

    files_to_check = [
        "backend/src/services/strategy_detector.py",
        "backend/src/services/confidence_engine.py",
        "backend/src/strategies/cascade_orchestrator.py",
        "backend/src/strategies/stage_meso.py"
    ]

    for file_path in files_to_check:
        if os.path.exists(file_path):
            mod_time = os.path.getmtime(file_path)
            from datetime import datetime
            dt = datetime.fromtimestamp(mod_time)
            print(f"{file_path}: {dt}")
        else:
            print(f"{file_path}: FILE NOT FOUND")

def main():
    """Main radical debugging function"""
    print("RADICAL DEBUGGING: PRODUCTION SYSTEM INVESTIGATION")
    print("=" * 60)

    find_all_python_processes()
    check_server_directories()
    check_environment_variables()
    check_file_modification_times()
    test_direct_api_call()

    print("\n" + "=" * 60)
    print("RADICAL DEBUGGING COMPLETE")
    print("If the issue persists, we need to:")
    print("1. Find the EXACT server process and directory")
    print("2. Verify our changes are in the CORRECT files")
    print("3. Check if server needs restart or cache clear")
    print("4. Test with direct API calls to isolate frontend issues")

if __name__ == "__main__":
    main()