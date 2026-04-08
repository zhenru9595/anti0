@echo off
title Drawing Extractor
echo =======================================
echo Starting Drawing Extractor...
echo =======================================

cd /d "%~dp0"
python drawing_extractor.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Program crashed with exit code %ERRORLEVEL%.
    pause
)
