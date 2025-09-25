@echo off
chcp 65001 > nul
:MENU
cls
echo ============================================
echo       RH Project - Main Menu
echo ============================================
echo.
echo 1. Initial Setup (run first time)
echo 2. Run All Verifications (standard)
echo 3. Run Quick Test
echo 4. Run High Precision Test
echo 5. View Latest Results
echo 6. Open Interactive Shell
echo 7. Clean Data and Logs
echo 8. Exit
echo.
set /p choice=Enter your choice (1-8): 

if "%choice%"=="1" goto SETUP
if "%choice%"=="2" goto RUNALL
if "%choice%"=="3" goto QUICK
if "%choice%"=="4" goto HIGH
if "%choice%"=="5" goto VIEW
if "%choice%"=="6" goto SHELL
if "%choice%"=="7" goto CLEAN
if "%choice%"=="8" goto EXIT

echo Invalid choice! Please try again.
pause
goto MENU

:SETUP
call setup.bat
pause
goto MENU

:RUNALL
call run_all.bat
pause
goto MENU

:QUICK
call run_quick.bat
pause
goto MENU

:HIGH
call run_high_precision.bat
pause
goto MENU

:VIEW
call view_results.bat
pause
goto MENU

:SHELL
call shell.bat
goto MENU

:CLEAN
call clean.bat
pause
goto MENU

:EXIT
echo Goodbye!
exit /b 0
