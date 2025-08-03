#!/usr/bin/env python3
"""
NET-est Backend - Diagnóstico Consolidado do Ambiente
Script de diagnóstico completo para verificação do ambiente de desenvolvimento
"""
import socket
import subprocess
import sys
import os
from pathlib import Path

def test_port(port=8000, host="127.0.0.1"):
    """Testa se a porta está disponível"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.bind((host, port))
        s.close()
        return True
    except (socket.error, OSError):
        return False

def check_virtual_env():
    """Verifica se o ambiente virtual está ativo"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def check_dependencies():
    """Verifica dependências principais"""
    dependencies = ['uvicorn', 'fastapi', 'pydantic', 'structlog']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    
    return missing

def check_project_structure():
    """Verifica estrutura do projeto"""
    required_paths = [
        Path("src/main.py"),
        Path("src/__init__.py"),
        Path("venv/Scripts/activate.bat"),
        Path("requirements.txt"),
        Path("start_optimized.py"),
        Path("start_optimized.bat")
    ]
    
    missing = []
    for path in required_paths:
        if not path.exists():
            missing.append(str(path))
    
    return missing

def check_processes():
    """Verifica processos Python/Uvicorn rodando"""
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        return len(result.stdout.splitlines()) > 3  # Header lines + processes
    except:
        return False

def main():
    print("🔍 NET-est Backend - Diagnóstico Consolidado")
    print("=" * 60)
    
    # Teste de portas
    ports = [8000, 8080, 3000]
    for port in ports:
        status = '✅ Disponível' if test_port(port) else '❌ Ocupada'
        print(f"🔌 Porta {port}: {status}")
    
    # Ambiente virtual
    venv_status = '✅ Ativo' if check_virtual_env() else '❌ Inativo'
    print(f"🐍 Ambiente Virtual: {venv_status}")
    
    # Dependências
    missing_deps = check_dependencies()
    if not missing_deps:
        print("📦 Dependências: ✅ Todas instaladas")
    else:
        print("📦 Dependências: ❌ Faltando:")
        for dep in missing_deps:
            print(f"   - {dep}")
    
    # Estrutura do projeto
    missing_files = check_project_structure()
    if not missing_files:
        print("📁 Estrutura do Projeto: ✅ OK")
    else:
        print("📁 Estrutura do Projeto: ❌ Arquivos faltando:")
        for file in missing_files:
            print(f"   - {file}")
    
    # Processos Python rodando
    python_running = check_processes()
    print(f"⚙️  Processos Python: {'⚠️  Rodando' if python_running else '✅ Limpo'}")
    
    print("\n" + "=" * 60)
    print("📖 Documentação: docs_dev/backend_windows_troubleshooting.md")
    print("🚀 Para iniciar: start_optimized.bat")
    print("🔧 Backup simples: start_backend.bat")

if __name__ == "__main__":
    main()
