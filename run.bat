@echo off
setlocal
cd /d "%~dp0"

:: ============================================
:: Monster Hunter World Chatbot - Launcher
:: ============================================

title MHW Chatbot

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH!
    pause
    exit /b 1
)

:: Check Frontend Build
if not exist "apps\frontend\dist\index.html" (
    echo [INFO] Frontend build not found. Building...
    cd apps\frontend
    call npm install
    call npm run build
    cd ..\..
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to build frontend.
        pause
        exit /b 1
    )
    echo [INFO] Frontend built successfully.
)

echo [INFO] Installing python dependencies...
pip install -q -r requirements.txt

echo.
echo ============================================
echo   MHW:I Chatbot - Ready
echo ============================================
echo.


echo.
echo [INFO] Iniciando servidor...
echo [INFO] Acesse em: http://localhost:8000
echo [INFO] Pressione Ctrl+C no terminal para encerrar o processo.
echo.

:: IMPORTANTE: Manter CWD na raiz do projeto para que caminhos relativos
:: (rag/, storage/, backend/) funcionem corretamente nos módulos originais.
:: Usar caminho absoluto para o novo main.py.
python apps\backend\src\main.py
pause
