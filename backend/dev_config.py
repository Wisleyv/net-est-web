"""
Configurações centralizadas do ambiente de desenvolvimento
Baseado nas correções do diagnóstico em docs_dev/backend_windows_troubleshooting.md
"""

# Configurações do servidor
SERVER_CONFIG = {
    "host": "127.0.0.1",  # Sempre localhost para evitar bloqueios de firewall
    "port": 8000,         # Porta padrão (fallback para 8080 se ocupada)
    "fallback_port": 8080,
    "reload": True,       # Desenvolvimento
    "log_level": "info"
}

# URLs do frontend (devem corresponder ao SERVER_CONFIG)
FRONTEND_URLS = {
    "api_base": f"http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}",
    "text_input": f"http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}/api/v1/text-input",
    "semantic_alignment": f"http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}/semantic-alignment",
    "docs": f"http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}/docs"
}

# Caminhos do projeto
PROJECT_PATHS = {
    "backend_root": "C:\\net\\backend",
    "frontend_root": "C:\\net\\frontend", 
    "venv_python": "C:\\net\\backend\\venv\\Scripts\\python.exe",
    "venv_activate": "C:\\net\\backend\\venv\\Scripts\\activate.bat"
}

# Comandos padronizados
COMMANDS = {
    "start_server": f"{PROJECT_PATHS['venv_python']} -m uvicorn src.main:app --host {SERVER_CONFIG['host']} --port {SERVER_CONFIG['port']} --reload",
    "diagnose": f"{PROJECT_PATHS['venv_python']} diagnose_fixed.py",
    "test_port": f"{PROJECT_PATHS['venv_python']} -c \"import socket; s = socket.socket(); s.bind(('{SERVER_CONFIG['host']}', {SERVER_CONFIG['port']})); print('✅ Porta disponível'); s.close()\""
}

print("📋 Configurações carregadas com sucesso!")
print(f"🔧 Servidor: {SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}")
print(f"📂 Backend: {PROJECT_PATHS['backend_root']}")
