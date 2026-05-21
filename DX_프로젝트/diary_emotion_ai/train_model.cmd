@echo off
chcp 65001 >nul
setlocal
if defined PYTHON_CMD goto run
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
  set "PYTHON_CMD=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
  goto run
)
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=py -3"
  goto run
)
where python >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=python"
  goto run
)
echo Python was not found. Install Python 3 or set PYTHON_CMD.
exit /b 1
:run
%PYTHON_CMD% "%~dp0scripts\02_train_naive_bayes.py"
