@echo off
chcp 65001 > nul
echo =========================================
echo  도면 정보 추출기 실행을 준비 중입니다...
echo =========================================
cd /d "%~dp0"
python drawing_extractor.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 프로그램 실행 중 오류가 발생했습니다.
    echo ❌ 위 에러 메시지를 확인해주세요.
    pause
)
