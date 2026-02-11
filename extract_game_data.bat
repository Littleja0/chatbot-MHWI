@echo off
setlocal

:: ============================================
:: Extracao COMPLETA de dados do jogo MHW
:: ============================================

title Extrator de Dados MHW

echo.
echo ============================================
echo   Extrator de Dados do Jogo MHW:Iceborne
echo ============================================
echo.
echo Este script vai:
echo 1. Localizar sua instalacao do MHW (Steam)
echo 2. Baixar ferramentas de extracao automaticamente
echo 3. Extrair dados dos arquivos do jogo
echo 4. Gerar um banco de dados atualizado
echo.
echo ATENCAO: Este processo pode demorar 15-30 minutos
echo e requer ~10GB de espaco em disco temporario.
echo.
echo O jogo NAO pode estar em execucao durante a extracao.
echo.

set /p confirm="Deseja continuar? (S/N): "
if /i not "%confirm%"=="S" (
    echo Operacao cancelada.
    pause
    exit /b
)

echo.
echo Iniciando extracao...
echo.

python backend/auto_update_db.py --full

echo.
if %errorlevel% equ 0 (
    echo ============================================
    echo [SUCESSO] Banco de dados atualizado!
    echo ============================================
) else (
    echo [ERRO] Falha na extracao, verifique os erros acima.
)

echo.
pause
