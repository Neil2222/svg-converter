@echo off
setlocal
cd /d "%~dp0"

set "VENV_DIR=.venv"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo Python virtual environment wordt aangemaakt...
    py -3.11 -m venv "%VENV_DIR%"
    if errorlevel 1 (
        python -m venv "%VENV_DIR%"
    )
)

if not exist "%PYTHON%" (
    echo.
    echo Kon geen virtual environment maken. Installeer Python 3.11 of nieuwer.
    pause
    exit /b 1
)

echo Dependencies en PyInstaller worden geinstalleerd...
"%PYTHON%" -m pip install -e . pyinstaller
if errorlevel 1 (
    echo.
    echo Installatie is mislukt.
    pause
    exit /b 1
)

echo.
echo De exe wordt gebouwd (dit kan enkele minuten duren)...
"%PYTHON%" -m PyInstaller --noconfirm --clean svg-converter.spec
if errorlevel 1 (
    echo.
    echo Build is mislukt.
    pause
    exit /b 1
)

echo.
echo Klaar: dist\svg-converter.exe
echo Dit is een zelfstandige exe; de ontvanger heeft geen Python nodig.
pause
