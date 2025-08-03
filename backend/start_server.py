#!/usr/bin/env python3
"""
Script de inicialização do servidor backend FastAPI
Implementa as correções definidas no diagnóstico de troubleshooting
"""
import uvicorn

def main():
    print("🚀 Iniciando servidor backend na porta 8000...")
    print("� Configuração: host=127.0.0.1, porta=8000")
    print("📂 Módulo: src.main:app")
    
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
        print(f"❌ Erro ao iniciar servidor: {e}")
        print("💡 Consulte docs_dev/backend_windows_troubleshooting.md para soluções")

