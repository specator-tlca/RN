@echo off
chcp 65001 > nul
echo ====================================
echo RH Project - View Latest Results
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

REM View results
python view_results.py

echo.
pause
