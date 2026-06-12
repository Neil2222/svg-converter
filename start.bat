@echo off
setlocal
cd /d "%~dp0"

set "VENV_DIR=.venv"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "URL=http://127.0.0.1:5285"

if not exist "%PYTHON%" (
    echo Python virtual environment wordt aangemaakt...
    py -3.11 -m venv "%VENV_DIR%"
    if errorlevel 1 (
        python -m venv "%VENV_DIR%"
    )
)

if not exist "%PYTHON%" (
    echo.
    echo Kon geen virtual environment maken.
    echo Installeer Python 3.11 of nieuwer en probeer opnieuw.
    pause
    exit /b 1
)

echo Dependencies worden gecontroleerd/geinstalleerd...
"%PYTHON%" -m pip install -e .
if errorlevel 1 (
    echo.
    echo Installatie van dependencies is mislukt.
    pause
    exit /b 1
)

echo.
echo Server start op %URL%
echo Sluit dit venster om de server te stoppen.
start "" "%URL%"
"%PYTHON%" -m uvicorn server:app --host 0.0.0.0 --port 5285
pause
