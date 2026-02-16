@echo off
cd /d "%~dp0"

:: Auto-Admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Solicitando acesso de Administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ============================================
echo   DIAGNOSTICO DE MEMORIA v6 - MHW Chatbot
echo ============================================
echo.

:: Instalar pymem na venv se necessario
echo [INFO] Verificando pymem...
"%~dp0.venv\Scripts\pip.exe" install pymem >nul 2>&1
echo [OK] pymem verificado!
echo.
echo Certifique-se de que o MHW esta aberto com o save carregado!
echo.
echo ANTES DE RODAR, verifique se os valores em diagnostico_v6.py
echo estao corretos:
echo   - PLAYER_NAME  = seu nome no jogo
echo   - HR_REAL      = seu Hunter Rank
echo   - MR_REAL      = seu Master Rank
echo.

"%~dp0.venv\Scripts\python.exe" "%~dp0diagnostico_v6.py"

pause
