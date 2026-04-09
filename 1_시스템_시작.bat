@echo off
title Factory_System_Launcher
cd /d "%~dp0"

echo ==============================================
echo  Starting Factory Temperature System...
echo ==============================================

echo [1/3] Starting Sensor Server (Role 1)...
start /min "Factory_Server" python factory_sensor.py

timeout /t 2 /nobreak > nul

echo [2/3] Starting Data Logger (Role 2)...
start /min "Factory_Logger" python factory_logger.py

timeout /t 2 /nobreak > nul

echo [3/3] Starting Manager Dashboard (Role 3 and 4)...
python factory_manager_ui.py

echo.
echo System terminated.
pause
