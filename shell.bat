@echo off
chcp 65001 > nul
echo ====================================
echo RH Project - Interactive Shell
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
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo You are now in the RH project environment
echo.
echo Examples:
echo   python src\compute_C_right.py --P 100000
echo   python src\measure_Cthin_star.py
echo   python view_results.py
echo.
echo Type 'exit' to leave
echo.

cmd /k
