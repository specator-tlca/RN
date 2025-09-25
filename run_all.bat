@echo off
chcp 65001 > nul
echo ====================================
echo RH Project - Run All Verifications
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

REM Run all scripts
echo.
echo Running all verification scripts...
python run_all.py

REM Show results
echo.
echo ====================================
echo Showing results summary...
echo ====================================
python view_results.py

echo.
echo ====================================
echo Completed! Check logs\ for details
echo ====================================
pause
