@echo off
echo ========================================
echo Urban Mobility Analytics
echo Iniciando Dashboard...
echo ========================================
echo.

REM Verificar se venv existe
if not exist .venv (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Por favor, execute primeiro: INSTALL-WINDOWS-FIX.bat
    pause
    exit /b 1
)

REM Ativar venv
call .venv\Scripts\activate.bat

REM Verificar se streamlit esta instalado
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ERRO: Streamlit nao instalado!
    echo Execute: INSTALL-WINDOWS-FIX.bat
    pause
    exit /b 1
)

REM Iniciar dashboard
echo.
echo Dashboard abrindo no navegador...
echo Pressione Ctrl+C para parar
echo.
streamlit run src\urban_mobility\dashboard.py

pause
