@echo off
setlocal

:: ============================================
:: Atualiza o banco de dados do MHW (Forcado)
:: ============================================

title Atualizador MHW DB

echo.
echo ============================================
echo   Atualizador de Banco de Dados MHW
echo ============================================
echo.
echo Este script vai baixar a versao mais recente
echo do banco de dados do GitHub.
echo.

python backend/auto_update_db.py --force

echo.
if %errorlevel% equ 0 (
    echo [SUCESSO] Banco de dados atualizado!
) else (
    echo [ERRO] Falha ao atualizar banco de dados
)

echo.
pause
