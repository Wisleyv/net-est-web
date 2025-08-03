@echo off
REM ========================================
REM   NET-est Backend Server (Consolidado)
REM   Versão definitiva com todas as correções
REM ========================================

echo 🚀 NET-est Backend Server - Versão Consolidada
echo.

cd /d "C:\net\backend"

REM Verificações de integridade
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Ambiente virtual não encontrado!
    echo 💡 Execute: python -m venv venv && .\venv\Scripts\activate && pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "src\main.py" (
    echo ❌ Arquivo principal src\main.py não encontrado!
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call .\venv\Scripts\activate.bat

REM Verificar dependências críticas
echo 🔍 Verificando dependências...
.\venv\Scripts\python.exe -c "import uvicorn, fastapi; print('✅ Dependências OK')" 2>nul
if errorlevel 1 (
    echo ❌ Dependências não encontradas!
    echo 💡 Execute: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Executar servidor otimizado
echo.
echo 🎯 Iniciando servidor com detecção automática de porta...
echo.
.\venv\Scripts\python.exe start_optimized.py

pause
