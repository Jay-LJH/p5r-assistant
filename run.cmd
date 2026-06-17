@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
python -m p5r_assistant.app run
exit /b %ERRORLEVEL%
