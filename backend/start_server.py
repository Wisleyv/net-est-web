#!/usr/bin/env python3
"""
Script de inicialização do servidor backend FastAPI
This version avoids printing non-ASCII characters to the console
to prevent encoding errors on Windows consoles.
"""
import uvicorn

def main():
    # Use plain ASCII messages to avoid Windows encoding issues
    print("Starting backend server on port 8000...")
    print("Config: host=127.0.0.1, port=8000")
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
        # Print ASCII-only error messages (no emoji) to avoid encoding problems
        print(f"Error starting server: {e}")
        print("See docs_dev/backend_windows_troubleshooting.md for guidance")
