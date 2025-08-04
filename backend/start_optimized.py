#!/usr/bin/env python3
"""
NET-est Backend Server - Versão Definitiva Consolidada
Script de inicialização otimizado com configurações centralizadas
Implementa todas as correções documentadas em docs_dev/
"""
import socket
import uvicorn
import sys
import os
from pathlib import Path

# Add src to path to import settings
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from core.config import Settings
    settings = Settings()
except ImportError:
    # Fallback configuration if imports fail
    print("⚠️ Não foi possível carregar configurações do .env, usando valores padrão")
    class FallbackSettings:
        HOST = "127.0.0.1"
        PORT = 8000
        FALLBACK_PORT = 8080
        RELOAD = True
        LOG_LEVEL = "INFO"
    settings = FallbackSettings()

def test_port(host, port):
    """Testa se uma porta está disponível"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.bind((host, port))
        s.close()
        return True
    except (socket.error, OSError):
        return False

def get_available_port():
    """Retorna uma porta disponível com fallback inteligente"""
    host = settings.HOST
    primary_port = settings.PORT
    fallback_port = settings.FALLBACK_PORT
    
    if test_port(host, primary_port):
        print(f"✅ Porta {primary_port} disponível")
        return primary_port
    elif test_port(host, fallback_port):
        print(f"⚠️  Porta {primary_port} ocupada, usando {fallback_port}")
        return fallback_port
    else:
        print(f"❌ Ambas as portas ({primary_port}, {fallback_port}) estão ocupadas")
        return None

def main():
    """Função principal de inicialização"""
    print("🚀 NET-est Backend Server (Versão Consolidada)")
    print("=" * 55)
    
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Determinar porta disponível
    port = get_available_port()
    if not port:
        print("💡 Consulte docs_dev/backend_windows_troubleshooting.md")
        print("💡 Ou tente fechar outros serviços que usem as portas 8000/8080")
        return
    
    print(f"🔧 Configuração: {settings.HOST}:{port}")
    print(f"📖 Documentação: http://{settings.HOST}:{port}/docs")
    print(f"🌐 API Base: http://{settings.HOST}:{port}")
    print("🛑 Para parar: Ctrl+C")
    print("-" * 55)
    
    # Iniciar servidor com path absoluto
    app_path = f"{script_dir}/src/main:app"
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=port,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("💡 Consulte docs_dev/backend_windows_troubleshooting.md")
