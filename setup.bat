@echo off
echo ====================================
echo RH Project - Initial Setup
echo ====================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH!
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment
if exist .venv (
    echo Virtual environment already exists
    choice /C YN /M "Do you want to recreate it"
    if errorlevel 2 goto SkipVenv
    echo Removing old environment...
    rmdir /s /q .venv
)

echo Creating virtual environment...
python -m venv .venv

:SkipVenv
REM Activate environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing requirements...
pip install -r requirements.txt

REM Create directories
echo.
echo Creating directories...
if not exist data mkdir data
if not exist logs mkdir logs

REM Show installed packages
echo.
echo ====================================
echo Installed packages:
echo ====================================
pip list

echo.
echo ====================================
echo Setup completed successfully!
echo ====================================
echo.
echo To run verifications, use: run_all.bat
echo To run quick test, use: run_quick.bat
echo.
pause
