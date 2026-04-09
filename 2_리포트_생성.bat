@echo off
title Factory_Report_Generator
cd /d "%~dp0"

echo ==============================================
echo  Generating Factory Temperature Report (PDF)...
echo ==============================================

python factory_report_manager.py

echo.
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to generate report.
) else (
    echo [SUCCESS] Report generation completed.
)
echo.
pause
