@echo off
echo ====================================
echo RH Project - Clean Data and Logs
echo ====================================
echo.

echo This will delete all files in:
echo   - data\
echo   - logs\
echo.

choice /C YN /M "Are you sure"
if errorlevel 2 exit /b 0

echo.
echo Cleaning data directory...
if exist data\*.* del /q data\*.*

echo Cleaning logs directory...
if exist logs\*.* del /q logs\*.*

echo.
echo ====================================
echo Cleanup completed!
echo ====================================
pause
