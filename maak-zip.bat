@echo off
setlocal
cd /d "%~dp0"

set "ZIP_NAME=svg-converter.zip"
set "STAGE_DIR=%TEMP%\svg-converter-zip"

if exist "%STAGE_DIR%" rmdir /s /q "%STAGE_DIR%"
mkdir "%STAGE_DIR%"

copy /y "server.py" "%STAGE_DIR%\" >nul
copy /y "pyproject.toml" "%STAGE_DIR%\" >nul
copy /y "start.bat" "%STAGE_DIR%\" >nul
copy /y "README.md" "%STAGE_DIR%\" >nul
xcopy /e /i /y "static" "%STAGE_DIR%\static" >nul

if exist "%ZIP_NAME%" del /q "%ZIP_NAME%"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Compress-Archive -Path '%STAGE_DIR%\*' -DestinationPath '%CD%\%ZIP_NAME%' -Force"

if errorlevel 1 (
    echo.
    echo Zip maken is mislukt.
    pause
    exit /b 1
)

rmdir /s /q "%STAGE_DIR%"

echo.
echo Klaar: %ZIP_NAME%
echo Deze zip bevat alleen de bestanden die nodig zijn om de app lokaal te starten.
pause
