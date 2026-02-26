@echo off
echo ========================================
echo   Application Analyse Escrime
echo ========================================
echo.
echo Installation des dependances...
pip install -r requirements.txt
echo.
echo Lancement de l'application...
echo.
echo L'application va s'ouvrir dans votre navigateur
echo Appuyez sur Ctrl+C pour arreter l'application
echo.
streamlit run app.py
pause
