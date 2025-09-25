@echo off
chcp 65001 > nul
echo ====================================
echo RH Project - Quick Test
echo ====================================
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run quick precision test
echo Running quick precision test...
python run_precision_test.py quick

echo.
echo ====================================
echo Quick test completed!
echo ====================================
pause
