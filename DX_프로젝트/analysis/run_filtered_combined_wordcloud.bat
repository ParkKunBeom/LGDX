@echo off
set PYTHON_EXE=C:\Users\Park_kunbeom\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
set SCRIPT_PATH=%~dp0make_filtered_combined_wordcloud.py

"%PYTHON_EXE%" -u "%SCRIPT_PATH%"
pause
