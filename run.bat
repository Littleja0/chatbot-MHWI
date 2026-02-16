@echo off
setlocal
cd /d "%~dp0"

:: Testar Admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Solicitando acesso de Administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [OK] Rodando como Administrador!
:: ============================================
:: Monster Hunter World Chatbot - Launcher
:: ============================================

title MHW Chatbot

:: Check if Python is installed and in PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH!
    echo.
    echo Please install Python 3.10+ and make sure to check "Add Python to PATH" during installation.
    echo.
    echo Attempting to install via Winget...
    winget install -e --id Python.Python.3.11
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Failed to install Python automatically.
        echo Please manually install from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo.
    echo Python installed. Please REUSE this terminal or RESTART it to update environment variables.
    pause
    exit /b
)

echo [INFO] Python found. Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip not found! Please reinstall Python and ensure pip is included.
    pause
    exit /b 1
)

echo [INFO] Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ============================================
echo   Monster Hunter World: Iceborne Chatbot
echo   [Modular Architecture v2.0]
echo ============================================
echo.

:: O update agora é feito automaticamente dentro do main.py com Splash Screen

echo.
echo [INFO] Iniciando servidor...
echo [INFO] Acesse em: http://localhost:8000
echo [INFO] Pressione Ctrl+C no terminal para encerrar o processo.
echo.

:: IMPORTANTE: Manter CWD na raiz do projeto para que caminhos relativos
:: (rag/, storage/, backend/) funcionem corretamente nos módulos originais.
:: Usar caminho absoluto para o novo main.py.
if exist "apps\backend\src\main.py" (
    python apps\backend\src\main.py
) else (
    python backend\main.py
)
pause
