@echo off
echo ========================================
echo Corrigindo Versoes - Urban Mobility
echo ========================================
echo.

REM Ativar venv
call .venv\Scripts\activate.bat

echo Desinstalando versoes conflitantes...
pip uninstall -y streamlit-folium folium 2>nul

echo.
echo Instalando versoes corretas...
echo.

pip install streamlit==1.31.0 --quiet
pip install folium==0.15.1 --quiet
pip install streamlit-folium==0.18.0 --quiet
pip install plotly==5.18.0 --quiet
pip install pandas==2.1.4 --quiet
pip install requests==2.31.0 --quiet

echo.
echo ========================================
echo Correcao concluida!
echo ========================================
echo.
echo Testando instalacao...
python -c "import streamlit, folium, streamlit_folium, plotly, pandas, requests; print('✓ Todos os modulos instalados corretamente!')"
echo.
echo Para iniciar o dashboard: START-WINDOWS.bat
echo.
pause
