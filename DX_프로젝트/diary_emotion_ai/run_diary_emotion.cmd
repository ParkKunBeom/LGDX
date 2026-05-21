@echo off
chcp 65001 >nul
setlocal
set "APP_DIR=%~dp0"
set "PREDICT_SCRIPT=%APP_DIR%scripts\03_predict_diary_emotion.ps1"

if not exist "%PREDICT_SCRIPT%" (
  echo Prediction script was not found.
  pause
  exit /b 1
)

echo.
echo Diary Emotion Analyzer
echo Type diary text and press Enter.
echo Press Enter with empty text to exit.
echo.

:loop
set "DIARY_TEXT="
set /p "DIARY_TEXT=Diary text> "
if "%DIARY_TEXT%"=="" exit /b 0
powershell -NoProfile -ExecutionPolicy Bypass -File "%PREDICT_SCRIPT%" -Text "%DIARY_TEXT%"
echo.
goto loop
