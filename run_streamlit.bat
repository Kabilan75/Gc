@echo off
REM Always starts Streamlit from THIS folder (the folder that contains this .bat file).
cd /d "%~dp0"
echo.
echo Starting Streamlit from:
echo   %CD%
echo   Main file: app.py
echo.
streamlit run "%~dp0app.py"
pause
