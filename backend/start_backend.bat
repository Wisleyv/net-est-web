@echo off
REM ========================================
REM   NET-est Backend - Inicialização Simples
REM   Script backup para inicialização direta
REM ========================================

echo 🚀 NET-est Backend Server - Inicialização Simples
echo.

cd /d "C:\net\backend"

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call .\venv\Scripts\activate.bat

echo.
echo 🎯 Iniciando servidor na porta 8000...
echo 📖 Documentação: http://localhost:8000/docs
echo 🛑 Para parar: Ctrl+C
echo.

.\venv\Scripts\python.exe start_server.py

pause

pause
