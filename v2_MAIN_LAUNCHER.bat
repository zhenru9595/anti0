@echo off
title Factory_System_V2_Main_Launcher
cd /d "%~dp0"

echo ==============================================
echo  Starting Factory System VERSION 2...
echo ==============================================

echo [1/4] Starting V2 Sensor Server...
start /min "v2_Sensor" python temp_sensor_server.py

timeout /t 1 /nobreak > nul

echo [2/4] Starting V2 Live Monitor (1s)...
start "v2_Monitor" python temp_monitor_gui.py

timeout /t 1 /nobreak > nul

echo [3/4] Starting V2 Data Accumulator (10m)...
start "v2_Accumulator" python v2_accumulator.py

timeout /t 1 /nobreak > nul

echo [4/4] Starting V2 Excel Logger (Watcher)...
start "v2_Excel_Logger" python v2_excel_logger.py

echo.
echo Version 2 System is now ACTIVE.
echo Data will be logged to 'sensor_history.xlsx' via CSV files.
echo.
pause
