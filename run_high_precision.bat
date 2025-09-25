@echo off
chcp 65001 > nul
echo ====================================
echo RH Project - High Precision Run
echo ====================================
echo.
echo WARNING: This may take several minutes!
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

choice /C YN /M "Run high precision computation? This will take time"
if errorlevel 2 exit /b 0

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run high precision test
echo.
echo Running high precision test...
python run_precision_test.py high

echo.
echo ====================================
echo High precision run completed!
echo ====================================
pause
