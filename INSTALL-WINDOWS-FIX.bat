@echo off
echo ========================================
echo Urban Mobility - Instalacao Windows
echo ========================================
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale Python 3.9+ de python.org
    pause
    exit /b 1
)

echo Python encontrado!
echo.

REM Criar venv se nao existir
if not exist .venv (
    echo Criando ambiente virtual...
    python -m venv .venv
    echo Ambiente virtual criado!
) else (
    echo Ambiente virtual ja existe.
)
echo.

REM Ativar venv
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Atualizando pip...
python -m pip install --upgrade pip --quiet
echo.

REM Instalar dependencias NA ORDEM CERTA
echo Instalando dependencias...
echo (Isso pode levar alguns minutos)
echo.
pip install streamlit==1.31.0 --quiet
pip install folium==0.15.1 --quiet
pip install streamlit-folium==0.18.0 --quiet
pip install plotly==5.18.0 --quiet
pip install pandas==2.1.4 --quiet
pip install requests==2.31.0 --quiet

echo.
echo Testando instalacao...
python -c "import streamlit, folium, streamlit_folium, plotly, pandas, requests; print('Sucesso! Todos os modulos instalados!')"

if errorlevel 1 (
    echo.
    echo AVISO: Alguns modulos podem ter falhado.
    echo Execute: CORRECAO-VERSOES.bat
) else (
    echo.
    echo ========================================
    echo Instalacao concluida com sucesso!
    echo ========================================
)

echo.
echo Para iniciar o dashboard, execute: START-WINDOWS.bat
echo.
pause
