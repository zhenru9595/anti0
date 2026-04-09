@echo off
title Factory_System_V2_Report_Generator
cd /d "%~dp0"

echo ==============================================
echo  Generating PDF Report from Excel (V2)...
echo ==============================================

python v2_report_gen.py

echo.
echo Operation Completed.
pause
