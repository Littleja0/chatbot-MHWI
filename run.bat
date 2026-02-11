@echo off
setlocal

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
echo ============================================
echo.

:: O update agora é feito automaticamente dentro do main.py com Splash Screen

echo.
echo [INFO] Iniciando servidor...
echo [INFO] Acesse em: http://localhost:8000
echo [INFO] Pressione Ctrl+C para parar o servidor
echo.
python backend/main.py
pause

