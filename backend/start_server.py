#!/usr/bin/env python3
"""
Script de inicialização do servidor backend FastAPI
Implementa as correções definidas no diagnóstico de troubleshooting
"""
import uvicorn

def main():
    print("Starting backend server on port 8000...")
    print("Configuration: host=127.0.0.1, port=8000")
    print("Module: src.main:app")

    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Check docs_dev/backend_windows_troubleshooting.md for solutions")
